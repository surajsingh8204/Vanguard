from keybert import KeyBERT

from analytics.narrative_abstractor import NarrativeAbstractor


class ClusterLabeler:

    def __init__(self, top_n=5):

        print("Loading KeyBERT model...")

        self.kw_model = KeyBERT()

        self.abstractor = NarrativeAbstractor()

        self.top_n = top_n

    # ---------------------------------------------------
    # GENERATE LABEL
    # ---------------------------------------------------

    def generate_label(self, texts):

        try:

            combined = " ".join(texts[:50])

            keywords = self.kw_model.extract_keywords(

                combined,

                keyphrase_ngram_range=(1, 3),

                stop_words='english',

                use_maxsum=True,

                nr_candidates=20,

                top_n=self.top_n
            )

            phrases = [
                kw[0]
                for kw in keywords
            ]

            if len(phrases) == 0:
                return "Unknown Narrative"

            # ---------------------------------------------
            # LLM NARRATIVE ABSTRACTION
            # ---------------------------------------------

            label = self.abstractor.abstract(phrases)

            return label

        except Exception as e:

            print("Labeling error:", e)

            return "Unknown Narrative"