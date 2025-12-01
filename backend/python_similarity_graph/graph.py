import numpy as np
from collections import deque, defaultdict
import spacy
from spacy.tokens import Span
import pathlib
import json
import os
import sqlite3
from utils import split_into_sentences
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
        embeddings = self._model.encode(contents, normalize_embeddings=True)
        self._article_embedding = dict(zip(urls, embeddings))
        emb = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True)+1e-9)
        self._embeddings = emb.astype(np.float32)
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

        p = pathlib.Path(os.path.join("data","clusters.json"))
        with open(p,'w') as f:
            json.dump(self._cluster_ids,f, indent=4)
        f.close()

        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        batch_rows = []
        sql = "INSERT INTO clusters (cluster_id, articles, sentences, meta) VALUES (?,?,?,?)"

        for id, data in self._cluster_ids.items():
            # batch add to database for performance
            batch_rows.append((
                id,
                json.dumps(data["articles"]),
                json.dumps(data["sentences"]),
                json.dumps(data["meta"]),
            ))
        cursor.executemany(sql, batch_rows)

        batch_rows = []
        sql = "INSERT INTO pairs (cluster_id, source_sentence, source_url, match_sentence, match_url, score) VALUES (?,?,?,?,?,?)"

        for id, data in self._cluster_ids.items():
            for p in data["pairs"]:
                # batch add to database for performance
                batch_rows.append((
                    id,
                    p["source"],
                    p["source_url"],
                    p["match"],
                    p["match_url"],
                    p["score"]
                ))
        cursor.executemany(sql, batch_rows)

        conn.commit()
        conn.close()

    
    def store_graph(self):
        """ format collected and computed data of each article and add to the database.db file """

        # json output for debugging purposes
        p = pathlib.Path(os.path.join("data","articles.json"))
        with open(p,'w') as f:
            json.dump(self._id_to_data,f, indent=4)
        f.close()
        
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        batch_rows = []
        sql = "INSERT INTO articles (url, site, title, text, images, labels, score, cluster_id, article_keywords) VALUES (?,?,?,?,?,?,?,?,?)"

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

            cluster_id = self._id_to_cluster[id]

            # batch add to database for performance
            batch_rows.append((
                url,
                site,
                data["title"],
                data["content"],
                json.dumps(data["images"]),
                data["labels"],
                data["score"],
                cluster_id,
                json.dumps(self._article_keywords[url])
            ))

        cursor.executemany(sql, batch_rows)
        conn.commit()
        conn.close()
    
    def compute_inferences(self):
        """ generate pairs of sentences across articles that have similar meaning for each cluster and also generate keywords for every article """
        
        STOPWORDS = set(["the", "this", "that", "it", "they", "he", "she", "we", "you", "i", "a", "an"])
        spacy_cache = {}
        def get_doc(s):
            if s not in spacy_cache:
                spacy_cache[s] = nlp(s)
            return spacy_cache[s]
        
        def entities(sentence):
            doc = get_doc(sentence)
            return len(doc.ents)
        
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
                
    
        for cluster in self._cluster_ids.values():
            cluster_sentences = []  # list of sentences for cluster
            cluster_embeddings = [] # list of embeddings for all sentences for all articles in cluster
            cluster_sentence_meta = {} # maps sentence index to article url for cross article recognition

            for url in cluster["articles"]:
                # generate embeddings of sentences from articles within same cluster only for pairwise similarity
                # also generate keywords for articles within the same loop
                text = self._id_to_data[url]["content"]
                res =  split_into_sentences(text)

                article_sentences = [s for s in res if len(s.split()) >= 7 and entities(s) >= 2]
                sentence_embeddings = self._model.encode(article_sentences,normalize_embeddings=True)

                # similarity of sentence embedding to article embedding
                article_embedding_vector = np.atleast_2d(self._article_embedding[url])
                significance_scores = (article_embedding_vector @ sentence_embeddings.T)[0]

                top_k = min(5,len(article_sentences))
                top_sentence_inidices = np.argsort(significance_scores)[-top_k:]
                top_sentences = [article_sentences[i] for i in top_sentence_inidices]

                # find candidates for keywords for each article and fallbacks
                candidates = set()
                for s in top_sentences:
                    doc = get_doc(s)
                    for chunk in doc.noun_chunks:
                        phrase = clean_phrase(chunk.text)
                        if good_phrase(phrase):
                            candidates.add(phrase)
                if len(candidates) < 3:
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
                candidate_embeddings = self._model.encode(candidates, normalize_embeddings=True)
                keyword_scores = (article_embedding_vector @ candidate_embeddings.T)[0]
                # choose top 10 keywords that resembles the articles the most via their embedding scores
                ranked_scores = sorted(zip(candidates, keyword_scores), key = lambda x: x[1], reverse=True)
                self._article_keywords[url] = [keyword for keyword, _ in ranked_scores[:10]]
                
                start = len(cluster_sentences)
                cluster_sentences.extend(article_sentences)
                cluster_embeddings.extend(sentence_embeddings)
                for i in range(len(article_sentences)):
                    cluster_sentence_meta[start + i] = url

            
            cluster_embeddings = np.array(cluster_embeddings)
            similarity_matrix = cluster_embeddings @ cluster_embeddings.T

            # collect data for cluster data structure
            pairs = []
            for i in range(len(cluster_sentences)):
                url_i = cluster_sentence_meta[i]
                for j in range(len(cluster_sentences)):
                    if i == j:
                        continue
                    url_j = cluster_sentence_meta[j]
                    score = similarity_matrix[i][j]
                    if url_i != url_j and score > 0.60:
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