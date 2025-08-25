import numpy as np
from collections import deque

class Graph():
    def __init__(self, embeddings: np.ndarray, ids):
        self.idToInt = {}
        self.intToId = []
        self.embeddings = embeddings
        self.adj = [dict() for _ in range(len(embeddings))]
        self.thresh = 0.80
        self.ids = ids
        self.idToCluster= {}
        self.length = len(embeddings)

        for i in ids:
            self.intToId.append(i)
            self.idToInt[i] = len(self.intToId)-1 

    def compute_edges(self):
        """ given an embedding arr compute adj graph based on threshhold val """
        cos = self.embeddings @ self.embeddings.T
        for i in range(self.length):
            row = cos[i] # arr of similiarty (cosine) scrs with the other articles
            for j in range(i+1, self.length):
                val = float(row[j]) # cosine value between i & j articles
                # if value > thresh then form an edge 
                # and record edge in adj from both POVs
                if val >= self.thresh:
                    self.adj[i][j] = val
                    self.adj[j][i] = val
    
    def cluster(self):
        """ assign each id to a cluster based on connected edges from adj matrix """
        visited = set()
        q = deque()
        cluster = 0

        # run until every id is assigned to a cluster
        for x in self.ids:
            if x in visited(): # id is processed and assigned a cluster so skip
                continue

            cluster += 1
            q.append(x)

            # find all ids for current cluster using BFS
            while q:
                curr = q.popleft()
                if curr in visited:
                    continue

                visited.add(curr)
                i = self.idToInt(curr)

                # if adj[i][j] is not 0.0 then j is child of i, we add to q for BFS
                for j in range(self.length):
                    if self.adj[i].get(j, 0.0) != 0.0:
                        q.append(self.intToId(j))

                # assign to current cluster since its connected
                self.idToCluster[curr] = f"c({cluster})"


