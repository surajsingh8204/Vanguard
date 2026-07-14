import hashlib
import re

from config.settings import (
    CSS_JS_HIT_THRESHOLD,
    CSS_JS_PATTERNS,
    CLOUDFLARE_PATTERNS,
    HTML_TAG_RATIO_THRESHOLD,
    LANGUAGE_QUALITY_THRESHOLD,
    MIN_CHUNK_LENGTH,
    NAVIGATION_HIT_THRESHOLD,
    NAVIGATION_PATTERNS,
    LOW_INFORMATION_THRESHOLD,
)


class DataQualityFirewall:

    def __init__(self):
        self.stats = {
            "accepted": 0,
            "cloudflare": 0,
            "html": 0,
            "css_js": 0,
            "navigation": 0,
            "short": 0,
            "duplicate": 0,
            "low_information": 0,
            "language_quality": 0,
        }

    def is_cloudflare(self, text):
        lowered = text.lower()
        return any(pattern in lowered for pattern in CLOUDFLARE_PATTERNS)

    def is_html_heavy(self, text):
        words = text.split()
        total_words = len(words)
        if total_words == 0:
            return True

        html_markers = (
            text.count("<")
            + text.count(">")
            + text.count("</")
            + text.count("/>")
        )
        ratio = html_markers / total_words
        return ratio > HTML_TAG_RATIO_THRESHOLD

    def is_css_or_js(self, text):
        lowered = text.lower()
        hits = sum(1 for pattern in CSS_JS_PATTERNS if pattern in lowered)
        return hits >= CSS_JS_HIT_THRESHOLD

    def is_navigation(self, text):
        lowered = text.lower()
        hits = sum(1 for pattern in NAVIGATION_PATTERNS if pattern in lowered)
        return hits >= NAVIGATION_HIT_THRESHOLD

    def is_too_short(self, text):
        word_count = len(text.split())
        return word_count < MIN_CHUNK_LENGTH

    def is_low_information(self, text):
        words = [word.strip().lower() for word in text.split() if word.strip()]
        total_words = len(words)
        if total_words == 0:
            return True

        unique_words = len(set(words))
        ratio = unique_words / total_words
        return ratio < LOW_INFORMATION_THRESHOLD

    def is_duplicate(self, text, existing_hashes):
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        if text_hash in existing_hashes:
            return True, text_hash
        return False, text_hash

    def is_language_quality(self, text):
        total_characters = len(text)
        if total_characters == 0:
            return False

        alphabetic_characters = sum(1 for char in text if char.isalpha())
        ratio = alphabetic_characters / total_characters
        return ratio < LANGUAGE_QUALITY_THRESHOLD

    def validate(self, text, existing_hashes):
        if self.is_cloudflare(text):
            self.stats["cloudflare"] += 1
            return False, "cloudflare"

        if self.is_html_heavy(text):
            self.stats["html"] += 1
            return False, "html"

        if self.is_css_or_js(text):
            self.stats["css_js"] += 1
            return False, "css_js"

        if self.is_navigation(text):
            self.stats["navigation"] += 1
            return False, "navigation"

        if self.is_too_short(text):
            self.stats["short"] += 1
            return False, "short"

        is_duplicate, text_hash = self.is_duplicate(text, existing_hashes)
        if is_duplicate:
            self.stats["duplicate"] += 1
            return False, "duplicate"

        if self.is_low_information(text):
            self.stats["low_information"] += 1
            return False, "low_information"

        if self.is_language_quality(text):
            self.stats["language_quality"] += 1
            return False, "language_quality"

        existing_hashes.add(text_hash)
        self.stats["accepted"] += 1
        return True, "valid"

    def print_report(self):
        print("========================================")
        print("DATA QUALITY REPORT")
        print("========================================")
        print()
        print(f"Accepted: {self.stats['accepted']}")
        print()
        print("Rejected")
        print()
        print(f"Cloudflare: {self.stats['cloudflare']}")
        print()
        print(f"HTML: {self.stats['html']}")
        print()
        print(f"CSS/JS: {self.stats['css_js']}")
        print()
        print(f"Navigation: {self.stats['navigation']}")
        print()
        print(f"Duplicate: {self.stats['duplicate']}")
        print()
        print(f"Short: {self.stats['short']}")
        print()
        print(f"Low Information: {self.stats['low_information']}")
        print()
        print(f"Language Quality: {self.stats['language_quality']}")
        print()
        print("========================================")
