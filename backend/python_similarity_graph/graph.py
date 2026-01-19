import numpy as np
from collections import deque, defaultdict
import spacy
import pathlib
import json
import os
from utils import split_into_sentences, append_to_json_array
from sentence_transformers import SentenceTransformer
import re

nlp = spacy.load("en_core_web_sm")
nlp.disable_pipe("lemmatizer")
nlp.disable_pipe("attribute_ruler")
nlp.disable_pipe("senter")


class Graph():
    def __init__(self, articles, thresh):
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        urls = [a["url"] for a in articles]
        contents = [a["content"] for a in articles]
        embeddings = self._model.encode(contents, normalize_embeddings=True).astype(np.float32)
        self._embeddings = embeddings
        self._article_embedding = dict(zip(urls, embeddings))
        self._length = len(embeddings)
        self._adj = [dict() for _ in range(len(embeddings))]
        self._id_to_int = {}
        self._int_to_id = []
        self._thresh = thresh
        self._id_to_data = {} # article url to article mapping
        self._ids = [a["url"] for a in articles]
        self._id_to_cluster= {} # article ID to cluster mapping
        self._cluster_ids = defaultdict(lambda: {"articles": [],"pairs": []}) # list of article for each cluster and the cluster's similarity matrix
        self._article_keywords = {}

        for a in articles:
            self._id_to_data[a["url"]] = a

        for i in self._ids:
            self._int_to_id.append(i)
            self._id_to_int[f"{i}"] = len(self._int_to_id)-1 

    def compute_edges(self):
        """ given an embedding arr compute adj graph based on threshhold val """
        cos = self._embeddings @ self._embeddings.T
        for i in range(self._length):
            row = cos[i] # arr of similiarty (cosine) scrs with the other articles
            for j in range(i+1, self._length):
                val = float(row[j]) # cosine value between i & j articles
                # if value > thresh then form an edge 
                # and record edge in adj from both POVs
                if val >= self._thresh:
                    self._adj[i][j] = val
                    self._adj[j][i] = val
    
    def cluster(self):
        """ assign each id to a cluster based on connected edges from adj matrix """
        visited = set()
        q = deque()
        cluster = 0

        # run until every id is assigned to a cluster
        for x in self._ids:
            if x in visited: # id is processed and assigned a cluster so skip
                continue

            cluster += 1
            cid = f"c{cluster}"
            visited.add(x)
            q.append(x)

            # find all ids for current cluster using BFS
            while q:
                curr = q.popleft()
                i = self._id_to_int[curr]

                for j in self._adj[i].keys():
                    neighbor = self._int_to_id[j]
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
                        
                # assign to current cluster since its connected
                self._id_to_cluster[curr] = cid

        for key, val in self._id_to_cluster.items():
            self._cluster_ids[val]["articles"].append(key)
        
        self.compute_inferences()
        self.store_graph()
        self.store_clusters()

    def store_clusters(self):
        """ write cluster dictionary to a field in json format for debugging """
        
        base_dir = pathlib.Path(__file__).resolve().parent
        pair_path = pathlib.Path(os.path.join(base_dir,"data","pairs.json"))
        clusters_path = pathlib.Path(os.path.join(base_dir, "data","clusters.json"))
        
        # delete old file and make file to populate new data
        if pair_path.exists(): os.remove(pair_path) 
        if clusters_path.exists(): os.remove(clusters_path)

        for id, data in self._cluster_ids.items():
            cluster_obj = {
                "cluster_id": id,
                "articles": data["articles"],
            }
            append_to_json_array(clusters_path,cluster_obj)

        count = 0
        for id, data in self._cluster_ids.items():
            for p in data["pairs"]:
                pair_obj = {
                    "id": count,
                    "cluster_id": id,
                    "source_sentence": p["source"],
                    "source_url": p["source_url"],
                    "match_sentence": p["match"],
                    "match_url": p["match_url"],
                    "score": p["score"]
                }
                append_to_json_array(pair_path,pair_obj)
                count += 1
    
    def store_graph(self):
        """ format collected and computed data of each article store in JSON file """
        
        base_dir = pathlib.Path(__file__).resolve().parent
        p = pathlib.Path(os.path.join(base_dir, "data","articles.json"))
        
        # delete old file and make file to populate new data
        if p.exists():
            os.remove(p)

        for id in self._ids:
            data = self._id_to_data[id]
            url = data["url"]
            site = ""
            if "bbc.co" in url:
                site = "BBC"
            elif "aljazeera.com" in url:
                site = "Al Jazeera"
            elif "dw.com" in url:
                site = "Deutsche Welle"
            elif "npr.org" in url:
                site = "NPR"
            elif "pbs.org" in url:
                site = "PBS"
            else:
                site = "APNews"

            obj = {
                "id": self._id_to_int[url],
                "url": url,
                "site": site,
                "title": data["title"],
                "article": data["content"],
                "images": json.dumps(data["images"]),
                "labels": data["labels"],
                "score": data["score"],
                "cluster_id": self._id_to_cluster[id],
                "article_keywords": self._article_keywords[url]
            }
            append_to_json_array(p, obj)
    
    def compute_inferences(self):
        """ generate pairs of sentences across articles that have similar meaning for each cluster and also generate keywords for every article """
        
        STOPWORDS = set(["the", "this", "that", "it", "they", "he", "she", "we", "you", "i", "a", "an"])
        FACT_ENTS = {"PERSON","ORG","GPE","LOC","NORP","EVENT","WORK_OF_ART","PRODUCT"}
        
        def normalize_text(s: str) -> str:
            return " ".join(s.lower().split())
        def good_phrase(p):
            words = p.split()
            if len(words) < 1 or len(words) > 6:
                return False
            if all(w in STOPWORDS for w in words):
                return False
            return True
        def facty(i, j):
            if entities_set[i] and entities_set[j] and (entities_set[i] & entities_set[j]):
                return True
            if numbers_set[i] and numbers_set[j] and (numbers_set[i] & numbers_set[j]):
                return True
            return False
        # check phrases for proper nouns for keyword candidates
        def is_facty_chunk(chunk):
            has_propn = any(token.pos_ == "PROPN" for token in chunk)
            long_enough = len(chunk.text.split()) >= 2
            return long_enough and has_propn
        def fact_bonus(phrase: str) -> float:
            bonus = 0.0
            if re.search(r"\b\d", phrase):
                bonus += 0.05
            if len(phrase.split()) >= 2:
                bonus += 0.02
            return bonus
    
        for cluster in self._cluster_ids.values():
            candidate_sentences = []
            cluster_sentence_meta = [] # maps candidate_sentence index to article url for cross article recognition
            # global list of entities and numbers per sentence in order of candidate_sentences for sentence matching
            entities_set = [] 
            numbers_set = []
            sentence_spans = {}

            # breaking up logic into multiple for loops to enable batch mbeddings for performance
            for url in cluster["articles"]:
                # first loop filters out good sentences, groups them by articles and sets up everything for later for loops
                article_sentences = split_into_sentences(self._id_to_data[url]["content"])
                good_sentences = []
                article_entities = []
                article_numbers = []
                
                for s, d in zip(article_sentences, nlp.pipe(article_sentences, batch_size=128)):
                    if len(d) >= 7 and len(d.ents) >= 2:
                        good_sentences.append(s)
                        entities = {
                            normalize_text(e.text)
                            for e in d.ents
                            if e.label_ in ("PERSON","ORG","GPE","LOC","NORP","EVENT","PRODUCT")
                        }
                        article_entities.append(entities)
                        nums = set(re.findall(r"\b\d+(?:[\.,]\d+)?\b", d.text))
                        article_numbers.append(nums)

                # extend cluster-global arrays in the SAME order
                start = len(candidate_sentences)
                candidate_sentences.extend(good_sentences) # we only want to embed sentences that might be meaningful
                end = len(candidate_sentences)
                sentence_spans[url] = (start, end)

                cluster_sentence_meta.extend([url] * len(good_sentences))
                entities_set.extend(article_entities)
                numbers_set.extend(article_numbers)
            
            all_embeddings = self._model.encode(candidate_sentences, normalize_embeddings=True, batch_size=64, show_progress_bar=False).astype(np.float32)
            all_top_sentences = []
            top_sentences_span = {}

            for url in cluster["articles"]:
                # second loop finds representative sentences per article for later keyword extraction and cross article similarities
                start, end = sentence_spans[url]
                article_sentences = candidate_sentences[start:end] 
                article_sentence_embeddings = all_embeddings[start:end]     

                article_embedding_vector = np.atleast_2d(self._article_embedding[url])
                significance_scores = (article_embedding_vector @ article_sentence_embeddings.T)[0] # significance of sentence to article 

                # insert dummy values so code doesn't break for empty articles
                if len(article_sentences) == 0:
                    top_sentences_span[url] = (len(all_top_sentences), len(all_top_sentences))
                    continue

                top_k = min(5,len(article_sentences))
                top_sentence_indices = np.argpartition(significance_scores, -top_k)[-top_k:]
                top_sentences = [article_sentences[i] for i in top_sentence_indices]

                top_sentences_start = len(all_top_sentences)
                all_top_sentences.extend(top_sentences)
                top_sentences_end = len(all_top_sentences)
                top_sentences_span[url] = (top_sentences_start, top_sentences_end)

            all_top_docs = list(nlp.pipe(all_top_sentences, batch_size=128))
            all_candidates = []
            candidates_map = {} # map each url to a list of candidates

            for url in cluster["articles"]:
                # find, collect and map candidates for keywords for each article
                candidates = set()
                start, end = top_sentences_span[url]
                top_docs = all_top_docs[start:end]
                top_sentences = all_top_sentences[start:end]

                for doc in top_docs:
                    for chunk in doc.noun_chunks:
                        if is_facty_chunk(chunk):
                            phrase = normalize_text(chunk.text)
                            if good_phrase(phrase):
                                candidates.add(phrase)
                    for entities in doc.ents:
                        if entities.label_ in FACT_ENTS:
                            phrase = normalize_text(entities.text)
                            if good_phrase(phrase):
                                candidates.add(phrase)

                # fall back candidate generation if above filters were too strict
                if not candidates or len(candidates) < 3:
                    for doc in top_docs:
                        for entitiy in doc.ents:
                            phrase = normalize_text(entitiy.text)
                            if good_phrase(phrase):
                                candidates.add(phrase)

                candidates = [c for c in candidates if not c.isnumeric()] # numbers by themselves have no meaning
                candidates_map[url] = candidates
                all_candidates.extend(candidates)
                 
            similarity_matrix = all_embeddings @ all_embeddings.T
            all_candidates = list(dict.fromkeys(all_candidates)) # create a unique list
            all_candidate_embeddings = self._model.encode(all_candidates, normalize_embeddings=True, batch_size=128, show_progress_bar=False).astype(np.float32)
            candidate_index = {c: i for i, c in enumerate(all_candidates)}

            for url in cluster["articles"]:
                candidates = candidates_map[url]
                if not candidates:
                    self._article_keywords[url] = []
                    continue
                idx = np.fromiter((candidate_index[c] for c in candidates), dtype=np.int32)
                candidate_embeddings = all_candidate_embeddings[idx]
                article_embedding_vector = np.atleast_2d(self._article_embedding[url])
                keyword_scores = (article_embedding_vector @ candidate_embeddings.T)[0]

                # favor keywords that are longer and have numbers to represent the article based on embedding scores
                ranked_scores = sorted(((c, float(s) + fact_bonus(c)) for c, s in zip(candidates, keyword_scores)), key = lambda x: x[1], reverse=True)
                self._article_keywords[url] = [keyword for keyword, _ in ranked_scores[:10]]

            # pairs of sentences with higher scores from different articles connect articles so find and keep them
            pairs = []
            for i in range(len(candidate_sentences)):
                url_i = cluster_sentence_meta[i]
                for j in range(i+1, len(candidate_sentences)):
                    url_j = cluster_sentence_meta[j]
                    score = similarity_matrix[i][j]
                    if url_i != url_j and score > 0.60 and facty(i, j):
                        pairs.append((i,j, score))
            
            # cluster["sentences"] = candidate_sentences
            # cluster["meta"] = cluster_sentence_meta
            # store pairs for later use in frontend
            for i,j, score in pairs:
                cluster["pairs"].append({
                    "source": candidate_sentences[i],
                    "source_url": cluster_sentence_meta[i],
                    "match": candidate_sentences[j],
                    "match_url": cluster_sentence_meta[j],
                    "score": float(score)
                })