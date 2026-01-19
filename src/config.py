import os
from dotenv import load_dotenv

load_dotenv()

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJ_ROOT, "data")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Scraper Config
AUTHORITATIVE_URLS = [
    "https://www.synergisticit.com/",
    "https://www.synergisticit.com/about-us/",
    "https://www.synergisticit.com/javadevjopp/",
    "https://www.synergisticit.com/data-science-training-in-indianapolis/",
    "https://www.synergisticit.com/synergisticit-technology-upskill-program/",
    "https://www.synergisticit.com/it-staffing/"
]
