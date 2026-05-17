import json
import os
from processing.narrative_deduplicator import NarrativeDeduplicator


def load_articles():

    articles = []

    for root, _, files in os.walk("data_lake/raw"):

        for file in files:

            if file.endswith(".json"):

                with open(os.path.join(root, file)) as f:
                    articles.extend(json.load(f))

    return articles


articles = load_articles()

print("Total articles:", len(articles))

deduplicator = NarrativeDeduplicator()

unique = deduplicator.deduplicate(articles)

print("Unique narratives:", len(unique))