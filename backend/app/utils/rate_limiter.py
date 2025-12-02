"""
Rate limiter utility for controlling request frequency to different domains.
"""

import time
from typing import Dict
from asyncio import Lock
from loguru import logger


class RateLimiter:
    """
    Per-domain rate limiter to prevent overwhelming web servers.
    """
    
    def __init__(self):
        """Initialize the rate limiter."""
        self._last_request_time: Dict[str, float] = {}
        self._locks: Dict[str, Lock] = {}
    
    def _get_lock(self, domain: str) -> Lock:
        """Get or create a lock for the specified domain."""
        if domain not in self._locks:
            self._locks[domain] = Lock()
        return self._locks[domain]
    
    async def wait_if_needed(self, domain: str, min_delay: float = 1.0):
        """
        Wait if necessary to respect rate limit for the domain.
        
        Args:
            domain: Domain name (e.g., 'bbc.com')
            min_delay: Minimum seconds between requests to this domain
        """
        lock = self._get_lock(domain)
        
        async with lock:
            current_time = time.time()
            last_time = self._last_request_time.get(domain, 0)
            time_since_last = current_time - last_time
            
            if time_since_last < min_delay:
                wait_time = min_delay - time_since_last
                logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
                time.sleep(wait_time)  # Using sync sleep as we're in async lock
            
            self._last_request_time[domain] = time.time()
    
    def reset(self, domain: str = None):
        """
        Reset rate limiter for specific domain or all domains.
        
        Args:
            domain: Domain to reset, or None to reset all
        """
        if domain:
            self._last_request_time.pop(domain, None)
            logger.debug(f"Reset rate limiter for {domain}")
        else:
            self._last_request_time.clear()
            logger.debug("Reset rate limiter for all domains")
    
    def get_stats(self) -> Dict[str, float]:
        """
        Get statistics about rate limiting.
        
        Returns:
            Dictionary mapping domain to last request time
        """
        return self._last_request_time.copy()


# Global rate limiter instance
rate_limiter = RateLimiter()
