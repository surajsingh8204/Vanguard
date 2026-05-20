import re


class DocumentPurifier:

    def __init__(self):

        # ---------------------------------------------
        # noisy patterns
        # ---------------------------------------------

        self.noise_patterns = [

            r"for additional information.*",
            r"contact:.*",
            r"read more.*",
            r"related articles.*",
            r"recommended stories.*",
            r"click here.*",
            r"follow us.*",
            r"subscribe.*",
            r"all rights reserved.*",
            r"copyright.*",
            r"advertisement.*",
            r"newsletter.*",
            r"share this article.*",
            r"watch live.*",

            r"phone\s*\+?\d+.*",
            r"e-mail:.*",
            r"email:.*",

            r"###.*"
        ]

    # ---------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------

    def clean(self, text):

        if not text:
            return ""

        text = text.lower()

        # ---------------------------------------------
        # remove noisy blocks
        # ---------------------------------------------

        for pattern in self.noise_patterns:

            text = re.sub(
                pattern,
                "",
                text,
                flags=re.IGNORECASE | re.DOTALL
            )

        # ---------------------------------------------
        # remove excessive whitespace
        # ---------------------------------------------

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ---------------------------------------------------
    # QUALITY CHECK
    # ---------------------------------------------------

    def is_valid(self, text):

        if not text:
            return False

        # too short
        if len(text.split()) < 80:
            return False

        # too many separators = likely merged junk
        bad_tokens = [
            "...",
            "###",
            "|",
            ">>",
            "<<"
        ]

        bad_count = sum(
            text.count(t)
            for t in bad_tokens
        )

        if bad_count > 15:
            return False

        return True