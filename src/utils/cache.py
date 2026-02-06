
import redis
import hashlib
import json
from typing import Optional
from src.config import REDIS_URL

class CacheManager:
    _instance = None
    _redis_client = None
    _is_available = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize Redis connection safely."""
        try:
            self._redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            # Ping to verify connection
            self._redis_client.ping()
            self._is_available = True
            print(f"✅ Redis Cache Connected: {REDIS_URL}")
        except Exception as e:
            self._is_available = False
            print(f"⚠️ Redis Cache Unavailable: {e}. Running without cache.")

    def _generate_key(self, text: str) -> str:
        """Generate SHA256 hash for the query text."""
        # Normalize: lower case, strip whitespace
        normalized = text.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, query: str) -> Optional[str]:
        """Retrieve cached answer for a query."""
        if not self._is_available:
            return None
        
        key = self._generate_key(query)
        try:
            return self._redis_client.get(key)
        except Exception:
            return None

    def set(self, query: str, answer: str, ttl: int = 86400):
        """Cache an answer for a query (default TTL: 24 hours)."""
        if not self._is_available:
            return
        
        key = self._generate_key(query)
        try:
            self._redis_client.setex(key, ttl, answer)
        except Exception as e:
            print(f"⚠️ Failed to write to cache: {e}")

# Global instance
cache = CacheManager()
