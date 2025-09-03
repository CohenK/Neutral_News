import numpy as np
from collections import deque
from sklearn.feature_extraction.text import TfidfVectorizer

class Graph():
    def __init__(self, embeddings: np.ndarray, articles, thresh):
        self._idToInt = {}
        self._intToId = []
        self._embeddings = embeddings
        self._adj = [dict() for _ in range(len(embeddings))]
        self._thresh = thresh
        self._idToData = {}
        self._ids = [a.url for a in articles]
        self._idToCluster= {}
        self._length = len(embeddings)
        self._clusterKeywords = {}

        for a in articles:
            self._idToData[a.url] = a

        for i in self.ids:
            self._intToId.append(i)
            self._idToInt[f"{i}"] = len(self._intToId)-1 

    @property
    def idToCluster(self):
        return self._idToCluster

    @property
    def adj(self):
        return self.adj
    
    @property
    def intToId(self):
        return self._intToId
    
    @property
    def idToInt(self):
        return self._idToInt

    @property
    def clusterKeywords(self):
        return self.cluster

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
                    self.adj[i][j] = val
                    self.adj[j][i] = val
    
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
                text.append(self._idToData[curr].content)

            min_df_val: int | float = 1 if len(text) == 1 else 2
            tf = TfidfVectorizer( 
                stop_words = "english",
                ngram_range = (1,2),
                min_df = min_df_val,
                max_df = 0.7,
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