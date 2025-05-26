"""
SearchEngine Pro - History Manager

This module handles search history tracking, storage, and retrieval.
"""

import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from ..utils.config import Config
from .models import SearchHistory

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Manages search history storage and retrieval
    """
    
    def __init__(self, config: Config):
        """Initialize history manager"""
        self.config = config
        self.history: List[SearchHistory] = []
        self.history_file = Path(config.data_dir) / "search_history.json"
        self.max_entries = getattr(config.history, 'max_entries', 1000)
        
        # Create data directory if it doesn't exist
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load_history()
    
    def _load_history(self):
        """Load history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [SearchHistory.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self.history)} history entries")
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save history to file"""
        try:
            data = [entry.to_dict() for entry in self.history]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
    
    async def add_entry(self, entry: SearchHistory):
        """Add a new search history entry"""
        self.history.append(entry)
        
        # Limit history size
        if len(self.history) > self.max_entries:
            self.history = self.history[-self.max_entries:]
        
        self._save_history()
    
    def get_history(self, limit: int = 50) -> List[SearchHistory]:
        """Get recent search history"""
        return self.history[-limit:]
    
    def clear_history(self):
        """Clear all search history"""
        self.history = []
        self._save_history()
    
    async def close(self):
        """Cleanup resources"""
        self._save_history() 