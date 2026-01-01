# =============================================================================
# PROFILE PARSER
# =============================================================================
# Generic profile parser base class for extracting structured data from HTML.
# =============================================================================

"""
Profile Parser

Base class for platform-specific HTML parsers. Uses BeautifulSoup to
extract profile information from collected HTML.

Common fields extracted:
- name
- username
- bio/description
- follower/following counts
- job titles
- locations
- external URLs
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# PROFILE PARSER CLASS
# =============================================================================

class ProfileParser(ABC):
    """
    Base class for profile HTML parsers.
    
    Provides common utilities for parsing HTML and extracting data.
    """
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """
        Get the platform name.
        
        Returns:
            Platform name (lowercase)
        """
        pass
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML string into BeautifulSoup object.
        
        Args:
            html: HTML content as string
        
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')
    
    def extract_meta_content(self, soup: BeautifulSoup, property_name: str) -> Optional[str]:
        """
        Extract content from Open Graph meta tags.
        
        Args:
            soup: BeautifulSoup object
            property_name: Meta property name (e.g., "og:title")
        
        Returns:
            Content string or None
        """
        tag = soup.find('meta', property=property_name) or soup.find('meta', attrs={'name': property_name})
        if tag and tag.get('content'):
            return tag['content'].strip()
        return None
    
    def extract_text_by_selector(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """
        Extract text using CSS selector.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector
        
        Returns:
            Text content or None
        """
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
        return None
    
    def extract_all_text_by_selector(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """
        Extract text from all elements matching selector.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector
        
        Returns:
            List of text content
        """
        elements = soup.select(selector)
        return [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
    
    def extract_number_from_text(self, text: str) -> Optional[int]:
        """
        Extract number from text (e.g., "1.2K followers" -> 1200).
        
        Args:
            text: Text containing number
        
        Returns:
            Extracted number or None
        """
        if not text:
            return None
        
        # Remove commas and spaces
        text = text.replace(',', '').replace(' ', '').lower()
        
        # Handle K, M, B suffixes
        multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if suffix in text:
                try:
                    number = float(re.findall(r'[\d.]+', text)[0])
                    return int(number * multiplier)
                except (IndexError, ValueError):
                    pass
        
        # Try to extract plain number
        try:
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
        except ValueError:
            pass
        
        return None
    
    def extract_urls(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract all URLs from links in the HTML.
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            List of URLs
        """
        links = soup.find_all('a', href=True)
        urls = []
        
        for link in links:
            href = link['href']
            # Filter out internal navigation links
            if href.startswith('http'):
                urls.append(href)
        
        return list(set(urls))  # Deduplicate
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract URLs from plain text (e.g., from bio).
        
        Args:
            text: Text containing URLs
        
        Returns:
            List of extracted URLs
        """
        if not text:
            return []
        
        # URL pattern - matches http://, https://, and bare domains
        url_pattern = r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?'
        urls = re.findall(url_pattern, text)
        
        # Clean up URLs (remove trailing punctuation)
        cleaned_urls = []
        for url in urls:
            url = url.rstrip('.,;:!?)')
            if not url.startswith('http'):
                url = 'https://' + url
            cleaned_urls.append(url)
        
        return list(set(cleaned_urls))  # Deduplicate
    
    @abstractmethod
    def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse HTML and extract profile data.
        
        Must be implemented by each platform parser.
        
        Args:
            html: HTML content as string
        
        Returns:
            Dict with extracted profile data:
            {
                "platform": str,
                "name": str,
                "username": str,
                "bio": str,
                "followers": int,
                "following": int,
                "location": str,
                "urls": List[str],
                "job_title": str,
                "metadata": Dict[str, Any]
            }
        """
        pass
