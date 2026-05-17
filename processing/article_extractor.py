import trafilatura
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


class ArticleExtractor:

    def __init__(self, max_workers=10):

        self.max_workers = max_workers

    def _extract_trafilatura(self, url):

        try:
            downloaded = trafilatura.fetch_url(url)

            if downloaded:
                text = trafilatura.extract(downloaded)

                if text and len(text) > 200:
                    return text

        except:
            return None

    def _fallback(self, url):

        try:
            response = requests.get(url, timeout=5)

            soup = BeautifulSoup(response.text, "html.parser")

            paragraphs = soup.find_all("p")

            text = " ".join([p.get_text() for p in paragraphs])

            return text[:3000]

        except:
            return None

    def _process_single(self, article):

        url = article.get("url")

        if not url:
            return None

        text = self._extract_trafilatura(url)

        if not text:
            text = self._fallback(url)

        if text:
            article["content"] = text
            return article

        return None

    def extract_batch(self, articles):

        print(f"Extracting content using {self.max_workers} workers...")

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            futures = [executor.submit(self._process_single, a) for a in articles]

            for future in as_completed(futures):

                result = future.result()

                if result:
                    results.append(result)

        print("Extraction complete:", len(results))

        return results