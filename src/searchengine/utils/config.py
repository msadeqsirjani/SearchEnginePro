"""
SearchEngine Pro - Configuration Management

This module handles loading and managing configuration settings
from files and environment variables.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchConfig:
    """Search-related configuration"""
    results_per_page: int = 10
    default_timeout: int = 30
    max_retries: int = 3
    user_agent: str = "SearchEngine Pro/3.2"
    request_delay: float = 0.5


@dataclass
class DisplayConfig:
    """Display-related configuration"""
    colors: bool = True
    animations: bool = True
    unicode_symbols: bool = True
    max_snippet_length: int = 200
    show_metadata: bool = True


@dataclass
class CacheConfig:
    """Cache-related configuration"""
    enabled: bool = True
    search_ttl: int = 3600  # 1 hour
    max_size: int = 1000
    cleanup_interval: int = 300  # 5 minutes


@dataclass
class HistoryConfig:
    """History-related configuration"""
    max_entries: int = 1000
    save_to_file: bool = True
    auto_cleanup_days: int = 30


@dataclass
class APIConfig:
    """API-related configuration"""
    providers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    default_provider: str = "google"
    api_keys: Dict[str, str] = field(default_factory=dict)
    rate_limits: Dict[str, int] = field(default_factory=dict)


class Config:
    """
    Main configuration class that loads and manages all settings
    """
    
    def __init__(self):
        self.search = SearchConfig()
        self.display = DisplayConfig()
        self.cache = CacheConfig()
        self.history = HistoryConfig()
        self.api = APIConfig()
        
        # Paths
        self.config_dir = self._get_config_dir()
        self.data_dir = self._get_data_dir()
        self.cache_dir = self._get_cache_dir()
        
        # Create directories
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from file or create default
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            Config instance
        """
        config = cls()
        
        if config_path:
            config._load_from_file(config_path)
        else:
            # Try to load from default locations
            default_config_file = config.config_dir / "config.yaml"
            if default_config_file.exists():
                config._load_from_file(default_config_file)
            else:
                # Create default config file
                config._save_default_config(default_config_file)
        
        # Load environment variables
        config._load_from_env()
        
        return config
    
    def _get_config_dir(self) -> Path:
        """Get configuration directory path"""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData/Roaming'))
        else:  # Unix-like
            # Try XDG_CONFIG_HOME first, then fall back to .searchengine in home
            xdg_config = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
            try:
                # Test if we can write to the XDG config directory
                test_dir = xdg_config / 'searchengine'
                test_dir.mkdir(parents=True, exist_ok=True)
                base_dir = xdg_config
            except (PermissionError, OSError):
                # Fall back to .searchengine in home directory
                base_dir = Path.home()
                return base_dir / '.searchengine'
        
        return base_dir / 'searchengine'
    
    def _get_data_dir(self) -> Path:
        """Get data directory path"""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local'))
        else:  # Unix-like
            xdg_data = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
            try:
                # Test if we can write to the XDG data directory
                test_dir = xdg_data / 'searchengine'
                test_dir.mkdir(parents=True, exist_ok=True)
                base_dir = xdg_data
            except (PermissionError, OSError):
                # Fall back to .searchengine/data in home directory
                base_dir = Path.home()
                return base_dir / '.searchengine' / 'data'
        
        return base_dir / 'searchengine'
    
    def _get_cache_dir(self) -> Path:
        """Get cache directory path"""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('TEMP', Path.home() / 'AppData/Local/Temp'))
        else:  # Unix-like
            xdg_cache = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
            try:
                # Test if we can write to the XDG cache directory
                test_dir = xdg_cache / 'searchengine'
                test_dir.mkdir(parents=True, exist_ok=True)
                base_dir = xdg_cache
            except (PermissionError, OSError):
                # Fall back to .searchengine/cache in home directory
                base_dir = Path.home()
                return base_dir / '.searchengine' / 'cache'
        
        return base_dir / 'searchengine'
    
    def _load_from_file(self, config_file: Path):
        """Load configuration from file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            self._apply_config_data(data)
            logger.info(f"Configuration loaded from {config_file}")
            
        except Exception as e:
            logger.warning(f"Failed to load configuration from {config_file}: {e}")
    
    def _apply_config_data(self, data: Dict[str, Any]):
        """Apply configuration data to config objects"""
        if 'search' in data:
            search_data = data['search']
            self.search.results_per_page = search_data.get('results_per_page', self.search.results_per_page)
            self.search.default_timeout = search_data.get('default_timeout', self.search.default_timeout)
            self.search.max_retries = search_data.get('max_retries', self.search.max_retries)
            self.search.user_agent = search_data.get('user_agent', self.search.user_agent)
            self.search.request_delay = search_data.get('request_delay', self.search.request_delay)
        
        if 'display' in data:
            display_data = data['display']
            self.display.colors = display_data.get('colors', self.display.colors)
            self.display.animations = display_data.get('animations', self.display.animations)
            self.display.unicode_symbols = display_data.get('unicode_symbols', self.display.unicode_symbols)
            self.display.max_snippet_length = display_data.get('max_snippet_length', self.display.max_snippet_length)
            self.display.show_metadata = display_data.get('show_metadata', self.display.show_metadata)
        
        if 'cache' in data:
            cache_data = data['cache']
            self.cache.enabled = cache_data.get('enabled', self.cache.enabled)
            self.cache.search_ttl = cache_data.get('search_ttl', self.cache.search_ttl)
            self.cache.max_size = cache_data.get('max_size', self.cache.max_size)
            self.cache.cleanup_interval = cache_data.get('cleanup_interval', self.cache.cleanup_interval)
        
        if 'history' in data:
            history_data = data['history']
            self.history.max_entries = history_data.get('max_entries', self.history.max_entries)
            self.history.save_to_file = history_data.get('save_to_file', self.history.save_to_file)
            self.history.auto_cleanup_days = history_data.get('auto_cleanup_days', self.history.auto_cleanup_days)
        
        if 'api' in data:
            api_data = data['api']
            self.api.providers = api_data.get('providers', self.api.providers)
            self.api.default_provider = api_data.get('default_provider', self.api.default_provider)
            self.api.api_keys = api_data.get('api_keys', self.api.api_keys)
            self.api.rate_limits = api_data.get('rate_limits', self.api.rate_limits)
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Search configuration
        if 'SEARCHENGINE_RESULTS_PER_PAGE' in os.environ:
            self.search.results_per_page = int(os.environ['SEARCHENGINE_RESULTS_PER_PAGE'])
        
        if 'SEARCHENGINE_TIMEOUT' in os.environ:
            self.search.default_timeout = int(os.environ['SEARCHENGINE_TIMEOUT'])
        
        if 'SEARCHENGINE_USER_AGENT' in os.environ:
            self.search.user_agent = os.environ['SEARCHENGINE_USER_AGENT']
        
        # Display configuration
        if 'SEARCHENGINE_NO_COLORS' in os.environ:
            self.display.colors = False
        
        if 'SEARCHENGINE_NO_ANIMATIONS' in os.environ:
            self.display.animations = False
        
        # API configuration
        if 'SEARCHENGINE_DEFAULT_PROVIDER' in os.environ:
            self.api.default_provider = os.environ['SEARCHENGINE_DEFAULT_PROVIDER']
        
        # Load API keys from environment
        for key, value in os.environ.items():
            if key.startswith('SEARCHENGINE_API_KEY_'):
                provider_name = key.replace('SEARCHENGINE_API_KEY_', '').lower()
                self.api.api_keys[provider_name] = value
    
    def _save_default_config(self, config_file: Path):
        """Save default configuration to file"""
        try:
            default_config = {
                'search': {
                    'results_per_page': self.search.results_per_page,
                    'default_timeout': self.search.default_timeout,
                    'max_retries': self.search.max_retries,
                    'user_agent': self.search.user_agent,
                    'request_delay': self.search.request_delay
                },
                'display': {
                    'colors': self.display.colors,
                    'animations': self.display.animations,
                    'unicode_symbols': self.display.unicode_symbols,
                    'max_snippet_length': self.display.max_snippet_length,
                    'show_metadata': self.display.show_metadata
                },
                'cache': {
                    'enabled': self.cache.enabled,
                    'search_ttl': self.cache.search_ttl,
                    'max_size': self.cache.max_size,
                    'cleanup_interval': self.cache.cleanup_interval
                },
                'history': {
                    'max_entries': self.history.max_entries,
                    'save_to_file': self.history.save_to_file,
                    'auto_cleanup_days': self.history.auto_cleanup_days
                },
                'api': {
                    'default_provider': "google",
                    'providers': {},
                    'api_keys': {},
                    'rate_limits': {}
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Default configuration saved to {config_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save default configuration: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'search': {
                'results_per_page': self.search.results_per_page,
                'default_timeout': self.search.default_timeout,
                'max_retries': self.search.max_retries,
                'user_agent': self.search.user_agent,
                'request_delay': self.search.request_delay
            },
            'display': {
                'colors': self.display.colors,
                'animations': self.display.animations,
                'unicode_symbols': self.display.unicode_symbols,
                'max_snippet_length': self.display.max_snippet_length,
                'show_metadata': self.display.show_metadata
            },
            'cache': {
                'enabled': self.cache.enabled,
                'search_ttl': self.cache.search_ttl,
                'max_size': self.cache.max_size,
                'cleanup_interval': self.cache.cleanup_interval
            },
            'history': {
                'max_entries': self.history.max_entries,
                'save_to_file': self.history.save_to_file,
                'auto_cleanup_days': self.history.auto_cleanup_days
            },
            'api': {
                'default_provider': self.api.default_provider,
                'providers': self.api.providers,
                'api_keys': self.api.api_keys,
                'rate_limits': self.api.rate_limits
            }
        } 