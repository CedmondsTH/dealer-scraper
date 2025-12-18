"""
Strategy caching system for AI-guided scraping.

This module provides caching capabilities for scraping strategies,
allowing the system to remember successful extraction patterns for
specific domains and avoid redundant AI analysis calls.
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
from utils.logging import logger


class StrategyCache:
    """
    Manages caching of scraping strategies by domain.
    
    Strategies are stored as JSON and include:
    - CSS selectors for extraction
    - Confidence scores
    - Last successful use timestamp
    - Success count
    """
    
    def __init__(self, cache_file: str = "data/strategy_cache.json"):
        """
        Initialize the strategy cache.
        
        Args:
            cache_file: Path to the JSON cache file
        """
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._ensure_cache_directory()
        self._load_cache()
    
    def _ensure_cache_directory(self):
        """Ensure the cache directory exists."""
        cache_dir = os.path.dirname(self.cache_file)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            logger.debug(f"Created cache directory: {cache_dir}")
    
    def _load_cache(self):
        """Load cache from disk."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache)} cached strategies")
            else:
                logger.debug("No existing cache file found, starting fresh")
                self.cache = {}
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug(f"Saved {len(self.cache)} strategies to cache")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _get_domain_key(self, url: str) -> str:
        """
        Extract domain key from URL for caching.
        
        Args:
            url: Full URL
            
        Returns:
            Domain key (e.g., "example.com")
        """
        try:
            parsed = urlparse(url)
            # Use domain without www prefix for consistency
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            logger.warning(f"Failed to parse URL {url}: {e}")
            return url.lower()
    
    def get_strategy(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached strategy for a URL's domain.
        
        Args:
            url: URL to look up
            
        Returns:
            Strategy dict if found, None otherwise
        """
        domain = self._get_domain_key(url)
        strategy = self.cache.get(domain)
        
        if strategy:
            logger.info(f"Found cached strategy for {domain}")
            return strategy.copy()
        else:
            logger.debug(f"No cached strategy for {domain}")
            return None
    
    def save_strategy(self, url: str, strategy: Dict[str, Any], 
                     success: bool = True):
        """
        Save or update a strategy for a URL's domain.
        
        Args:
            url: URL the strategy was used for
            strategy: Strategy dictionary containing selectors and metadata
            success: Whether the strategy was successful
        """
        domain = self._get_domain_key(url)
        
        # Get existing entry or create new one
        entry = self.cache.get(domain, {
            'strategy': {},
            'success_count': 0,
            'failure_count': 0,
            'first_seen': datetime.now().isoformat(),
            'last_used': None,
            'last_success': None
        })
        
        # Update strategy
        entry['strategy'] = strategy
        entry['last_used'] = datetime.now().isoformat()
        
        # Update success/failure counts
        if success:
            entry['success_count'] = entry.get('success_count', 0) + 1
            entry['last_success'] = datetime.now().isoformat()
            logger.info(f"Saved successful strategy for {domain} "
                       f"(success count: {entry['success_count']})")
        else:
            entry['failure_count'] = entry.get('failure_count', 0) + 1
            logger.warning(f"Recorded strategy failure for {domain} "
                          f"(failure count: {entry['failure_count']})")
        
        # Save to cache
        self.cache[domain] = entry
        self._save_cache()
    
    def invalidate_strategy(self, url: str):
        """
        Remove a strategy from the cache.
        
        Args:
            url: URL whose strategy should be invalidated
        """
        domain = self._get_domain_key(url)
        if domain in self.cache:
            del self.cache[domain]
            self._save_cache()
            logger.info(f"Invalidated strategy for {domain}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_strategies = len(self.cache)
        total_successes = sum(entry.get('success_count', 0) 
                             for entry in self.cache.values())
        total_failures = sum(entry.get('failure_count', 0) 
                            for entry in self.cache.values())
        
        return {
            'total_strategies': total_strategies,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'domains': list(self.cache.keys())
        }
    
    def clear_cache(self):
        """Clear all cached strategies."""
        self.cache = {}
        self._save_cache()
        logger.info("Cleared all cached strategies")


# Global cache instance
strategy_cache = StrategyCache()

