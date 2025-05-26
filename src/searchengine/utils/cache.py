"""
SearchEngine Pro - Cache Manager

Simple in-memory cache for search results with TTL support.
"""

import time
import logging
from typing import Any, Optional, Dict
from dataclasses import dataclass

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL"""
    data: Any
    timestamp: float
    ttl: int


class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = config.cache.max_size
        self.enabled = config.cache.enabled
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled:
            return None
            
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry.timestamp < entry.ttl:
                return entry.data
            else:
                del self.cache[key]
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value"""
        if not self.enabled:
            return
            
        # Clean up if cache is full
        if len(self.cache) >= self.max_size:
            self._cleanup_old_entries()
        
        self.cache[key] = CacheEntry(
            data=value,
            timestamp=time.time(),
            ttl=ttl
        )
    
    def _cleanup_old_entries(self):
        """Remove old cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry.timestamp >= entry.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        # If still too large, remove oldest entries
        if len(self.cache) >= self.max_size:
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1].timestamp
            )
            for key, _ in sorted_items[:len(self.cache) - self.max_size + 1]:
                del self.cache[key]
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    async def close(self):
        """Cleanup resources"""
        self.cache.clear() 