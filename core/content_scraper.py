"""
Content Scraper Module
Fetches and extracts content from URLs, especially optimized for Gcore articles
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, urljoin

class ContentScraper:
    """Scrape and extract content from web pages"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        self.headers = {
            'User-Agent': self.user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        # Common content selectors for different sites
        self.content_selectors = {
            'gcore.com': {
                'title': ['h1', 'title'],
                'content': ['article', '.article-content', '.content', 'main'],
                'remove': ['nav', 'header', 'footer', '.sidebar', '.related-articles', '.comments']
            },
            'default': {
                'title': ['h1', 'title'],
                'content': ['article', 'main', '.content', '#content', '.post', '.entry-content'],
                'remove': ['nav', 'header', 'footer', 'aside', '.sidebar', '.comments', '.advertisement']
            }
        }
    
    def fetch_from_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch and extract content from a URL
        
        Args:
            url: The URL to scrape
            
        Returns:
            Dictionary with extracted content and metadata
        """
        result = {
            'success': False,
            'url': url,
            'title': '',
            'content_html': '',
            'content_text': '',
            'meta_description': '',
            'headings': [],
            'error': None
        }
        
        try:
            # Try fetching with retry logic for 403 errors
            response = None
            for i, user_agent in enumerate(self.user_agents):
                headers = self.headers.copy()
                headers['User-Agent'] = user_agent

                try:
                    response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
                    response.raise_for_status()
                    break  # Success, exit loop
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 403 and i < len(self.user_agents) - 1:
                        # Try next user agent
                        continue
                    else:
                        # Not a 403 or no more user agents to try
                        raise

            if response is None:
                raise Exception("Failed to fetch URL after retrying with different user agents")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get domain for site-specific extraction
            domain = urlparse(url).netloc
            if 'gcore.com' in domain:
                selectors = self.content_selectors['gcore.com']
            else:
                selectors = self.content_selectors['default']
            
            # Extract title
            title = self._extract_title(soup, selectors)
            result['title'] = title
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                result['meta_description'] = meta_desc.get('content', '')
            
            # Remove unwanted elements
            for selector in selectors['remove']:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extract main content
            content_html, content_text, headings = self._extract_content(soup, selectors)
            
            result['content_html'] = content_html
            result['content_text'] = content_text
            result['headings'] = headings
            result['success'] = True
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else 'unknown'
            result['error'] = f"HTTP Error {status_code}: {str(e)}"
        except requests.exceptions.ConnectionError as e:
            result['error'] = f"Connection Error: Unable to reach {url}. Check your internet connection or the URL."
        except requests.exceptions.Timeout as e:
            result['error'] = f"Timeout Error: The request to {url} took too long."
        except requests.exceptions.RequestException as e:
            result['error'] = f"Request Error: {str(e)}"
        except Exception as e:
            result['error'] = f"Parse Error: {str(e)}"
        
        return result
    
    def _extract_title(self, soup: BeautifulSoup, selectors: Dict) -> str:
        """Extract the page title"""
        for selector in selectors['title']:
            element = soup.find(selector)
            if element:
                return element.get_text(strip=True)
        return ''
    
    def _extract_content(self, soup: BeautifulSoup, selectors: Dict) -> tuple:
        """
        Extract main content from the page
        
        Returns:
            Tuple of (html_content, text_content, headings_list)
        """
        # Try to find main content container
        content_element = None
        for selector in selectors['content']:
            content_element = soup.select_one(selector)
            if content_element:
                break
        
        # If no specific container found, use body
        if not content_element:
            content_element = soup.find('body')
        
        if not content_element:
            return '', '', []
        
        # Remove Gcore-specific related articles section and everything after
        # Look for the resources section component
        resources_section = content_element.find('gcore-resources-section')
        if resources_section:
            # Remove this section and everything after it
            for sibling in list(resources_section.find_next_siblings()):
                sibling.decompose()
            resources_section.decompose()
        
        # Also check for section tags with the specific Angular class
        for section in content_element.find_all('section'):
            # Check if it contains "Related articles" text
            if section.find(text=re.compile(r'Related articles', re.IGNORECASE)):
                # Remove this section and everything after
                for sibling in list(section.find_next_siblings()):
                    sibling.decompose()
                section.decompose()
                break
        
        # Fallback: Remove everything after "Related articles" heading
        stop_sections = [
            'related articles', 'subscribe to our newsletter', 'newsletter',
            'related posts', 'you might also like', 'recommended reading',
            'footer', 'comments', 'about the author', 'share this article'
        ]
        
        for heading in content_element.find_all(['h1', 'h2', 'h3', 'h4']):
            heading_text = heading.get_text(strip=True).lower()
            if any(stop_text in heading_text for stop_text in stop_sections):
                # Remove this heading and everything after it
                parent = heading.parent
                # Find the parent section or article element
                while parent and parent.name not in ['section', 'article', 'main', 'body']:
                    parent = parent.parent
                
                if parent:
                    # Remove all siblings after this parent
                    for sibling in list(parent.find_next_siblings()):
                        sibling.decompose()
                    # Remove the parent section itself
                    parent.decompose()
                else:
                    # Fallback: just remove the heading and its siblings
                    for sibling in list(heading.find_next_siblings()):
                        sibling.decompose()
                    heading.decompose()
                break
        
        # Also remove common footer/sidebar elements by class or id
        for selector in ['.related-articles', '.newsletter', '.footer', '.sidebar', 
                         '.comments', '.social-share', '.author-bio', '.recommended',
                         'gcore-resources-section', '[class*="resources-section"]',
                         '[class*="gc-resources-section"]']:
            for element in content_element.select(selector):
                element.decompose()
        
        # Extract headings structure (after cleanup)
        headings = self._extract_headings(content_element)
        
        # Get HTML content
        content_html = self._clean_html(str(content_element))
        
        # Get text content
        content_text = content_element.get_text(separator='\n', strip=True)
        
        return content_html, content_text, headings
    
    def _extract_headings(self, element) -> List[Dict[str, str]]:
        """Extract all headings from content"""
        headings = []
        
        for heading in element.find_all(['h1', 'h2', 'h3']):
            headings.append({
                'level': heading.name.upper(),
                'text': heading.get_text(strip=True)
            })
        
        return headings
    
    def _clean_html(self, html: str) -> str:
        """Clean and format HTML content"""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove inline styles and scripts
        html = re.sub(r'\s*style="[^"]*"', '', html)
        html = re.sub(r'\s*onclick="[^"]*"', '', html)
        html = re.sub(r'\s*onload="[^"]*"', '', html)
        
        # Remove excessive whitespace
        html = re.sub(r'\s+', ' ', html)
        html = re.sub(r'>\s+<', '><', html)
        
        return html.strip()
    
    def extract_gcore_article(self, url: str) -> Dict[str, Any]:
        """
        Specialized extraction for Gcore learning articles
        
        Args:
            url: Gcore article URL
            
        Returns:
            Structured content dictionary
        """
        result = self.fetch_from_url(url)
        
        if not result['success']:
            return result
        
        # Additional Gcore-specific processing
        soup = BeautifulSoup(result['content_html'], 'html.parser')
        
        # Count actual content words (excluding headings)
        content_words = 0
        for element in soup.find_all(['p', 'li', 'td']):
            content_words += len(element.get_text(strip=True).split())
        
        # Extract article metadata if available
        article_data = {
            'title': result['title'],
            'url': url,
            'meta_description': result['meta_description'],
            'content_sections': {},
            'raw_html': result['content_html'],
            'headings': result['headings'],
            'word_count': content_words,  # More accurate word count
            'success': True
        }
        
        # Extract content by sections (only main content)
        current_heading = None
        current_content = []
        
        # Stop at these sections
        stop_sections = ['related articles', 'subscribe', 'newsletter']
        
        for element in soup.children:
            if element.name in ['h1', 'h2', 'h3']:
                heading_text = element.get_text(strip=True)
                
                # Check if we should stop
                if any(stop in heading_text.lower() for stop in stop_sections):
                    break
                
                # Save previous section
                if current_heading:
                    article_data['content_sections'][current_heading] = '\n'.join(current_content)
                
                # Start new section
                current_heading = heading_text
                current_content = []
            elif element.name:  # Skip text nodes
                content = element.get_text(strip=True)
                if content and len(content) > 10:  # Skip very short snippets
                    current_content.append(content)
        
        # Save last section
        if current_heading and current_content:
            article_data['content_sections'][current_heading] = '\n'.join(current_content)
        
        return article_data
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible and valid
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Try HEAD request first (faster)
            response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except:
            return False
    
    def extract_primary_keyword(self, url: str, title: str, content: str) -> str:
        """
        Try to extract primary keyword from URL, title, and content
        
        Args:
            url: Page URL
            title: Page title
            content: Page content
            
        Returns:
            Suggested primary keyword
        """
        # Extract from URL path
        path = urlparse(url).path
        url_keywords = re.findall(r'[a-z]+(?:-[a-z]+)*', path.lower())
        
        # Clean common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        
        # Extract from title
        title_words = [word.lower() for word in re.findall(r'\w+', title) if word.lower() not in stop_words]
        
        # Find most relevant keyword
        if 'learning' in path and url_keywords:
            # For Gcore learning articles, use the last segment
            relevant_keywords = [k for k in url_keywords if k not in ['learning', 'gcore', 'com']]
            if relevant_keywords:
                return ' '.join(relevant_keywords[-1].split('-'))
        
        # Use title if available
        if title_words:
            # Return first 2-3 significant words from title
            return ' '.join(title_words[:3])
        
        return ''