"""
SearchEngine Pro - Search Providers

This module contains different search providers including simulation
and real API integrations.
"""

import asyncio
import logging
import requests
from typing import List, Dict, Any, Tuple
from abc import ABC, abstractmethod
import time
import re
from urllib.parse import urlparse

from ..core.models import SearchQuery, SearchFilter, ResultType
from ..utils.config import Config

try:
    from googlesearch import search as google_search
    from bs4 import BeautifulSoup
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

logger = logging.getLogger(__name__)


class SearchProvider(ABC):
    """Abstract base class for search providers"""
    
    @abstractmethod
    async def search(self, query: SearchQuery, page: int, filters: SearchFilter) -> Tuple[List[Dict[str, Any]], int]:
        """Perform search and return results"""
        pass
    
    @abstractmethod
    async def get_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions"""
        pass


class SimulationProvider(SearchProvider):
    """Simulation provider for testing and demo purposes"""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def search(self, query: SearchQuery, page: int, filters: SearchFilter) -> Tuple[List[Dict[str, Any]], int]:
        """Simulate search results"""
        await asyncio.sleep(0.2)  # Simulate search delay
        
        results = []
        base_index = (page - 1) * self.config.search.results_per_page
        
        # Generate realistic results based on query
        query_text = query.raw_query.lower()
        
        if "python" in query_text:
            results.extend([
                {
                    "title": "Python.org - Welcome to Python.org",
                    "url": "https://www.python.org/",
                    "snippet": "The official home of the Python Programming Language. Download the latest version, browse documentation, and learn Python programming.",
                    "source": "python.org",
                    "date": "2024-01-15",
                    "type": "webpage"
                },
                {
                    "title": "Python Tutorial - W3Schools",
                    "url": "https://www.w3schools.com/python/",
                    "snippet": "Well organized and easy to understand Web building tutorials with lots of examples of how to use HTML, CSS, JavaScript, SQL, Python, PHP, Bootstrap, Java, XML and more.",
                    "source": "w3schools.com",
                    "date": "2024-01-10",
                    "type": "webpage"
                }
            ])
        
        elif "news" in query_text or "2024" in query_text:
            results.extend([
                {
                    "title": f"Latest News: {query.raw_query.title()} - BBC News",
                    "url": "https://www.bbc.com/news",
                    "snippet": "Breaking news, analysis and features from BBC News, including international, UK, business, technology and entertainment news.",
                    "source": "BBC News",
                    "date": "2024-01-20",
                    "type": "news"
                }
            ])
        
        elif "how to" in query_text:
            results.extend([
                {
                    "title": f"How to {query_text.replace('how to ', '').title()} - WikiHow",
                    "url": "https://www.wikihow.com",
                    "snippet": "Detailed step-by-step instructions with helpful tips and illustrations to guide you through the process.",
                    "source": "WikiHow",
                    "date": "2024-01-18",
                    "type": "webpage"
                }
            ])
        
        # Fill remaining slots with generic results
        while len(results) < self.config.search.results_per_page:
            idx = len(results) + base_index + 1
            results.append({
                "title": f"{query.raw_query.title()} - Resource #{idx}",
                "url": f"https://www.example{idx}.com/{query.raw_query.replace(' ', '-')}",
                "snippet": f"Additional information and resources about {query.raw_query} with detailed analysis and comprehensive coverage.",
                "source": f"Source {idx}",
                "date": "2024-01-15",
                "type": "webpage"
            })
        
        total_results = len(results) * 10 + (page - 1) * 50  # Simulate large result set
        
        return results[:self.config.search.results_per_page], total_results
    
    async def get_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions"""
        await asyncio.sleep(0.1)
        
        # Simple suggestion logic
        suggestions = [
            f"{partial_query} tutorial",
            f"{partial_query} examples",
            f"{partial_query} guide",
            f"how to {partial_query}",
            f"{partial_query} best practices"
        ]
        
        return suggestions[:5]


class GoogleSearchProvider(SearchProvider):
    """Real Google search provider using googlesearch-python"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.search.user_agent
        })
        
        if not GOOGLE_AVAILABLE:
            logger.warning("googlesearch-python not available, falling back to simulation")
    
    async def search(self, query: SearchQuery, page: int, filters: SearchFilter) -> Tuple[List[Dict[str, Any]], int]:
        """Perform real Google search"""
        if not GOOGLE_AVAILABLE:
            logger.warning("Google search not available, using simulation")
            sim_provider = SimulationProvider(self.config)
            return await sim_provider.search(query, page, filters)
        
        try:
            # Small delay to be respectful to Google
            await asyncio.sleep(self.config.search.request_delay)
            
            # Prepare search query
            search_query = self._build_search_query(query, filters)
            
            # Calculate results range for pagination
            results_per_page = self.config.search.results_per_page
            start_index = (page - 1) * results_per_page
            
            # Perform Google search
            logger.info(f"Searching Google for: {search_query} (Page {page})")
            
            search_results = []
            try:
                # Get URLs from Google search with pagination support
                urls = list(google_search(
                    search_query, 
                    num_results=results_per_page,
                    lang='en',
                    sleep_interval=1,  # Be respectful with delays
                    timeout=10,
                    start_num=start_index  # This enables pagination
                ))
                
                # Fetch metadata for each URL
                for i, url in enumerate(urls):
                    try:
                        result = await self._fetch_result_metadata(url, i + start_index + 1)
                        if result:
                            search_results.append(result)
                    except Exception as e:
                        logger.warning(f"Failed to fetch metadata for {url}: {e}")
                        # Create basic result if metadata fetch fails
                        search_results.append({
                            "title": f"Search Result #{i + start_index + 1}",
                            "url": url,
                            "snippet": "No description available",
                            "source": self._extract_domain(url),
                            "date": "",
                            "type": "webpage"
                        })
                
                # Estimate total results (Google doesn't provide exact count)
                total_results = min(len(urls) * 10, 1000000)  # Cap at reasonable number
                
                logger.info(f"Found {len(search_results)} results for page {page}")
                return search_results, total_results
                
            except Exception as e:
                logger.error(f"Google search failed: {e}")
                # Fall back to simulation
                sim_provider = SimulationProvider(self.config)
                return await sim_provider.search(query, page, filters)
                
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return [], 0
    
    def _build_search_query(self, query: SearchQuery, filters: SearchFilter) -> str:
        """Build Google search query with filters"""
        search_terms = []
        
        # Add regular terms
        search_terms.extend(query.terms)
        
        # Add required terms
        for term in query.required_terms:
            search_terms.append(f'"{term}"')
        
        # Add exact phrases
        for phrase in query.exact_phrases:
            search_terms.append(f'"{phrase}"')
        
        # Add site filter
        if query.site_filter:
            search_terms.append(f"site:{query.site_filter}")
        
        # Add filetype filter
        if query.filetype_filter:
            search_terms.append(f"filetype:{query.filetype_filter}")
        
        # Add content type filters
        if filters.content_type == "pdf":
            search_terms.append("filetype:pdf")
        elif filters.content_type == "doc":
            search_terms.append("filetype:doc OR filetype:docx")
        elif filters.content_type == "news":
            search_terms.append("site:news.google.com OR site:reuters.com OR site:bbc.com")
        
        # Exclude terms
        for term in query.excluded_terms:
            search_terms.append(f"-{term}")
        
        return " ".join(search_terms)
    
    async def _fetch_result_metadata(self, url: str, index: int) -> Dict[str, Any]:
        """Fetch metadata for a search result URL"""
        try:
            # Use asyncio to run the blocking request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(url, timeout=5, allow_redirects=True)
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else f"Search Result #{index}"
                
                # Extract description from meta tags
                description = ""
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content', '')
                
                # If no meta description, try to get text from first paragraph
                if not description:
                    first_p = soup.find('p')
                    if first_p:
                        description = first_p.get_text()[:200] + "..."
                
                # Extract domain
                domain = self._extract_domain(url)
                
                # Determine content type
                content_type = self._determine_content_type(url, soup)
                
                return {
                    "title": title[:100],  # Limit title length
                    "url": url,
                    "snippet": description[:300] if description else "No description available",
                    "source": domain,
                    "date": "",  # Could extract from meta tags if available
                    "type": content_type
                }
            else:
                return None
                
        except Exception as e:
            logger.debug(f"Failed to fetch metadata for {url}: {e}")
            return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "Unknown"
    
    def _determine_content_type(self, url: str, soup: BeautifulSoup) -> str:
        """Determine content type from URL and content"""
        url_lower = url.lower()
        
        if url_lower.endswith('.pdf'):
            return "pdf"
        elif any(ext in url_lower for ext in ['.doc', '.docx']):
            return "doc"
        elif any(domain in url_lower for domain in ['news.', 'bbc.', 'reuters.', 'cnn.']):
            return "news"
        elif any(domain in url_lower for domain in ['youtube.', 'vimeo.']):
            return "video"
        else:
            return "webpage"
    
    async def get_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions (simplified)"""
        await asyncio.sleep(0.1)
        
        # Simple suggestion logic based on common patterns
        suggestions = [
            f"{partial_query} tutorial",
            f"{partial_query} guide",
            f"how to {partial_query}",
            f"{partial_query} examples",
            f"best {partial_query}"
        ]
        
        return suggestions[:5]


class SearchProviderManager:
    """Manages multiple search providers"""
    
    def __init__(self, config: Config):
        self.config = config
        self.providers = {
            "simulation": SimulationProvider(config),
            "google": GoogleSearchProvider(config)
        }
        # Default to Google if available, otherwise simulation
        if GOOGLE_AVAILABLE and config.api.default_provider == "google":
            self.default_provider = "google"
        elif GOOGLE_AVAILABLE and config.api.default_provider == "simulation":
            self.default_provider = "simulation"
        else:
            self.default_provider = "google" if GOOGLE_AVAILABLE else "simulation"
    
    async def search(self, query: SearchQuery, page: int, filters: SearchFilter) -> Tuple[List[Dict[str, Any]], int]:
        """Search using the default provider"""
        provider = self.providers.get(self.default_provider)
        if not provider:
            provider = self.providers["simulation"]
        
        return await provider.search(query, page, filters)
    
    async def get_suggestions(self, partial_query: str) -> List[str]:
        """Get suggestions from default provider"""
        provider = self.providers.get(self.default_provider)
        if not provider:
            provider = self.providers["simulation"]
        
        return await provider.get_suggestions(partial_query)
    
    async def get_trending(self) -> List[str]:
        """Get trending searches"""
        await asyncio.sleep(0.1)
        return [
            "Python programming",
            "Machine learning",
            "Web development",
            "Data science",
            "Artificial intelligence"
        ] 