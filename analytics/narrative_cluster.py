from sklearn.cluster import KMeans


class NarrativeCluster:

    def __init__(self, n_clusters=5):

        self.model = KMeans(n_clusters=n_clusters)

    def cluster(self, embeddings):

        labels = self.model.fit_predict(embeddings)

        return labels