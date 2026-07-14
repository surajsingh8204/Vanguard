import re


class DocumentPurifier:

    def __init__(self):
        self.noise_patterns = [
            r"for additional information.*",
            r"contact:.*",
            r"read more.*",
            r"related articles.*",
            r"recommended stories.*",
            r"recommended for you.*",
            r"click here.*",
            r"follow us.*",
            r"subscribe.*",
            r"sign up.*",
            r"all rights reserved.*",
            r"copyright.*",
            r"advertisement.*",
            r"newsletter.*",
            r"share this article.*",
            r"share on.*",
            r"watch live.*",
            r"related story.*",
            r"you may also like.*",
            r"phone\s*\+?\d+.*",
            r"e-mail:.*",
            r"email:.*",
            r"mailto:.*",
            r"https?://\S+",
            r"###.*",
        ]

        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.noise_patterns
        ]

        self.inline_noise_terms = [
            "copyright",
            "advertisement",
            "newsletter",
            "related articles",
            "recommended stories",
            "share this article",
            "phone",
            "email",
            "e-mail",
        ]

    def _strip_noise_lines(self, text):

        cleaned_lines = []

        for line in text.splitlines():

            candidate = line.strip()

            if not candidate:
                continue

            lowered = candidate.lower()

            if any(term in lowered for term in self.inline_noise_terms):
                continue

            if any(pattern.search(candidate) for pattern in self.compiled_patterns):
                continue

            cleaned_lines.append(candidate)

        return "\n".join(cleaned_lines)

    def _remove_inline_boilerplate(self, text):

        cleaned = text

        for pattern in self.compiled_patterns:
            cleaned = pattern.sub(" ", cleaned)

        return cleaned

    def _normalize_whitespace(self, text):

        return re.sub(r"\s+", " ", text).strip()

    # ---------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------

    def clean(self, text):

        if not text:
            return ""

        text = self._strip_noise_lines(text)
        text = self._remove_inline_boilerplate(text)
        text = self._normalize_whitespace(text)

        return text

    # ---------------------------------------------------
    # QUALITY CHECK
    # ---------------------------------------------------

    def is_valid(self, text):

        if not text:
            return False

        if len(text.split()) < 40:
            return False

        bad_tokens = ["...", "###", "|", ">>", "<<"]

        bad_count = sum(
            text.count(t)
            for t in bad_tokens
        )

        if bad_count > 15:
            return False

        return True