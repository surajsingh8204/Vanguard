import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNK_SIZE = 300

MIN_CHUNK_LENGTH = 50

MIN_CLUSTER_SIZE = 12

MIN_SAMPLES = 4

MIN_SUBCLUSTER_SIZE = 5

GLOBAL_RETRIEVAL_K = 30

FINAL_RERANK_K = 8

TOP_CLUSTERS = 2

MIN_CONFIDENCE = 0.30

HTML_TAG_RATIO_THRESHOLD = 0.15

CSS_JS_HIT_THRESHOLD = 3

NAVIGATION_HIT_THRESHOLD = 3

LOW_INFORMATION_THRESHOLD = 0.25

LANGUAGE_QUALITY_THRESHOLD = 0.55

CLOUDFLARE_PATTERNS = (
	"cloudflare",
	"ray id",
	"attention required",
	"performance & security",
	"checking your browser",
	"verify you are human",
	"ddos protection",
)

CSS_JS_PATTERNS = (
	".widget",
	"@media",
	"display:",
	"font-size",
	"padding:",
	"margin:",
	"color:",
	"svg",
	"fill",
	"stroke",
	"script",
	"function(",
	"var",
	"const",
	"let",
)

NAVIGATION_PATTERNS = (
	"share",
	"subscribe",
	"sign in",
	"login",
	"register",
	"cookie",
	"privacy policy",
	"terms of service",
	"advertisement",
	"menu",
	"next article",
	"previous article",
)

FORECAST_TOP_K = 5

ARTIFACT_DIR = "artifacts"

VECTORSTORE_DIR = "artifacts/vectorstore"

ANALYTICS_DIR = "artifacts/analytics"

RAW_FEEDS_DIR = "data_lake/raw_feeds"

RAW_ARTICLES_DIR = "data_lake/raw"

PROCESSED_DIR = "data_lake/processed"

ENRICHED_ARTICLES_PATH = "data_lake/processed/enriched_articles.json"

PROCESSED_FEEDS_FILE = "data_lake/processed_feeds.txt"

ARTICLE_FETCH_TIMEOUT_SECONDS = 10

ARTICLE_FETCH_RETRIES = 3

ARTICLE_FETCH_BACKOFF_SECONDS = 1

FEED_DOWNLOAD_TIMEOUT_SECONDS = 10

FEED_DOWNLOAD_RETRIES = 3

FEED_DOWNLOAD_BACKOFF_SECONDS = 1

GDELT_FEED_BASE_URL = "http://data.gdeltproject.org/gdeltv2/"

LLM_MODEL = "llama-3.1-8b-instant"

GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

SEARCH_QUERY = "(geopolitics OR diplomacy OR conflict OR military OR sanctions)"

MAX_ARTICLES = 100

VECTOR_DIMENSION = 384

RAW_DATA_PATH = "data/raw/news_raw.csv"

PROCESSED_DATA_PATH = "data/processed/news_with_embeddings.csv"

BERT_MODEL = f"sentence-transformers/{EMBEDDING_MODEL}"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")