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
        self._cluster_ids = defaultdict(lambda: {"articles": [], "sentences": [], "meta": {},"pairs": []}) # list of article for each cluster and the cluster's similarity matrix
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
                "sentences": data["sentences"],
                "meta": data["meta"]
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
                site = "bbc"
            elif "aljazeera.com" in url:
                site = "aljazeera"
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
                "article_keywords": json.dumps(self._article_keywords[url])
            }
            append_to_json_array(p, obj)
    
    def compute_inferences(self):
        """ generate pairs of sentences across articles that have similar meaning for each cluster and also generate keywords for every article """
        
        STOPWORDS = set(["the", "this", "that", "it", "they", "he", "she", "we", "you", "i", "a", "an"])
        FACT_ENTS = {"PERSON","ORG","GPE","LOC","NORP","EVENT","WORK_OF_ART","PRODUCT"}
        
        def clean_phrase(p):
            p = p.strip().lower()
            p = re.sub(r"[\s\n]+", " ", p)
            return p
        
        def good_phrase(p):
            words = p.split()
            if len(words) < 1 or len(words) > 6:
                return False
            if all(w in STOPWORDS for w in words):
                return False
            return True
        
        def norm_ent(t: str) -> str:
            return re.sub(r"\s+", " ", t.strip().lower())
        
        def facty(i, j):
            if ents_set[i] and ents_set[j] and (ents_set[i] & ents_set[j]):
                return True
            if num_set[i] and num_set[j] and (num_set[i] & num_set[j]):
                return True
            return False
        
        def is_facty_chunk(chunk):
            # requires parser, which you have
            has_propn = any(t.pos_ == "PROPN" for t in chunk)
            has_num = any(t.like_num for t in chunk)
            long_enough = len(chunk.text.split()) >= 2
            return long_enough and (has_propn or has_num)

        def fact_bonus(phrase: str) -> float:
            bonus = 0.0
            if re.search(r"\b\d", phrase):
                bonus += 0.05
            if len(phrase.split()) >= 2:
                bonus += 0.02
            return bonus
    
        for cluster in self._cluster_ids.values():
            cluster_sentence_meta = [] # maps sentence index to article url for cross article recognition

            ents_set = []
            num_set = []

            all_sentences = []
            spans = {}
            # breaking up the logic into multiple for loops so that embeddings can happen all at once rather than per url for performance
            for url in cluster["articles"]:
                # generate embeddings of sentences from articles within same cluster only for pairwise similarity
                # also generate keywords for articles within the same loop
                res = split_into_sentences(self._id_to_data[url]["content"])

                docs = list(nlp.pipe(res, batch_size=128))
                
                article_sentences = []
                article_ents = []
                article_nums = []
                
                for s, d in zip(res, docs):
                    if len(d) >= 7 and len(d.ents) >= 2:
                        article_sentences.append(s)

                        ents = {
                            norm_ent(e.text)
                            for e in d.ents
                            if e.label_ in ("PERSON","ORG","GPE","LOC","NORP","EVENT","PRODUCT")
                        }
                        article_ents.append(ents)

                        nums = set(re.findall(r"\b\d+(?:[\.,]\d+)?\b", d.text))
                        article_nums.append(nums)

                # extend cluster-global arrays in the SAME order
                start = len(all_sentences)
                all_sentences.extend(article_sentences)
                end = len(all_sentences)
                spans[url] = (start, end)

                cluster_sentence_meta.extend([url] * len(article_sentences))
                ents_set.extend(article_ents)
                num_set.extend(article_nums)
            
            all_embeddings = self._model.encode(all_sentences, normalize_embeddings=True, batch_size=64, show_progress_bar=False)
            all_embeddings = all_embeddings.astype(np.float32)

            all_top_sentences = []
            top_sentences_span = {}
            for url in cluster["articles"]:
                start, end = spans[url]
                # sentences and embeddings for just this article
                article_sentences = all_sentences[start:end] 
                sentence_embeddings = all_embeddings[start:end]     

                # similarity of sentence embedding to article embedding
                article_embedding_vector = np.atleast_2d(self._article_embedding[url])
                significance_scores = (article_embedding_vector @ sentence_embeddings.T)[0]

                if len(article_sentences) == 0:
                    top_sentences_span[url] = (len(all_top_sentences), len(all_top_sentences))
                    continue

                top_k = min(5,len(article_sentences))
                top_sentence_inidices = np.argpartition(significance_scores, -top_k)[-top_k:]
                top_sentences = [article_sentences[i] for i in top_sentence_inidices]

                top_sentences_start = len(all_top_sentences)
                all_top_sentences.extend(top_sentences)
                top_sentences_end = len(all_top_sentences)
                top_sentences_span[url] = (top_sentences_start, top_sentences_end)

            all_top_docs = list(nlp.pipe(all_top_sentences, batch_size=128))
            all_candidates = []
            candidates_map = {} # map each url to a list of candidates

            
            for url in cluster["articles"]:
                # find candidates for keywords for each article and fallbacks
                candidates = set()
                start, end = top_sentences_span[url]
                top_docs = all_top_docs[start:end]
                top_sentences = all_top_sentences[start:end]

                for doc in top_docs:
                    for chunk in doc.noun_chunks:
                        if is_facty_chunk(chunk):
                            phrase = clean_phrase(chunk.text)
                            if good_phrase(phrase):
                                candidates.add(phrase)
                    for ent in doc.ents:
                        if ent.label_ in FACT_ENTS:
                            phrase = clean_phrase(ent.text)
                            if good_phrase(phrase):
                                candidates.add(phrase)
                    for tok in doc:
                        if tok.like_num:
                            # take a small window around the number
                            left = doc[max(tok.i-2, 0):tok.i]
                            right = doc[tok.i+1:min(tok.i+3, len(doc))]
                            phrase = clean_phrase(left.text + " " + tok.text + " " + right.text)
                            if good_phrase(phrase):
                                candidates.add(phrase)

                if len(candidates) < 3:
                    for doc in top_docs:
                        for ent in doc.ents:
                            phrase = clean_phrase(ent.text)
                            if good_phrase(phrase):
                                candidates.add(phrase)
                if not candidates:
                    for s in top_sentences:
                        for w in s.split():
                            w = clean_phrase(w)
                            if good_phrase(w) and len(w) > 3:
                                candidates.add(w)
                # remove potential keywords that were just a number
                candidates = [c for c in candidates if not c.isnumeric()]
                candidates_map[url] = candidates
                all_candidates.extend(candidates)
                 
            cluster_sentences = all_sentences
            cluster_embeddings = all_embeddings
            similarity_matrix = cluster_embeddings @ cluster_embeddings.T

            unique_candidates = list(dict.fromkeys(all_candidates))
            all_candidate_embeddings = self._model.encode(unique_candidates, normalize_embeddings=True, batch_size=128, show_progress_bar=False).astype(np.float32)
            candidate_index = {c: i for i, c in enumerate(unique_candidates)}

            for url in cluster["articles"]:
                candidates = candidates_map[url]
                if not candidates:
                    self._article_keywords[url] = []
                    continue
                idx = np.fromiter((candidate_index[c] for c in candidates), dtype=np.int32)
                candidate_embeddings = all_candidate_embeddings[idx]
                article_embedding_vector = np.atleast_2d(self._article_embedding[url])
                keyword_scores = (article_embedding_vector @ candidate_embeddings.T)[0]
                # choose top 10 keywords that resembles the articles the most via their embedding scores
                ranked_scores = sorted(((c, float(s) + fact_bonus(c)) for c, s in zip(candidates, keyword_scores)), key = lambda x: x[1], reverse=True)
                self._article_keywords[url] = [keyword for keyword, _ in ranked_scores[:10]]
            # collect data for cluster data structure
            pairs = []
            for i in range(len(cluster_sentences)):
                url_i = cluster_sentence_meta[i]
                for j in range(i+1, len(cluster_sentences)):
                    url_j = cluster_sentence_meta[j]
                    score = similarity_matrix[i][j]
                    if url_i != url_j and score > 0.60 and facty(i, j):
                        pairs.append((i,j, score))
            
            cluster["sentences"] = cluster_sentences
            cluster["meta"] = cluster_sentence_meta
            # store pairs for later use in frontend
            for i,j, score in pairs:
                cluster["pairs"].append({
                    "source": cluster_sentences[i],
                    "source_url": cluster_sentence_meta[i],
                    "match": cluster_sentences[j],
                    "match_url": cluster_sentence_meta[j],
                    "score": float(score)
                })