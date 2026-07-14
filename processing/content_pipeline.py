import hashlib
import json
import logging
import os

from config.settings import ENRICHED_ARTICLES_PATH, RAW_ARTICLES_DIR
from processing.article_extractor import ArticleExtractor
from processing.data_quality_firewall import DataQualityFirewall
from processing.document_purifier import DocumentPurifier
from utils.time_utils import TimeUtils


logger = logging.getLogger(__name__)


class ContentPipeline:

    def __init__(self, raw_dir=RAW_ARTICLES_DIR, output_path=ENRICHED_ARTICLES_PATH):

        self.raw_dir = raw_dir
        self.output_path = output_path
        self.extractor = ArticleExtractor(max_workers=10)
        self.purifier = DocumentPurifier()
        self.firewall = DataQualityFirewall()
        self.existing_hashes = set()
        self.stats = {
            "feeds_processed": 0,
            "urls_discovered": 0,
            "duplicate_urls_removed": 0,
            "articles_extracted": 0,
            "extraction_failures": 0,
            "purifier_rejected": 0,
            "firewall_rejected": 0,
            "metadata_rejected": 0,
            "content_duplicates_removed": 0,
            "accepted_articles": 0,
        }

    def load_articles(self):

        articles = []
        json_files = []

        for root, _, files in os.walk(self.raw_dir):

            for file_name in files:

                if file_name.endswith(".json"):
                    json_files.append(os.path.join(root, file_name))

        self.stats["feeds_processed"] = len(json_files)

        for file_path in sorted(json_files):

            try:
                with open(file_path, "r", encoding="utf-8") as handle:
                    payload = json.load(handle)

                if isinstance(payload, list):
                    articles.extend(payload)

                elif isinstance(payload, dict):
                    articles.append(payload)

                else:
                    logger.warning("Skipping unexpected payload in %s", file_path)

            except (OSError, json.JSONDecodeError) as exc:
                logger.exception("Unable to load raw articles from %s: %s", file_path, exc)

        for article in articles:
            raw_time = article.get("formatted_date") or article.get("date")
            if raw_time and not article.get("formatted_date"):
                article["formatted_date"] = TimeUtils.format_gdelt_time(raw_time)

        self.stats["urls_discovered"] = len(articles)
        return articles

    def deduplicate(self, articles, stage="url"):

        if stage == "url":
            seen_urls = set()
            unique_articles = []

            for article in articles:
                url = article.get("url")
                if not url:
                    continue

                if url in seen_urls:
                    self.stats["duplicate_urls_removed"] += 1
                    continue

                seen_urls.add(url)
                unique_articles.append(article)

            return unique_articles

        if stage == "content":
            grouped = {}

            for article in articles:
                content = self._normalized_content(article.get("content", ""))
                if not content:
                    continue

                content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
                grouped.setdefault(content_hash, []).append(article)

            deduplicated = []

            for group in grouped.values():
                deduplicated.append(self._select_best_article(group))
                self.stats["content_duplicates_removed"] += max(len(group) - 1, 0)

            return deduplicated

        raise ValueError(f"Unsupported deduplication stage: {stage}")

    def extract_articles(self, articles):

        extracted = self.extractor.extract_batch(articles)
        self.stats["articles_extracted"] = len(extracted)
        self.stats["extraction_failures"] = len(articles) - len(extracted)
        return extracted

    def purify_articles(self, articles):

        purified = []

        for article in articles:
            content = self.purifier.clean(article.get("content", ""))

            if not self.purifier.is_valid(content):
                self.stats["purifier_rejected"] += 1
                continue

            article["content"] = content
            article["word_count"] = len(content.split())
            purified.append(article)

        return purified

    def validate_articles(self, articles):

        validated = []

        for article in articles:
            if not self._has_required_metadata(article):
                self.stats["metadata_rejected"] += 1
                continue

            valid, reason = self.firewall.validate(
                article.get("content", ""),
                self.existing_hashes,
            )

            if not valid:
                self.stats["firewall_rejected"] += 1
                logger.info("Rejected article %s: %s", article.get("url"), reason)
                continue

            validated.append(article)

        self.stats["accepted_articles"] = len(validated)
        return validated

    def save_articles(self, articles):

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as handle:
            json.dump(articles, handle, indent=2, ensure_ascii=False)

        logger.info("Saved %s validated articles to %s", len(articles), self.output_path)
        return self.output_path

    def print_report(self):

        extraction_success = 0.0
        if self.stats["urls_discovered"]:
            extraction_success = (
                self.stats["articles_extracted"] / self.stats["urls_discovered"]
            ) * 100

        print("========================================")
        print()
        print("INGESTION REPORT")
        print()
        print("========================================")
        print()
        print(f"Feeds processed: {self.stats['feeds_processed']}")
        print()
        print(f"URLs discovered: {self.stats['urls_discovered']}")
        print()
        print(f"Duplicate URLs removed: {self.stats['duplicate_urls_removed']}")
        print()
        print(f"Articles extracted: {self.stats['articles_extracted']}")
        print()
        print(f"Extraction failures: {self.stats['extraction_failures']}")
        print()
        print(f"Purifier rejected: {self.stats['purifier_rejected']}")
        print()
        print(f"Content duplicates removed: {self.stats['content_duplicates_removed']}")
        print()
        print(f"Firewall rejected: {self.stats['firewall_rejected']}")
        print()
        print(f"Accepted articles: {self.stats['accepted_articles']}")
        print()
        print(f"Extraction success %: {extraction_success:.2f}")
        print()
        print("========================================")

    def run(self):

        print("Loading raw articles...")
        articles = self.load_articles()
        print("Total raw articles:", len(articles))

        print("Deduplicating URLs...")
        articles = self.deduplicate(articles, stage="url")
        print("After URL dedupe:", len(articles))

        print("Extracting articles...")
        articles = self.extract_articles(articles)
        print("After extraction:", len(articles))

        print("Purifying articles...")
        articles = self.purify_articles(articles)
        print("After purification:", len(articles))

        print("Deduplicating content...")
        articles = self.deduplicate(articles, stage="content")
        print("After content dedupe:", len(articles))

        print("Validating articles...")
        articles = self.validate_articles(articles)
        print("After validation:", len(articles))

        self.save_articles(articles)
        self.print_report()
        self.firewall.print_report()

        return articles

    def _normalized_content(self, content):

        return " ".join(content.split()).strip().lower()

    def _select_best_article(self, articles):

        return max(
            articles,
            key=lambda item: (
                item.get("word_count", 0),
                len(item.get("content", "")),
                1 if item.get("title") else 0,
            ),
        )

    def _has_required_metadata(self, article):

        required_fields = ("url", "formatted_date", "content", "word_count")

        if any(not article.get(field) for field in required_fields):
            return False

        return True


if __name__ == "__main__":

    pipeline = ContentPipeline()

    pipeline.run()