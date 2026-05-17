import json
import os
from processing.narrative_deduplicator import NarrativeDeduplicator
from processing.article_extractor import ArticleExtractor
from utils.time_utils import TimeUtils


class ContentPipeline:

    def __init__(self):

        self.deduplicator = NarrativeDeduplicator()
        self.extractor = ArticleExtractor(max_workers=10)

    def load_articles(self):

        articles = []

        for root, _, files in os.walk("data_lake/raw"):

            for file in files:

                if file.endswith(".json"):

                    with open(os.path.join(root, file)) as f:
                        articles.extend(json.load(f))

        return articles

    def run(self):

        print("Loading articles...")

        articles = self.load_articles()

        for article in articles:
            raw_time = article.get("date")
            article["formatted_date"] = TimeUtils.format_gdelt_time(raw_time)

        print("Total articles:", len(articles))

        print("Running deduplication...")

        unique = self.deduplicator.deduplicate(articles)

        print("Unique narratives:", len(unique))

        print("Extracting content...")

        enriched = self.extractor.extract_batch(unique)

        os.makedirs("data_lake/processed", exist_ok=True)

        with open("data_lake/processed/enriched_articles.json", "w") as f:
            json.dump(enriched, f, indent=2)

        print("Final enriched:", len(enriched))

        return enriched
    
if __name__ == "__main__":

    pipeline = ContentPipeline()

    pipeline.run()