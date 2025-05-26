"""
SearchEngine Pro - Main Search Engine

This module contains the core WebSearchEngine class that handles search
operations, result processing, and coordination with various search providers.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from ..api.providers import SearchProviderManager
from ..api.client import HTTPClient
from ..utils.config import Config
from ..utils.cache import CacheManager
from .models import (
    SearchResult, SearchFilter, SearchHistory, SearchQuery,
    ResultType, SafeSearchLevel
)
from .filters import FilterManager
from .history import HistoryManager

logger = logging.getLogger(__name__)


class WebSearchEngine:
    """
    Main search engine class that coordinates all search operations
    
    This class provides the primary interface for performing web searches,
    managing results, handling filters, and maintaining search history.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the search engine
        
        Args:
            config: Configuration object, loads default if None
        """
        self.config = config or Config.load()
        self.session_id = str(uuid.uuid4())
        
        # Initialize managers
        self.provider_manager = SearchProviderManager(self.config)
        self.http_client = HTTPClient(self.config)
        self.cache_manager = CacheManager(self.config)
        self.filter_manager = FilterManager()
        self.history_manager = HistoryManager(self.config)
        
        # Current search state
        self.current_query = ""
        self.current_results: List[SearchResult] = []
        self.current_page = 1
        self.current_filters = SearchFilter()
        self.total_results = 0
        
        # Performance tracking
        self.last_search_time = 0.0
        self.search_stats = {
            "total_searches": 0,
            "total_results": 0,
            "average_time": 0.0,
            "cache_hits": 0
        }
        
        logger.info(f"Search engine initialized with session ID: {self.session_id}")
    
    async def search_async(
        self,
        query: str,
        page: int = 1,
        filters: Optional[SearchFilter] = None,
        use_cache: bool = True
    ) -> Tuple[List[SearchResult], int, float]:
        """
        Perform an asynchronous web search
        
        Args:
            query: Search query string
            page: Page number (1-based)
            filters: Search filters to apply
            use_cache: Whether to use cached results
            
        Returns:
            Tuple of (results, total_count, execution_time)
        """
        start_time = time.time()
        
        try:
            # Parse and validate query
            parsed_query = SearchQuery.parse(query)
            if not parsed_query.terms and not parsed_query.exact_phrases:
                raise ValueError("Query must contain search terms")
            
            # Apply filters
            search_filters = filters or self.current_filters
            
            # Check cache first
            cache_key = self._generate_cache_key(query, page, search_filters)
            if use_cache:
                cached_results = await self.cache_manager.get(cache_key)
                if cached_results:
                    self.search_stats["cache_hits"] += 1
                    execution_time = time.time() - start_time
                    return cached_results["results"], cached_results["total"], execution_time
            
            # Perform search using provider
            results, total_count = await self.provider_manager.search(
                parsed_query, page, search_filters
            )
            
            # Process and enhance results
            processed_results = await self._process_results(results, parsed_query)
            
            # Cache results
            if use_cache:
                await self.cache_manager.set(
                    cache_key,
                    {"results": processed_results, "total": total_count},
                    ttl=self.config.cache.search_ttl
                )
            
            # Update search state
            self.current_query = query
            self.current_results = processed_results
            self.current_page = page
            self.current_filters = search_filters
            self.total_results = total_count
            
            execution_time = time.time() - start_time
            self.last_search_time = execution_time
            
            # Update statistics
            self._update_search_stats(len(processed_results), execution_time)
            
            # Add to history
            history_entry = SearchHistory(
                query=query,
                timestamp=datetime.now(),
                results_count=total_count,
                filters=search_filters,
                execution_time=execution_time,
                page=page,
                session_id=self.session_id
            )
            await self.history_manager.add_entry(history_entry)
            
            logger.info(
                f"Search completed: '{query}' -> {len(processed_results)} results "
                f"in {execution_time:.2f}s"
            )
            
            return processed_results, total_count, execution_time
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            execution_time = time.time() - start_time
            return [], 0, execution_time
    
    def search(
        self,
        query: str,
        page: int = 1,
        filters: Optional[SearchFilter] = None,
        use_cache: bool = True
    ) -> Tuple[List[SearchResult], int, float]:
        """
        Synchronous wrapper for search_async
        
        Args:
            query: Search query string
            page: Page number (1-based)
            filters: Search filters to apply
            use_cache: Whether to use cached results
            
        Returns:
            Tuple of (results, total_count, execution_time)
        """
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_running_loop()
                # If there's a running loop, use ThreadPoolExecutor
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.search_async(query, page, filters, use_cache))
                    return future.result()
            except RuntimeError:
                # No running loop, safe to use asyncio.run
                return asyncio.run(self.search_async(query, page, filters, use_cache))
        except Exception as e:
            logger.error(f"Synchronous search failed: {e}")
            return [], 0, 0.0
    
    async def _process_results(
        self,
        raw_results: List[Dict[str, Any]],
        query: SearchQuery
    ) -> List[SearchResult]:
        """
        Process and enhance raw search results
        
        Args:
            raw_results: Raw results from search provider
            query: Parsed search query
            
        Returns:
            List of processed SearchResult objects
        """
        processed_results = []
        
        for i, raw_result in enumerate(raw_results):
            try:
                # Create SearchResult object
                result = SearchResult(
                    title=raw_result.get("title", ""),
                    url=raw_result.get("url", ""),
                    snippet=raw_result.get("snippet", ""),
                    source=raw_result.get("source", ""),
                    date=raw_result.get("date", ""),
                    result_type=ResultType(raw_result.get("type", "webpage")),
                    metadata=raw_result.get("metadata", {})
                )
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(result, query)
                result.relevance_score = relevance_score
                
                processed_results.append(result)
                
            except Exception as e:
                logger.warning(f"Failed to process result {i}: {e}")
                continue
        
        # Sort by relevance score
        processed_results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return processed_results
    
    def _calculate_relevance_score(
        self,
        result: SearchResult,
        query: SearchQuery
    ) -> float:
        """
        Calculate relevance score for a search result
        
        Args:
            result: Search result to score
            query: Parsed search query
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        max_score = 0.0
        
        # Title matching (highest weight)
        title_lower = result.title.lower()
        for term in query.terms + query.required_terms:
            max_score += 3.0
            if term.lower() in title_lower:
                score += 3.0
        
        # Exact phrase matching in title
        for phrase in query.exact_phrases:
            max_score += 5.0
            if phrase.lower() in title_lower:
                score += 5.0
        
        # Snippet matching (medium weight)
        snippet_lower = result.snippet.lower()
        for term in query.terms + query.required_terms:
            max_score += 2.0
            if term.lower() in snippet_lower:
                score += 2.0
        
        # URL matching (low weight)
        url_lower = result.url.lower()
        for term in query.terms + query.required_terms:
            max_score += 1.0
            if term.lower() in url_lower:
                score += 1.0
        
        # Domain authority bonus (if available)
        if result.metadata.get("domain_authority"):
            authority = float(result.metadata["domain_authority"]) / 100.0
            score += authority * 2.0
            max_score += 2.0
        
        # Recency bonus for news results
        if result.result_type == ResultType.NEWS and result.date:
            try:
                # Parse date and give bonus for recent results
                # Implementation would depend on date format
                score += 1.0
                max_score += 1.0
            except:
                pass
        
        # Normalize score
        if max_score > 0:
            return min(1.0, score / max_score)
        else:
            return 0.5  # Default score if no terms to match
    
    def _generate_cache_key(
        self,
        query: str,
        page: int,
        filters: SearchFilter
    ) -> str:
        """Generate cache key for search results"""
        import hashlib
        
        # Create a unique key based on query, page, and filters
        key_data = f"{query}|{page}|{filters.to_dict()}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_search_stats(self, result_count: int, execution_time: float):
        """Update search statistics"""
        self.search_stats["total_searches"] += 1
        self.search_stats["total_results"] += result_count
        
        # Update average time
        total_searches = self.search_stats["total_searches"]
        current_avg = self.search_stats["average_time"]
        new_avg = ((current_avg * (total_searches - 1)) + execution_time) / total_searches
        self.search_stats["average_time"] = new_avg
    
    async def next_page(self) -> Tuple[List[SearchResult], int, float]:
        """Get next page of current search results"""
        if not self.current_query:
            raise ValueError("No active search to paginate")
        
        return await self.search_async(
            self.current_query,
            self.current_page + 1,
            self.current_filters
        )
    
    async def previous_page(self) -> Tuple[List[SearchResult], int, float]:
        """Get previous page of current search results"""
        if not self.current_query:
            raise ValueError("No active search to paginate")
        
        if self.current_page <= 1:
            raise ValueError("Already on first page")
        
        return await self.search_async(
            self.current_query,
            self.current_page - 1,
            self.current_filters
        )
    
    def get_current_results(self) -> Tuple[List[SearchResult], int, float]:
        """Get current search results without making a new search"""
        return self.current_results, self.total_results, self.last_search_time
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages based on results per page"""
        if self.total_results == 0:
            return 0
        results_per_page = self.config.search.results_per_page
        return (self.total_results + results_per_page - 1) // results_per_page
    
    @property 
    def last_query(self) -> str:
        """Get the last executed query"""
        return self.current_query
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics for the enhanced console interface"""
        return {
            "total_searches": self.search_stats["total_searches"],
            "total_results": self.search_stats["total_results"], 
            "avg_search_time": self.search_stats["average_time"],
            "success_rate": 100.0 if self.search_stats["total_searches"] == 0 else 
                           (self.search_stats["total_searches"] / max(1, self.search_stats["total_searches"])) * 100,
            "cache_hits": self.search_stats["cache_hits"],
            "provider": self.config.api.default_provider,
            "session_id": self.session_id,
            "current_page": self.current_page,
            "total_pages": self.total_pages
        }
    
    def apply_filters(self, filters: SearchFilter):
        """Apply new search filters"""
        self.current_filters = filters
        self.filter_manager.apply_filters(filters)
    
    def get_search_history(self, limit: int = 50) -> List[SearchHistory]:
        """Get recent search history"""
        return self.history_manager.get_history(limit)
    
    def clear_search_history(self):
        """Clear all search history"""
        self.history_manager.clear_history()
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        return {
            **self.search_stats,
            "session_id": self.session_id,
            "current_query": self.current_query,
            "current_page": self.current_page,
            "total_results": self.total_results,
            "last_search_time": self.last_search_time,
            "cache_size": self.cache_manager.get_cache_size(),
            "active_filters": self.current_filters.is_active()
        }
    
    async def suggest_queries(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        try:
            return await self.provider_manager.get_suggestions(partial_query)
        except Exception as e:
            logger.warning(f"Failed to get suggestions for '{partial_query}': {e}")
            return []
    
    async def get_trending_searches(self) -> List[str]:
        """Get trending search queries"""
        try:
            return await self.provider_manager.get_trending()
        except Exception as e:
            logger.warning(f"Failed to get trending searches: {e}")
            return []
    
    def export_results(
        self,
        format_type: str = "json",
        include_metadata: bool = True
    ) -> str:
        """
        Export current search results in specified format
        
        Args:
            format_type: Export format ('json', 'csv', 'txt')
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted string of results
        """
        if not self.current_results:
            return ""
        
        if format_type.lower() == "json":
            import json
            data = {
                "query": self.current_query,
                "page": self.current_page,
                "total_results": self.total_results,
                "execution_time": self.last_search_time,
                "results": [r.to_dict() for r in self.current_results]
            }
            if include_metadata:
                data["filters"] = self.current_filters.to_dict()
                data["session_id"] = self.session_id
                data["timestamp"] = datetime.now().isoformat()
            
            return json.dumps(data, indent=2)
        
        elif format_type.lower() == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # Header
            headers = ["Title", "URL", "Snippet", "Source", "Date", "Type"]
            if include_metadata:
                headers.extend(["Relevance Score", "Metadata"])
            writer.writerow(headers)
            
            # Data
            for result in self.current_results:
                row = [
                    result.title,
                    result.url,
                    result.snippet,
                    result.source,
                    result.date,
                    result.result_type.value
                ]
                if include_metadata:
                    row.extend([
                        result.relevance_score,
                        str(result.metadata)
                    ])
                writer.writerow(row)
            
            return output.getvalue()
        
        elif format_type.lower() == "txt":
            lines = [
                f"Search Query: {self.current_query}",
                f"Page: {self.current_page}",
                f"Total Results: {self.total_results}",
                f"Execution Time: {self.last_search_time:.2f}s",
                f"Session ID: {self.session_id}",
                f"Timestamp: {datetime.now().isoformat()}",
                "",
                "=" * 80,
                ""
            ]
            
            for i, result in enumerate(self.current_results, 1):
                lines.extend([
                    f"{i}. {result.title}",
                    f"   URL: {result.url}",
                    f"   Source: {result.source}",
                    f"   Date: {result.date}",
                    f"   Type: {result.result_type.value}",
                    f"   Snippet: {result.snippet}",
                ])
                
                if include_metadata and result.metadata:
                    lines.append(f"   Metadata: {result.metadata}")
                
                if include_metadata:
                    lines.append(f"   Relevance: {result.relevance_score:.3f}")
                
                lines.append("")
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    async def close(self):
        """Clean up resources"""
        await self.http_client.close()
        await self.cache_manager.close()
        await self.history_manager.close()
        logger.info("Search engine closed") 