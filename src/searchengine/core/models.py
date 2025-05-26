"""
SearchEngine Pro - Data Models

This module defines the core data models used throughout the search engine
including search results, filters, and history entries.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class ResultType(Enum):
    """Enumeration of different result types"""
    WEBPAGE = "webpage"
    NEWS = "news"
    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    ACADEMIC = "academic"
    SHOPPING = "shopping"


class SafeSearchLevel(Enum):
    """Safe search filtering levels"""
    OFF = "off"
    MODERATE = "moderate"
    STRICT = "strict"


@dataclass
class SearchResult:
    """
    Represents a single search result
    
    Attributes:
        title: The title of the result
        url: The URL of the result
        snippet: A short description/snippet
        source: The source domain or provider
        date: Publication or last modified date
        result_type: Type of result (webpage, news, etc.)
        relevance_score: Computed relevance score (0.0-1.0)
        metadata: Additional metadata as key-value pairs
    """
    title: str
    url: str
    snippet: str
    source: str = ""
    date: str = ""
    result_type: ResultType = ResultType.WEBPAGE
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and normalize data after initialization"""
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.url.strip():
            raise ValueError("URL cannot be empty")
        if not self.snippet.strip():
            raise ValueError("Snippet cannot be empty")
            
        # Normalize relevance score
        self.relevance_score = max(0.0, min(1.0, self.relevance_score))
        
        # Convert result_type to enum if it's a string
        if isinstance(self.result_type, str):
            try:
                self.result_type = ResultType(self.result_type.lower())
            except ValueError:
                self.result_type = ResultType.WEBPAGE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "date": self.date,
            "result_type": self.result_type.value,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create SearchResult from dictionary"""
        return cls(
            title=data["title"],
            url=data["url"],
            snippet=data["snippet"],
            source=data.get("source", ""),
            date=data.get("date", ""),
            result_type=ResultType(data.get("result_type", "webpage")),
            relevance_score=data.get("relevance_score", 0.0),
            metadata=data.get("metadata", {})
        )


@dataclass
class SearchFilter:
    """
    Search filtering configuration
    
    Attributes:
        date_range: Time range filter (any, day, week, month, year)
        content_type: Content type filter (any, pdf, doc, image, video)
        language: Language filter (ISO code or 'any')
        region: Region/country filter (ISO code or 'any')
        safe_search: Safe search level
        custom_filters: Additional custom filters
    """
    date_range: str = "any"
    content_type: str = "any"
    language: str = "any"
    region: str = "any"
    safe_search: SafeSearchLevel = SafeSearchLevel.MODERATE
    custom_filters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate filter values"""
        valid_date_ranges = ["any", "day", "week", "month", "year"]
        if self.date_range not in valid_date_ranges:
            raise ValueError(f"Invalid date_range: {self.date_range}")
            
        valid_content_types = ["any", "pdf", "doc", "image", "video", "news"]
        if self.content_type not in valid_content_types:
            self.content_type = "any"
            
        # Convert safe_search to enum if it's a string
        if isinstance(self.safe_search, str):
            try:
                self.safe_search = SafeSearchLevel(self.safe_search.lower())
            except ValueError:
                self.safe_search = SafeSearchLevel.MODERATE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "date_range": self.date_range,
            "content_type": self.content_type,
            "language": self.language,
            "region": self.region,
            "safe_search": self.safe_search.value,
            "custom_filters": self.custom_filters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchFilter":
        """Create SearchFilter from dictionary"""
        return cls(
            date_range=data.get("date_range", "any"),
            content_type=data.get("content_type", "any"),
            language=data.get("language", "any"),
            region=data.get("region", "any"),
            safe_search=SafeSearchLevel(data.get("safe_search", "moderate")),
            custom_filters=data.get("custom_filters", {})
        )
    
    def is_active(self) -> bool:
        """Check if any filters are active (not default values)"""
        return (
            self.date_range != "any" or
            self.content_type != "any" or
            self.language != "any" or
            self.region != "any" or
            self.safe_search != SafeSearchLevel.MODERATE or
            bool(self.custom_filters)
        )


@dataclass
class SearchHistory:
    """
    Represents a search history entry
    
    Attributes:
        query: The search query
        timestamp: When the search was performed
        results_count: Number of results returned
        filters: Filter settings used
        execution_time: How long the search took (seconds)
        page: Which page of results was viewed
        session_id: Unique session identifier
    """
    query: str
    timestamp: datetime
    results_count: int = 0
    filters: Optional[SearchFilter] = None
    execution_time: float = 0.0
    page: int = 1
    session_id: str = ""
    
    def __post_init__(self):
        """Validate and normalize data"""
        if not self.query.strip():
            raise ValueError("Query cannot be empty")
        if self.results_count < 0:
            self.results_count = 0
        if self.execution_time < 0:
            self.execution_time = 0.0
        if self.page < 1:
            self.page = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "query": self.query,
            "timestamp": self.timestamp.isoformat(),
            "results_count": self.results_count,
            "filters": self.filters.to_dict() if self.filters else None,
            "execution_time": self.execution_time,
            "page": self.page,
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchHistory":
        """Create SearchHistory from dictionary"""
        filters = None
        if data.get("filters"):
            filters = SearchFilter.from_dict(data["filters"])
            
        return cls(
            query=data["query"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            results_count=data.get("results_count", 0),
            filters=filters,
            execution_time=data.get("execution_time", 0.0),
            page=data.get("page", 1),
            session_id=data.get("session_id", "")
        )


@dataclass
class SearchQuery:
    """
    Represents a parsed search query with operators
    
    Attributes:
        raw_query: Original query string
        terms: List of search terms
        required_terms: Terms that must be included (+term)
        excluded_terms: Terms that must be excluded (-term)
        exact_phrases: Phrases that must match exactly ("phrase")
        site_filter: Specific site to search (site:example.com)
        filetype_filter: Specific file type (filetype:pdf)
    """
    raw_query: str
    terms: List[str] = field(default_factory=list)
    required_terms: List[str] = field(default_factory=list)
    excluded_terms: List[str] = field(default_factory=list)
    exact_phrases: List[str] = field(default_factory=list)
    site_filter: str = ""
    filetype_filter: str = ""
    
    @classmethod
    def parse(cls, query: str) -> "SearchQuery":
        """Parse a raw query string into structured components"""
        import re
        
        parsed = cls(raw_query=query)
        
        # Find exact phrases (quoted text)
        phrase_pattern = r'"([^"]+)"'
        phrases = re.findall(phrase_pattern, query)
        parsed.exact_phrases = phrases
        
        # Remove phrases from query for further processing
        query_without_phrases = re.sub(phrase_pattern, '', query)
        
        # Find site filters
        site_pattern = r'site:(\S+)'
        site_match = re.search(site_pattern, query_without_phrases)
        if site_match:
            parsed.site_filter = site_match.group(1)
            query_without_phrases = re.sub(site_pattern, '', query_without_phrases)
        
        # Find filetype filters
        filetype_pattern = r'filetype:(\S+)'
        filetype_match = re.search(filetype_pattern, query_without_phrases)
        if filetype_match:
            parsed.filetype_filter = filetype_match.group(1)
            query_without_phrases = re.sub(filetype_pattern, '', query_without_phrases)
        
        # Split remaining terms
        words = query_without_phrases.split()
        
        for word in words:
            if word.startswith('+'):
                parsed.required_terms.append(word[1:])
            elif word.startswith('-'):
                parsed.excluded_terms.append(word[1:])
            elif word.strip():
                parsed.terms.append(word)
        
        return parsed
    
    def to_simple_query(self) -> str:
        """Convert back to a simple query string for search APIs"""
        parts = []
        
        # Add regular terms
        parts.extend(self.terms)
        
        # Add required terms
        for term in self.required_terms:
            parts.append(f'"{term}"')
        
        # Add exact phrases
        for phrase in self.exact_phrases:
            parts.append(f'"{phrase}"')
        
        # Add site filter
        if self.site_filter:
            parts.append(f"site:{self.site_filter}")
        
        # Add filetype filter
        if self.filetype_filter:
            parts.append(f"filetype:{self.filetype_filter}")
        
        return " ".join(parts)


@dataclass
class Bookmark:
    """
    Represents a bookmarked search result
    
    Attributes:
        result: The bookmarked search result
        created_at: When the bookmark was created
        tags: List of tags for organization
        notes: User notes about the bookmark
        folder: Bookmark folder/category
    """
    result: SearchResult
    created_at: datetime
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    folder: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "result": self.result.to_dict(),
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
            "notes": self.notes,
            "folder": self.folder
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bookmark":
        """Create Bookmark from dictionary"""
        return cls(
            result=SearchResult.from_dict(data["result"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            tags=data.get("tags", []),
            notes=data.get("notes", ""),
            folder=data.get("folder", "default")
        ) 