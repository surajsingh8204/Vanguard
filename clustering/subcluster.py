import hdbscan
import numpy as np


class SubClusterer:

    def __init__(self, min_cluster_size=3):

        self.model = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=2,
            metric='euclidean'
        )

    def cluster(self, embeddings):

        embeddings = np.array(embeddings)

        labels = self.model.fit_predict(embeddings)

        return labels