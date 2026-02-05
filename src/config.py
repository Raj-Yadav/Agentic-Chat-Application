"""
Configuration module for the Agentic Chat Application.
Centralizes environment variables, file paths, and scraping settings.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Project Paths ---
PROJ_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str = os.path.join(PROJ_ROOT, "data")
CHROMA_DB_DIR: str = os.path.join(DATA_DIR, "chroma_db")

# --- API Keys ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY is not set in environment variables.")

# --- Scraper Configuration ---
# List of authoritative URLs to scrape for knowledge base
AUTHORITATIVE_URLS: List[str] = [
    "https://www.synergisticit.com/",
    "https://www.synergisticit.com/about-us/",
    "https://www.synergisticit.com/javadevjopp/",
    "https://www.synergisticit.com/data-science-training-in-indianapolis/",
    "https://www.synergisticit.com/synergisticit-technology-upskill-program/",
    "https://www.synergisticit.com/it-staffing/"
]

# Keywords to exclude from crawling
EXCLUDE_KEYWORDS: List[str] = [
    "interview-questions", 
    "3000-technical-interview-questions-and-answers",
    "category", # Skip archive pages
    "tag",      # Skip tag archives
    "wp-json"   # Skip API endpoints
]
