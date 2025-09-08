"""
Link Manager Module
Manages internal links for Gcore product pages and learning content
Focuses on high-value pages for SEO and user journey optimization
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import csv

@dataclass(frozen=True, eq=True)
class InternalLink:
    """Represents an internal link with metadata"""
    url: str
    title: str
    category: str  # product_service, product_solution, product_feature, learning
    subcategory: str  # cdn, cloud, security, etc.
    keywords: Tuple[str, ...]  # Use tuple for hashability
    relevance_keywords: Tuple[str, ...]  # Use tuple for hashability
    priority: int  # 1-5, higher is more important
    
    def __hash__(self):
        return hash((self.url, self.category))

class LinkManager:
    """Manages internal links for content generation and optimization"""
    
    def __init__(self, sitemap_path: Optional[str] = None, learning_topics_path: Optional[str] = None):
        """
        Initialize the Link Manager
        
        Args:
            sitemap_path: Path to sitemap CSV file
            learning_topics_path: Path to learning topics text file
        """
        self.links: List[InternalLink] = []
        self.category_map: Dict[str, List[InternalLink]] = {}
        self.keyword_index: Dict[str, List[InternalLink]] = {}
        
        # Default paths
        if sitemap_path is None:
            sitemap_path = Path(__file__).parent.parent.parent / "data" / "gcore" / "sitemap.csv"
        if learning_topics_path is None:
            learning_topics_path = Path(__file__).parent.parent.parent / "gcor-sitemap.txt"
            
        # Load links
        self._load_product_links(sitemap_path)
        self._load_learning_links(learning_topics_path)
        self._build_indices()
        
    def _load_product_links(self, sitemap_path):
        """Load product pages from sitemap CSV"""
        # High-value service categories to include
        INCLUDE_CATEGORIES = {'network', 'cloud', 'security', 'ai', 'hosting', 'edge'}
        INCLUDE_CONTENT_TYPES = {'service-page', 'service', 'solution', 'use-case', 'marketplace'}
        
        # URL patterns for key products
        PRODUCT_KEYWORDS = {
            '/cdn': ['cdn', 'content delivery', 'content distribution', 'cache', 'caching', 'performance'],
            '/cloud': ['cloud', 'cloud computing', 'virtual machine', 'vm', 'instance', 'kubernetes', 'k8s'],
            '/ddos-protection': ['ddos', 'ddos protection', 'ddos attack', 'security', 'mitigation'],
            '/dns': ['dns', 'domain name system', 'nameserver', 'dns resolution', 'dns hosting'],
            '/hosting': ['hosting', 'dedicated server', 'bare metal', 'vps', 'vds', 'server'],
            '/edge-network': ['edge', 'edge network', 'edge computing', 'low latency', 'global network'],
            '/ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'gpu', 'inference'],
            '/streaming': ['streaming', 'live streaming', 'video streaming', 'broadcast', 'hls', 'dash'],
            '/storage': ['storage', 'object storage', 's3', 'backup', 'data storage'],
            '/fastedge': ['fastedge', 'edge application', 'wasm', 'webassembly', 'serverless edge']
        }
        
        if isinstance(sitemap_path, str):
            sitemap_path = Path(sitemap_path)
            
        if not sitemap_path.exists():
            # Try alternative path
            alt_path = Path(__file__).parent.parent.parent.parent / "data" / "gcore" / "sitemap.csv"
            if alt_path.exists():
                sitemap_path = alt_path
            else:
                print(f"Warning: Sitemap not found at {sitemap_path}")
                return
                
        try:
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter for product pages only
                    if (row.get('service_category') in INCLUDE_CATEGORIES and 
                        row.get('content_type') in INCLUDE_CONTENT_TYPES):
                        
                        url = row['url'].replace('https://gcore.com', '')
                        
                        # Determine category
                        if 'service-page' in row.get('content_type', ''):
                            category = 'product_service'
                        elif 'solution' in row.get('content_type', ''):
                            category = 'product_solution'
                        elif 'use-case' in row.get('content_type', ''):
                            category = 'product_feature'
                        else:
                            category = 'product_feature'
                        
                        # Extract title from URL
                        title = url.split('/')[-1].replace('-', ' ').title() if url else 'Gcore Service'
                        
                        # Get keywords based on URL
                        keywords = []
                        relevance_keywords = []
                        for pattern, kw_list in PRODUCT_KEYWORDS.items():
                            if pattern in url:
                                keywords.extend(kw_list)
                                relevance_keywords.extend(kw_list)
                                break
                        
                        # Add URL components as keywords
                        url_parts = [p for p in url.split('/') if p and p != 'https:' and 'gcore' not in p]
                        for part in url_parts:
                            clean_part = part.replace('-', ' ')
                            keywords.append(clean_part)
                            relevance_keywords.append(clean_part)
                        
                        # Determine priority
                        priority = 5 if any(p in url for p in ['/cdn', '/cloud', '/ddos']) else 4
                        
                        link = InternalLink(
                            url=url,
                            title=title,
                            category=category,
                            subcategory=row.get('service_category', 'general'),
                            keywords=tuple(set(keywords)),
                            relevance_keywords=tuple(set(relevance_keywords)),
                            priority=priority
                        )
                        self.links.append(link)
                        
        except Exception as e:
            print(f"Error loading sitemap: {e}")
    
    def _load_learning_links(self, learning_topics_path):
        """Load learning/documentation pages"""
        # Keywords for categorizing learning content
        LEARNING_CATEGORIES = {
            'tutorial': ['configure', 'setup', 'install', 'deploy', 'build', 'create'],
            'concept': ['what-is', 'explained', 'overview', 'introduction', 'guide'],
            'troubleshooting': ['error', 'fix', 'troubleshoot', 'solve', 'debug'],
            'best-practices': ['best', 'optimize', 'improve', 'enhance', 'security'],
            'comparison': ['vs', 'versus', 'compare', 'difference']
        }
        
        if isinstance(learning_topics_path, str):
            learning_topics_path = Path(learning_topics_path)
            
        # Try to find learning topics
        if not learning_topics_path.exists():
            # Try alternative locations
            alt_paths = [
                Path(__file__).parent.parent.parent.parent / "gcore_learning_topics.txt",
                Path(__file__).parent.parent / "data" / "learning_topics.txt",
                Path(__file__).parent.parent / "data" / "gcore_learning_topics.txt"
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    learning_topics_path = alt_path
                    break
            else:
                # If no learning topics file, try parsing from sitemap for learning URLs
                print(f"Warning: Learning topics file not found, checking sitemap for /learning/ URLs")
                self._load_learning_from_sitemap()
                return
        
        try:
            with open(learning_topics_path, 'r', encoding='utf-8') as f:
                topics = [line.strip() for line in f if line.strip()]
                
            for topic in topics:
                # Create URL
                url = f"/learning/{topic}"
                
                # Create title from slug
                title = topic.replace('-', ' ').title()
                
                # Extract keywords from slug
                keywords = topic.split('-')
                relevance_keywords = keywords.copy()
                
                # Determine subcategory based on content
                subcategory = 'general'
                for cat, cat_keywords in LEARNING_CATEGORIES.items():
                    if any(kw in topic for kw in cat_keywords):
                        subcategory = cat
                        break
                
                # Add category-specific keywords
                if 'cdn' in topic:
                    relevance_keywords.extend(['cdn', 'content delivery', 'caching'])
                if 'kubernetes' in topic or 'k8s' in topic:
                    relevance_keywords.extend(['kubernetes', 'k8s', 'container', 'orchestration'])
                if 'docker' in topic:
                    relevance_keywords.extend(['docker', 'container', 'containerization'])
                if 'security' in topic or 'ddos' in topic:
                    relevance_keywords.extend(['security', 'protection', 'attack', 'defense'])
                if 'streaming' in topic or 'video' in topic:
                    relevance_keywords.extend(['streaming', 'video', 'media', 'broadcast'])
                    
                link = InternalLink(
                    url=url,
                    title=title,
                    category='learning',
                    subcategory=subcategory,
                    keywords=tuple(set(keywords)),
                    relevance_keywords=tuple(set(relevance_keywords)),
                    priority=3
                )
                self.links.append(link)
                
        except Exception as e:
            print(f"Error loading learning topics: {e}")
    
    def _load_learning_from_sitemap(self):
        """Load learning URLs from the main sitemap file"""
        sitemap_path = Path(__file__).parent.parent.parent.parent / "gcor-sitemap.txt"
        if not sitemap_path.exists():
            return
            
        try:
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                
            for url in urls:
                if '/learning/' in url:
                    # Extract the slug from the URL
                    parts = url.split('/learning/')
                    if len(parts) > 1:
                        slug = parts[1].strip('/')
                        if slug:
                            # Create learning link
                            title = slug.replace('-', ' ').title()
                            keywords = slug.split('-')
                            
                            link = InternalLink(
                                url=f"/learning/{slug}",
                                title=title,
                                category='learning',
                                subcategory='general',
                                keywords=tuple(keywords),
                                relevance_keywords=tuple(keywords),
                                priority=3
                            )
                            self.links.append(link)
        except Exception as e:
            print(f"Error loading learning from sitemap: {e}")
    
    def _build_indices(self):
        """Build category and keyword indices for fast lookup"""
        for link in self.links:
            # Category index
            if link.category not in self.category_map:
                self.category_map[link.category] = []
            self.category_map[link.category].append(link)
            
            # Keyword index (for all keywords and relevance keywords)
            all_keywords = set(link.keywords + link.relevance_keywords)
            for keyword in all_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower not in self.keyword_index:
                    self.keyword_index[keyword_lower] = []
                if link not in self.keyword_index[keyword_lower]:
                    self.keyword_index[keyword_lower].append(link)
    
    def find_relevant_links(self, content: str, topic: str = "", max_links: int = 5) -> List[InternalLink]:
        """
        Find relevant internal links for given content
        
        Args:
            content: The content to analyze
            topic: The main topic/heading
            max_links: Maximum number of links to return
            
        Returns:
            List of relevant InternalLink objects
        """
        # Extract keywords from content and topic
        content_lower = content.lower()
        topic_lower = topic.lower()
        
        # Score each link
        link_scores: Dict[InternalLink, float] = {}
        
        for link in self.links:
            score = 0.0
            
            # Check keyword matches in content
            for keyword in link.relevance_keywords:
                if keyword.lower() in content_lower:
                    score += 2.0
                    # Bonus for exact phrase match
                    if f" {keyword.lower()} " in f" {content_lower} ":
                        score += 1.0
            
            # Check topic relevance
            for keyword in link.keywords:
                if keyword.lower() in topic_lower:
                    score += 3.0
            
            # Priority bonus
            score += link.priority * 0.5
            
            # Category bonus for product pages
            if link.category.startswith('product'):
                score += 1.0
                
            if score > 0:
                link_scores[link] = score
        
        # Sort by score and return top N
        sorted_links = sorted(link_scores.items(), key=lambda x: x[1], reverse=True)
        return [link for link, score in sorted_links[:max_links] if score > 2.0]
    
    def get_links_by_category(self, category: str) -> List[InternalLink]:
        """Get all links in a specific category"""
        return self.category_map.get(category, [])
    
    def get_links_by_keyword(self, keyword: str) -> List[InternalLink]:
        """Get all links matching a keyword"""
        return self.keyword_index.get(keyword.lower(), [])
    
    def suggest_anchor_text(self, link: InternalLink, context: str) -> str:
        """
        Suggest natural anchor text for a link based on context
        
        Args:
            link: The internal link
            context: The surrounding text context
            
        Returns:
            Suggested anchor text
        """
        # Common patterns for different link types
        if link.category == 'product_service':
            if '/cdn' in link.url:
                return "CDN solution"
            elif '/cloud' in link.url:
                return "cloud platform"
            elif '/ddos' in link.url:
                return "DDoS protection"
            elif '/dns' in link.url:
                return "DNS hosting"
            elif '/hosting' in link.url:
                return "hosting services"
                
        elif link.category == 'learning':
            # For learning content, use more descriptive anchors
            if 'what-is' in link.url:
                topic = link.url.split('what-is-')[1] if 'what-is-' in link.url else 'this concept'
                return f"what {topic.replace('-', ' ')} is"
            elif 'how-to' in link.url or 'configure' in link.url:
                return "how to do this"
            elif 'guide' in link.url:
                return "complete guide"
                
        # Default: use title-based anchor
        return link.title.lower()
    
    def format_link_for_prompt(self, link: InternalLink, anchor_text: str) -> str:
        """Format a link for inclusion in generation prompt"""
        keywords_preview = ", ".join(link.keywords[:3]) if link.keywords else "related topics"
        return f'- Link to "{link.url}" with anchor text "{anchor_text}" when discussing {keywords_preview}'
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about loaded links"""
        stats = {
            'total_links': len(self.links),
            'product_services': len(self.get_links_by_category('product_service')),
            'product_solutions': len(self.get_links_by_category('product_solution')),
            'product_features': len(self.get_links_by_category('product_feature')),
            'learning_content': len(self.get_links_by_category('learning')),
            'unique_keywords': len(self.keyword_index)
        }
        return stats