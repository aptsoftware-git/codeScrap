"""
Content extraction service using BeautifulSoup for parsing HTML.
"""

from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from loguru import logger
import re


class ContentExtractor:
    """
    Extracts content from HTML using CSS selectors and fallback methods.
    """
    
    def __init__(self):
        """Initialize the content extractor."""
        self.parser = "lxml"  # Use lxml parser for better performance
    
    def extract_with_selectors(
        self,
        html: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Optional[str]]:
        """
        Extract content using provided CSS selectors.
        
        Args:
            html: Raw HTML content
            selectors: Dictionary mapping field names to CSS selectors
                      e.g., {'title': 'h1.article-title', 'content': 'div.article-body'}
        
        Returns:
            Dictionary with extracted content
        """
        try:
            soup = BeautifulSoup(html, self.parser)
            extracted = {}
            
            logger.debug(f"Extracting with selectors: {selectors}")
            
            for field, selector in selectors.items():
                try:
                    # Support multiple fallback selectors separated by commas
                    selector_list = [s.strip() for s in selector.split(',')]
                    elements = []
                    matched_selector = None
                    
                    # Try each selector until one matches
                    for sel in selector_list:
                        elements = soup.select(sel)
                        if elements:
                            matched_selector = sel
                            break
                    
                    if elements:
                        # Join text from all matching elements
                        text = ' '.join(el.get_text(strip=True) for el in elements)
                        extracted[field] = text if text else None
                        logger.debug(f"  {field}: Found {len(elements)} elements with '{matched_selector}', extracted {len(text) if text else 0} chars")
                    else:
                        extracted[field] = None
                        logger.debug(f"  {field}: No elements found for any selector in: {selector_list}")
                except Exception as e:
                    logger.warning(f"Error extracting field '{field}': {e}")
                    extracted[field] = None
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return {field: None for field in selectors.keys()}
    
    def extract_generic(self, html: str) -> Dict[str, Optional[str]]:
        """
        Generic content extraction when selectors are not available.
        Uses common HTML patterns to extract title and content.
        
        Args:
            html: Raw HTML content
        
        Returns:
            Dictionary with title and content
        """
        try:
            soup = BeautifulSoup(html, self.parser)
            extracted = {}
            
            # Extract title - try multiple common locations
            title = None
            for selector in ['h1', 'title', '.article-title', '.headline', 'h1.title']:
                elements = soup.select(selector)
                if elements:
                    title = elements[0].get_text(strip=True)
                    break
            extracted['title'] = title
            
            # Extract main content - try multiple common patterns
            content = None
            for selector in ['article', 'main', '.article-body', '.content', '[role="main"]']:
                elements = soup.select(selector)
                if elements:
                    # Get all paragraph text
                    paragraphs = elements[0].find_all('p')
                    if paragraphs:
                        content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                        break
            
            # Fallback: get all paragraphs
            if not content:
                all_paragraphs = soup.find_all('p')
                if all_paragraphs:
                    content = '\n\n'.join(p.get_text(strip=True) for p in all_paragraphs if p.get_text(strip=True))
            
            extracted['content'] = content
            
            # Extract date - try common patterns
            date = None
            for selector in ['time', '.published-date', '.date', '[datetime]']:
                elements = soup.select(selector)
                if elements:
                    date = elements[0].get_text(strip=True) or elements[0].get('datetime')
                    break
            extracted['date'] = date
            
            # Extract author
            author = None
            for selector in ['.author', '[rel="author"]', '.byline', '.author-name']:
                elements = soup.select(selector)
                if elements:
                    author = elements[0].get_text(strip=True)
                    break
            extracted['author'] = author
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error in generic extraction: {e}")
            return {'title': None, 'content': None, 'date': None, 'author': None}
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and normalizing.
        
        Args:
            text: Raw extracted text
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove common artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove [brackets]
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace again
        
        return text
    
    def extract_links(self, html: str, selector: str = 'a') -> List[str]:
        """
        Extract all links matching the selector.
        
        Args:
            html: Raw HTML content
            selector: CSS selector for links (default: 'a')
        
        Returns:
            List of URLs
        """
        try:
            soup = BeautifulSoup(html, self.parser)
            links = []
            
            for element in soup.select(selector):
                href = element.get('href')
                if href:
                    # Filter out javascript:, mailto:, tel:, etc.
                    if href.startswith(('http://', 'https://', '/')):
                        links.append(href)
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def is_valid_content(self, content: str, min_length: int = 100) -> bool:
        """
        Check if extracted content is valid and substantial.
        
        Args:
            content: Extracted content text
            min_length: Minimum required length
        
        Returns:
            True if content is valid
        """
        if not content:
            return False
        
        cleaned = self.clean_text(content)
        return len(cleaned) >= min_length
