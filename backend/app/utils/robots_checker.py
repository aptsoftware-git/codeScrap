"""
Robots.txt checker utility for ensuring compliance with website policies.
"""

import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict, Optional
from loguru import logger
from datetime import datetime, timedelta


class RobotsChecker:
    """
    Check robots.txt compliance for URLs before scraping.
    Caches robots.txt files to minimize requests.
    """
    
    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", cache_duration: int = 3600):
        """
        Initialize the robots.txt checker.
        
        Args:
            user_agent: User agent string to check permissions for (default: browser-like)
            cache_duration: How long to cache robots.txt files (seconds)
        """
        self.user_agent = user_agent
        self.cache_duration = cache_duration
        self._cache: Dict[str, tuple[urllib.robotparser.RobotFileParser, datetime]] = {}
    
    def _get_robots_url(self, url: str) -> str:
        """Get the robots.txt URL for a given website URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc
    
    def _get_parser(self, url: str) -> Optional[urllib.robotparser.RobotFileParser]:
        """
        Get robots.txt parser for the domain, using cache if available.
        
        Args:
            url: URL to get parser for
        
        Returns:
            RobotFileParser or None if robots.txt cannot be fetched
        """
        domain = self._get_domain(url)
        current_time = datetime.now()
        
        # Check cache
        if domain in self._cache:
            parser, cached_time = self._cache[domain]
            if current_time - cached_time < timedelta(seconds=self.cache_duration):
                return parser
        
        # Fetch new robots.txt
        robots_url = self._get_robots_url(url)
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)
        
        try:
            parser.read()
            self._cache[domain] = (parser, current_time)
            logger.debug(f"Fetched and cached robots.txt from {robots_url}")
            return parser
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt from {robots_url}: {e}")
            # Cache a permissive parser to avoid repeated failures
            parser.allow_all = True
            self._cache[domain] = (parser, current_time)
            return parser
    
    def can_fetch(self, url: str) -> bool:
        """
        Check if the URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
        
        Returns:
            True if fetching is allowed, False otherwise
        """
        parser = self._get_parser(url)
        if parser is None:
            # If we can't get robots.txt, assume it's okay (permissive approach)
            logger.debug(f"No robots.txt parser available for {url}, allowing fetch")
            return True
        
        allowed = parser.can_fetch(self.user_agent, url)
        
        if not allowed:
            logger.warning(f"robots.txt disallows fetching {url} for user agent {self.user_agent}")
        else:
            logger.debug(f"robots.txt allows fetching {url}")
        
        return allowed
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get the crawl delay specified in robots.txt for this domain.
        
        Args:
            url: URL to check
        
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        parser = self._get_parser(url)
        if parser is None:
            return None
        
        try:
            delay = parser.crawl_delay(self.user_agent)
            if delay:
                logger.debug(f"robots.txt specifies crawl delay of {delay}s for {self._get_domain(url)}")
            return delay
        except Exception:
            return None
    
    def clear_cache(self, domain: Optional[str] = None):
        """
        Clear the robots.txt cache.
        
        Args:
            domain: Specific domain to clear, or None to clear all
        """
        if domain:
            self._cache.pop(domain, None)
            logger.debug(f"Cleared robots.txt cache for {domain}")
        else:
            self._cache.clear()
            logger.debug("Cleared all robots.txt cache")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the cache."""
        return {
            "cached_domains": len(self._cache),
            "cache_duration": self.cache_duration
        }


# Global robots checker instance
robots_checker = RobotsChecker()
