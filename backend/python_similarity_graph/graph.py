import numpy as np
from collections import deque, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
import spacy
import pathlib
import json
import os
from sklearn.metrics.pairwise import cosine_similarity
from utils import add_to_json_file
import sqlite3

nlp = spacy.load("en_core_web_sm")

def noun_filter(text):
    filtered = []
    for doc in nlp.pipe(text, disable=["ner", "parser"]):
        tokens = [t.lemma_ for t in doc if t.pos_ in {"NOUN","PROPN"}]
        filtered.append(" ".join(tokens))
    return filtered

class Graph():
    def __init__(self, embeddings: np.ndarray, articles, thresh):
        self._idToInt = {}
        self._intToId = []
        self._adj = [dict() for _ in range(len(embeddings))]
        self._thresh = thresh
        self._idToData = {} # article url to article mapping
        self._ids = [a["url"] for a in articles]
        self._idToCluster= {} # article ID to cluster mapping
        self._clusterIds = defaultdict(lambda: {"articles": [], "common": []}) # list of article for each cluster
        self._length = len(embeddings)
        self._clusterKeywords = {}
        emb = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True)+1e-9)
        self._embeddings = emb.astype(np.float32)

        for a in articles:
            self._idToData[a["url"]] = a

        for i in self._ids:
            self._intToId.append(i)
            self._idToInt[f"{i}"] = len(self._intToId)-1 

    @property
    def idToCluster(self):
        return self._idToCluster

    @property
    def clusterKeywords(self):
        return self._clusterKeywords

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
        topk = 6

        # run until every id is assigned to a cluster
        for x in self._ids:
            if x in visited: # id is processed and assigned a cluster so skip
                continue

            text = []
            cluster += 1
            cid = f"c{cluster}"
            visited.add(x)
            q.append(x)

            # find all ids for current cluster using BFS
            while q:
                curr = q.popleft()
                i = self._idToInt[curr]

                for j in self._adj[i].keys():
                    neighbor = self._intToId[j]
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
                        
                # assign to current cluster since its connected
                self._idToCluster[curr] = cid
                # append article text to text for cluster keywords
                text.append(self._idToData[curr]["content"])

            min_df_val = 1 if len(text) <= 3 else 2
            max_df_val = 1.0 if len(text) <= 3 else 0.7
            tf = TfidfVectorizer( 
                stop_words = "english",
                ngram_range = (2,3),
                min_df = min_df_val,
                max_df = max_df_val,
                sublinear_tf = True,
                norm = None
            )

            X = tf.fit_transform(text)

            if X.shape[1] == 0:
                # no keywords detected
                self._clusterKeywords[cid] = ""
            else:
                scores = X.mean(axis=0).A1
                top_idx = scores.argsort()[-topk:][::-1]
                keywords = tf.get_feature_names_out()
                self._clusterKeywords[cid] = ",".join(keywords[top_idx])

        for key, val in self.idToCluster.items():
            self._clusterIds[val]["articles"].append(key)
        
        self.keyword_cleanup()
        self.store_graph()
        

    def write_cluster(self, path):
        """ write cluster dictionary to a field in json format for debugging """
        p = pathlib.Path(path)
        with open(p,'w') as f:
            json.dump(self._clusterIds,f, indent=4)
        f.close()

    def keyword_cleanup(self):
        """ clean keyword list for each cluster """
        
        unwanted = {'associated press', 'al jazeera', 'copyright 2025',
                    "said", "say", "also", "would", "could", "might", 
                    "according", "among", "within", "around", "between", 
                    "said", 'copyright', 'aljazeera',''}


        for cid, cluster in list(self._clusterKeywords.items()):
            #remove non nouns and pronouns
            cluster = noun_filter(cluster.split(","))
            #filter unwanted phrases
            cluster = set(filter(lambda x: x not in unwanted, cluster))
            self._clusterKeywords[cid] = cluster
    
    def store_graph(self):
        """ format collected and computed data of each article and add to the database.json file """
        
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        batch_rows = []
        sql = "INSERT INTO articles (url, site, title, text, images, labels, score, cluster_id, cluster_keywords) VALUES (?,?,?,?,?,?,?,?,?)"

        for id in self._ids:
            data = self._idToData[id]
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

            cluster_id = self._idToCluster[id]

            batch_rows.append((
                url,
                site,
                data["title"],
                data["content"],
                json.dumps(data["images"]),
                data["labels"],
                data["score"],
                cluster_id,
                ",".join(self._clusterKeywords[cluster_id])
            ))

        cursor.executemany(sql, batch_rows)
        conn.commit()
        conn.close()
    
    # def compute_cluster_sentences(self):
    #     for cluster in self._clusterIds:
    #         for url in cluster["articles"]:
