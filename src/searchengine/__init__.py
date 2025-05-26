"""
SearchEngine Pro - Interactive Console Web Search Engine

A comprehensive console-based search interface with real web search capabilities,
advanced filtering, search history, and interactive command processing.
"""

__version__ = "3.2.0"
__author__ = "SearchEngine Pro Team"
__email__ = "dev@searchengine-pro.com"
__license__ = "MIT"

from .core.engine import WebSearchEngine
from .core.models import SearchResult, SearchFilter
from .ui.console import ConsoleInterface
from .utils.config import Config

__all__ = [
    "WebSearchEngine",
    "SearchResult", 
    "SearchFilter",
    "ConsoleInterface",
    "Config",
] 