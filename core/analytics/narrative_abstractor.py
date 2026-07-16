from groq import Groq
import os


class NarrativeAbstractor:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.model = "llama-3.1-8b-instant"

    # ---------------------------------------------------
    # ABSTRACT LABEL
    # ---------------------------------------------------

    def abstract(self, phrases):

        try:

            joined = ", ".join(phrases)

            prompt = f"""
You are an AI narrative intelligence system.

Convert these semantic phrases into ONE short,
human-readable narrative concept.

Rules:
- 3 to 8 words
- concise
- meaningful
- no quotes
- no explanations
- summarize the narrative theme

Phrases:
{joined}
"""

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.2
            )

            label = response.choices[0].message.content.strip()

            return label

        except Exception as e:

            print("Narrative abstraction error:", e)

            return "Unknown Narrative"