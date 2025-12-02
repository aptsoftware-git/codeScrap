"""
Scraper manager for async web scraping with retry logic and rate limiting.
"""

import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime
from loguru import logger

from app.models import SourceConfig, ArticleContent
from app.utils.rate_limiter import rate_limiter
from app.utils.robots_checker import robots_checker
from app.services.content_extractor import ContentExtractor
from app.settings import settings


class ScraperManager:
    """
    Manages web scraping operations with async support, retries, and rate limiting.
    """
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        follow_redirects: bool = True
    ):
        """
        Initialize the scraper manager.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            follow_redirects: Whether to follow HTTP redirects
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.follow_redirects = follow_redirects
        self.content_extractor = ContentExtractor()
        
        # Default headers to appear as a browser
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc
    
    def _merge_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Merge custom headers with defaults."""
        headers = self.default_headers.copy()
        if custom_headers:
            headers.update(custom_headers)
        return headers
    
    async def fetch_url(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        rate_limit: float = 1.0,
        respect_robots: Optional[bool] = None
    ) -> Optional[str]:
        """
        Fetch content from a URL with retry logic, rate limiting, and robots.txt compliance.
        
        Args:
            url: URL to fetch
            headers: Optional custom headers
            rate_limit: Minimum delay between requests to this domain
            respect_robots: Whether to respect robots.txt (default: use settings.scraper_respect_robots)
        
        Returns:
            HTML content or None if failed
        """
        # Use setting if not explicitly specified
        if respect_robots is None:
            respect_robots = settings.scraper_respect_robots
        
        # Check robots.txt compliance
        if respect_robots and not robots_checker.can_fetch(url):
            logger.warning(f"Skipping {url} - disallowed by robots.txt")
            return None
        
        # Get crawl delay from robots.txt if specified
        if respect_robots:
            robots_delay = robots_checker.get_crawl_delay(url)
            if robots_delay and robots_delay > rate_limit:
                logger.debug(f"Using robots.txt crawl delay of {robots_delay}s instead of {rate_limit}s")
                rate_limit = robots_delay
        
        domain = self._get_domain(url)
        merged_headers = self._merge_headers(headers)
        
        # Apply rate limiting
        await rate_limiter.wait_if_needed(domain, rate_limit)
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=self.follow_redirects
                ) as client:
                    logger.debug(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                    response = await client.get(url, headers=merged_headers)
                    response.raise_for_status()
                    
                    logger.info(f"Successfully fetched {url} ({len(response.text)} chars)")
                    return response.text
                    
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error {e.response.status_code} for {url}")
                if e.response.status_code in [404, 403, 401]:
                    # Don't retry on client errors
                    return None
            except httpx.TimeoutException:
                logger.warning(f"Timeout fetching {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
            
            # Wait before retrying (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = (2 ** attempt) * rate_limit
                logger.debug(f"Waiting {wait_time:.2f}s before retry")
                import asyncio
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None
    
    async def scrape_article(
        self,
        url: str,
        source_config: SourceConfig
    ) -> Optional[ArticleContent]:
        """
        Scrape a single article using source configuration.
        
        Args:
            url: Article URL
            source_config: Source configuration with selectors
        
        Returns:
            ArticleContent object or None if failed
        """
        try:
            # Make URL absolute if relative
            if url.startswith('/'):
                url = urljoin(source_config.base_url, url)
            
            # Fetch HTML
            html = await self.fetch_url(
                url,
                headers=source_config.headers,
                rate_limit=source_config.rate_limit
            )
            
            if not html:
                return None
            
            # Extract content using selectors
            if source_config.selectors:
                extracted = self.content_extractor.extract_with_selectors(
                    html,
                    source_config.selectors
                )
            else:
                # Fallback to generic extraction
                extracted = self.content_extractor.extract_generic(html)
            
            # Clean the content
            title = self.content_extractor.clean_text(extracted.get('title', ''))
            content = self.content_extractor.clean_text(extracted.get('content', ''))
            
            # Validate content
            if not self.content_extractor.is_valid_content(content):
                logger.warning(
                    f"Invalid or insufficient content from {url} "
                    f"(title_len={len(title) if title else 0}, "
                    f"content_len={len(content) if content else 0}, "
                    f"extracted_fields={list(extracted.keys())})"
                )
                return None
            
            # Create ArticleContent object
            article = ArticleContent(
                url=url,
                title=title or "Untitled",
                content=content,
                author=extracted.get('author'),
                source_name=source_config.name
            )
            
            logger.info(f"Successfully scraped article from {url}")
            return article
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None
    
    async def scrape_search_results(
        self,
        source_config: SourceConfig,
        query: str,
        max_articles: int = 10
    ) -> List[ArticleContent]:
        """
        Scrape articles from search results.
        
        Args:
            source_config: Source configuration
            query: Search query
            max_articles: Maximum number of articles to scrape
        
        Returns:
            List of ArticleContent objects
        """
        articles = []
        
        try:
            # Build search URL
            if not source_config.search_url_template:
                logger.warning(f"No search URL template for {source_config.name}")
                return articles
            
            search_url = source_config.search_url_template.format(query=query)
            
            # Fetch search results page
            html = await self.fetch_url(
                search_url,
                headers=source_config.headers,
                rate_limit=source_config.rate_limit
            )
            
            if not html:
                return articles
            
            # Extract article links
            link_selector = source_config.selectors.get('article_links', 'a')
            article_links = self.content_extractor.extract_links(html, link_selector)
            
            logger.info(f"Found {len(article_links)} article links from {source_config.name}")
            
            # Scrape each article (up to max_articles)
            for link in article_links[:max_articles]:
                article = await self.scrape_article(link, source_config)
                if article:
                    articles.append(article)
                
                # Stop if we have enough articles
                if len(articles) >= max_articles:
                    break
            
            logger.info(f"Scraped {len(articles)} articles from {source_config.name}")
            
        except Exception as e:
            logger.error(f"Error scraping search results from {source_config.name}: {e}")
        
        return articles
    
    async def scrape_sources(
        self,
        sources: List[SourceConfig],
        query: str,
        max_articles_per_source: int = 10
    ) -> List[ArticleContent]:
        """
        Scrape articles from multiple sources.
        
        Args:
            sources: List of source configurations
            query: Search query
            max_articles_per_source: Max articles to get from each source
        
        Returns:
            Combined list of ArticleContent objects
        """
        all_articles = []
        
        logger.info(f"Starting scraping from {len(sources)} sources for query: '{query}'")
        
        for source in sources:
            if not source.enabled:
                logger.debug(f"Skipping disabled source: {source.name}")
                continue
            
            try:
                articles = await self.scrape_search_results(
                    source,
                    query,
                    max_articles_per_source
                )
                all_articles.extend(articles)
                logger.info(f"Got {len(articles)} articles from {source.name}")
                
            except Exception as e:
                logger.error(f"Error scraping {source.name}: {e}")
                continue
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles


# Global scraper manager instance
scraper_manager = ScraperManager()
