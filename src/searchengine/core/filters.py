"""
SearchEngine Pro - Filter Manager

This module handles search filtering logic including filter validation,
application, and management of filter states.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .models import SearchFilter, SafeSearchLevel

logger = logging.getLogger(__name__)


class FilterManager:
    """
    Manages search filters and their application
    
    This class handles the validation, application, and management of
    search filters including date ranges, content types, and other
    filtering criteria.
    """
    
    def __init__(self):
        """Initialize the filter manager"""
        self.active_filters = SearchFilter()
        self.filter_presets = self._create_default_presets()
        
    def _create_default_presets(self) -> Dict[str, SearchFilter]:
        """Create default filter presets"""
        return {
            "default": SearchFilter(),
            "recent": SearchFilter(date_range="week"),
            "images": SearchFilter(content_type="image"),
            "news": SearchFilter(content_type="news", date_range="week"),
            "pdfs": SearchFilter(content_type="pdf"),
            "academic": SearchFilter(content_type="any", custom_filters={"academic": True}),
            "safe": SearchFilter(safe_search=SafeSearchLevel.STRICT),
            "local": SearchFilter(region="us", language="en")
        }
    
    def apply_filters(self, filters: SearchFilter) -> bool:
        """
        Apply search filters
        
        Args:
            filters: SearchFilter object to apply
            
        Returns:
            True if filters were applied successfully
        """
        try:
            # Validate filters
            self.validate_filters(filters)
            
            # Apply filters
            self.active_filters = filters
            
            logger.info(f"Applied filters: {filters.to_dict()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply filters: {e}")
            return False
    
    def validate_filters(self, filters: SearchFilter) -> bool:
        """
        Validate filter values
        
        Args:
            filters: SearchFilter object to validate
            
        Returns:
            True if filters are valid
            
        Raises:
            ValueError: If filters are invalid
        """
        # Date range validation
        valid_date_ranges = ["any", "day", "week", "month", "year", "custom"]
        if filters.date_range not in valid_date_ranges:
            raise ValueError(f"Invalid date range: {filters.date_range}")
        
        # Content type validation
        valid_content_types = ["any", "webpage", "image", "video", "news", "pdf", "doc"]
        if filters.content_type not in valid_content_types:
            raise ValueError(f"Invalid content type: {filters.content_type}")
        
        # Language validation (basic check)
        if filters.language != "any" and len(filters.language) not in [2, 5]:
            raise ValueError(f"Invalid language code: {filters.language}")
        
        # Region validation (basic check)
        if filters.region != "any" and len(filters.region) != 2:
            raise ValueError(f"Invalid region code: {filters.region}")
        
        return True
    
    def get_filter_query_params(self, filters: SearchFilter) -> Dict[str, Any]:
        """
        Convert filters to query parameters for search APIs
        
        Args:
            filters: SearchFilter object
            
        Returns:
            Dictionary of query parameters
        """
        params = {}
        
        # Date range handling
        if filters.date_range != "any":
            date_mapping = {
                "day": timedelta(days=1),
                "week": timedelta(weeks=1),
                "month": timedelta(days=30),
                "year": timedelta(days=365)
            }
            
            if filters.date_range in date_mapping:
                since_date = datetime.now() - date_mapping[filters.date_range]
                params["since"] = since_date.isoformat()
        
        # Content type handling
        if filters.content_type != "any":
            if filters.content_type == "pdf":
                params["filetype"] = "pdf"
            elif filters.content_type == "doc":
                params["filetype"] = "doc"
            elif filters.content_type == "image":
                params["type"] = "image"
            elif filters.content_type == "video":
                params["type"] = "video"
            elif filters.content_type == "news":
                params["type"] = "news"
        
        # Language handling
        if filters.language != "any":
            params["lang"] = filters.language
        
        # Region handling
        if filters.region != "any":
            params["region"] = filters.region
        
        # Safe search handling
        if filters.safe_search != SafeSearchLevel.MODERATE:
            params["safe"] = filters.safe_search.value
        
        # Custom filters
        params.update(filters.custom_filters)
        
        return params
    
    def create_filter_from_params(self, **kwargs) -> SearchFilter:
        """
        Create a SearchFilter from keyword arguments
        
        Args:
            **kwargs: Filter parameters
            
        Returns:
            SearchFilter object
        """
        return SearchFilter(
            date_range=kwargs.get("date_range", "any"),
            content_type=kwargs.get("content_type", "any"),
            language=kwargs.get("language", "any"),
            region=kwargs.get("region", "any"),
            safe_search=SafeSearchLevel(kwargs.get("safe_search", "moderate")),
            custom_filters=kwargs.get("custom_filters", {})
        )
    
    def get_preset_filter(self, preset_name: str) -> Optional[SearchFilter]:
        """
        Get a preset filter configuration
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            SearchFilter object or None if preset not found
        """
        return self.filter_presets.get(preset_name)
    
    def add_preset_filter(self, name: str, filters: SearchFilter):
        """
        Add a new preset filter
        
        Args:
            name: Name for the preset
            filters: SearchFilter object
        """
        self.filter_presets[name] = filters
        logger.info(f"Added filter preset: {name}")
    
    def list_preset_filters(self) -> List[str]:
        """
        Get list of available preset filter names
        
        Returns:
            List of preset names
        """
        return list(self.filter_presets.keys())
    
    def clear_filters(self):
        """Reset filters to default state"""
        self.active_filters = SearchFilter()
        logger.info("Filters cleared to default state")
    
    def get_active_filters(self) -> SearchFilter:
        """
        Get currently active filters
        
        Returns:
            Current SearchFilter object
        """
        return self.active_filters
    
    def is_filters_active(self) -> bool:
        """
        Check if any filters are currently active
        
        Returns:
            True if filters are active
        """
        return self.active_filters.is_active()
    
    def get_filter_summary(self) -> str:
        """
        Get a human-readable summary of active filters
        
        Returns:
            String description of active filters
        """
        if not self.is_filters_active():
            return "No filters active"
        
        summary_parts = []
        
        if self.active_filters.date_range != "any":
            summary_parts.append(f"Date: {self.active_filters.date_range}")
        
        if self.active_filters.content_type != "any":
            summary_parts.append(f"Type: {self.active_filters.content_type}")
        
        if self.active_filters.language != "any":
            summary_parts.append(f"Language: {self.active_filters.language}")
        
        if self.active_filters.region != "any":
            summary_parts.append(f"Region: {self.active_filters.region}")
        
        if self.active_filters.safe_search != SafeSearchLevel.MODERATE:
            summary_parts.append(f"Safe search: {self.active_filters.safe_search.value}")
        
        if self.active_filters.custom_filters:
            custom_parts = [f"{k}: {v}" for k, v in self.active_filters.custom_filters.items()]
            summary_parts.extend(custom_parts)
        
        return ", ".join(summary_parts)
    
    def merge_filters(self, base_filters: SearchFilter, override_filters: SearchFilter) -> SearchFilter:
        """
        Merge two filter objects, with override taking precedence
        
        Args:
            base_filters: Base filter settings
            override_filters: Override filter settings
            
        Returns:
            Merged SearchFilter object
        """
        merged_custom = {**base_filters.custom_filters, **override_filters.custom_filters}
        
        return SearchFilter(
            date_range=override_filters.date_range if override_filters.date_range != "any" else base_filters.date_range,
            content_type=override_filters.content_type if override_filters.content_type != "any" else base_filters.content_type,
            language=override_filters.language if override_filters.language != "any" else base_filters.language,
            region=override_filters.region if override_filters.region != "any" else base_filters.region,
            safe_search=override_filters.safe_search if override_filters.safe_search != SafeSearchLevel.MODERATE else base_filters.safe_search,
            custom_filters=merged_custom
        )
    
    def filter_results_post_search(self, results: List[Dict[str, Any]], filters: SearchFilter) -> List[Dict[str, Any]]:
        """
        Apply additional filtering to search results after retrieval
        
        Args:
            results: List of search result dictionaries
            filters: Filters to apply
            
        Returns:
            Filtered list of results
        """
        if not filters.is_active():
            return results
        
        filtered_results = []
        
        for result in results:
            # Apply custom filtering logic
            if self._result_matches_filters(result, filters):
                filtered_results.append(result)
        
        return filtered_results
    
    def _result_matches_filters(self, result: Dict[str, Any], filters: SearchFilter) -> bool:
        """
        Check if a single result matches the given filters
        
        Args:
            result: Search result dictionary
            filters: Filters to check against
            
        Returns:
            True if result matches filters
        """
        # Check content type
        if filters.content_type != "any":
            result_type = result.get("type", "webpage")
            if filters.content_type != result_type:
                return False
        
        # Check date range (if date is available)
        if filters.date_range != "any" and result.get("date"):
            try:
                result_date = datetime.fromisoformat(result["date"])
                cutoff_date = self._get_date_cutoff(filters.date_range)
                if result_date < cutoff_date:
                    return False
            except (ValueError, TypeError):
                pass  # Skip date filtering if date parsing fails
        
        # Check custom filters
        for key, value in filters.custom_filters.items():
            if key in result:
                if result[key] != value:
                    return False
        
        return True
    
    def _get_date_cutoff(self, date_range: str) -> datetime:
        """
        Get the cutoff date for a given date range
        
        Args:
            date_range: Date range string
            
        Returns:
            Cutoff datetime
        """
        now = datetime.now()
        
        if date_range == "day":
            return now - timedelta(days=1)
        elif date_range == "week":
            return now - timedelta(weeks=1)
        elif date_range == "month":
            return now - timedelta(days=30)
        elif date_range == "year":
            return now - timedelta(days=365)
        else:
            return datetime.min  # No cutoff for unknown ranges 