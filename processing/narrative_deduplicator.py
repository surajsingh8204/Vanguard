from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN


class NarrativeDeduplicator:

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):

        print("Loading deduplication model...")

        self.model = SentenceTransformer(model_name)

    def _prepare_titles(self, articles):

        titles = []
        valid_articles = []

        for article in articles:

            # GDELT gives no title → use URL as proxy (temporary)
            text = article.get("url")

            if text:
                titles.append(text)
                valid_articles.append(article)

        return titles, valid_articles

    def _cluster(self, embeddings):

        clustering = DBSCAN(
            eps=0.35,
            min_samples=2,
            metric="cosine"
        ).fit(embeddings)

        return clustering.labels_

    def deduplicate(self, articles):

        titles, valid_articles = self._prepare_titles(articles)

        if not titles:
            return []

        print("Generating embeddings...")

        embeddings = self.model.encode(titles)

        print("Clustering...")

        labels = self._cluster(embeddings)

        clusters = {}

        for i, label in enumerate(labels):

            if label == -1:
                continue

            clusters.setdefault(label, []).append(valid_articles[i])

        unique = []

        for cluster in clusters.values():

            # representative article
            unique.append(cluster[0])

        print("Reduced from", len(articles), "to", len(unique))

        return unique