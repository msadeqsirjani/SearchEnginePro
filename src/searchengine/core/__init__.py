"""
SearchEngine Pro - Core Module

This module contains the core functionality of the search engine including
the main engine, data models, filters, and history management.
"""

from .engine import WebSearchEngine
from .models import SearchResult, SearchFilter, SearchHistory
from .filters import FilterManager
from .history import HistoryManager

__all__ = [
    "WebSearchEngine",
    "SearchResult",
    "SearchFilter", 
    "SearchHistory",
    "FilterManager",
    "HistoryManager",
] 