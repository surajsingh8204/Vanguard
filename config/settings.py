import os
from dotenv import load_dotenv

load_dotenv()

GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

SEARCH_QUERY = "(geopolitics OR diplomacy OR conflict OR military OR sanctions)"

MAX_ARTICLES = 100

VECTOR_DIMENSION = 384

RAW_DATA_PATH = "data/raw/news_raw.csv"

PROCESSED_DATA_PATH = "data/processed/news_with_embeddings.csv"

BERT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")