"""
Internal Linker Module
Handles intelligent internal link placement following SOP requirements
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

from core.link_manager import LinkManager, InternalLink

@dataclass
class LinkPlacement:
    """Represents a suggested link placement within content"""
    link: InternalLink
    anchor_text: str
    position: int  # Character position in content
    relevance_score: float
    paragraph_index: int
    sentence_index: int
    placement_quality: str  # 'excellent', 'good', 'acceptable'

class InternalLinker:
    """
    Manages internal link suggestions and placement
    Following SOP requirements:
    - Exact match anchor text
    - Mid-paragraph placement preferred
    - Natural integration into sentences
    """
    
    def __init__(self, link_manager: Optional[LinkManager] = None):
        """
        Initialize the Internal Linker
        
        Args:
            link_manager: LinkManager instance for link database
        """
        self.link_manager = link_manager or LinkManager()
        self.min_relevance_score = 0.35  # Lowered from 0.7 for better matching
        self.max_links_per_section = 3
        self.min_words_between_links = 100
        
    def suggest_links_for_content(self, 
                                 content: str, 
                                 heading: str = "",
                                 max_links: int = 5) -> List[Tuple[InternalLink, str, float]]:
        """
        Suggest relevant internal links for content
        
        Args:
            content: The content to analyze
            heading: The section heading
            max_links: Maximum number of links to suggest
            
        Returns:
            List of tuples (InternalLink, suggested_anchor_text, relevance_score)
        """
        # Get relevant links from link manager
        relevant_links = self.link_manager.find_relevant_links(content, heading, max_links * 2)
        
        suggestions = []
        for link in relevant_links[:max_links]:
            # Calculate detailed relevance score
            relevance_score = self._calculate_relevance_score(link, content, heading)
            
            if relevance_score >= self.min_relevance_score:
                # Find best anchor text from content
                anchor_text = self._find_natural_anchor_text(link, content)
                if not anchor_text:
                    # Generate anchor text if not found in content
                    anchor_text = self.link_manager.suggest_anchor_text(link, content)
                
                suggestions.append((link, anchor_text, relevance_score))
        
        # Sort by relevance score
        suggestions.sort(key=lambda x: x[2], reverse=True)
        return suggestions[:max_links]
    
    def _calculate_relevance_score(self, link: InternalLink, content: str, heading: str) -> float:
        """
        Calculate detailed relevance score for a link
        
        Args:
            link: The internal link
            content: The content to analyze  
            heading: The section heading
            
        Returns:
            Relevance score between 0 and 1
        """
        score = 0.0
        content_lower = content.lower()
        heading_lower = heading.lower()
        
        # Keyword matching in content (40% weight)
        keyword_matches = 0
        for keyword in link.relevance_keywords:
            if keyword.lower() in content_lower:
                keyword_matches += 1
        if link.relevance_keywords:
            score += (keyword_matches / len(link.relevance_keywords)) * 0.4
        
        # Heading relevance (30% weight)
        heading_matches = 0
        for keyword in link.keywords:
            if keyword.lower() in heading_lower:
                heading_matches += 1
        if link.keywords:
            score += (heading_matches / len(link.keywords)) * 0.3
        
        # Category bonus (15% weight)
        if 'cloud' in content_lower and link.subcategory == 'cloud':
            score += 0.15
        elif 'cdn' in content_lower and link.subcategory == 'network':
            score += 0.15
        elif 'security' in content_lower and link.subcategory == 'security':
            score += 0.15
        elif 'streaming' in content_lower and 'streaming' in link.url:
            score += 0.15
        
        # Priority weight (15% weight)
        score += (link.priority / 5.0) * 0.15
        
        return min(score, 1.0)
    
    def _find_natural_anchor_text(self, link: InternalLink, content: str) -> Optional[str]:
        """
        Find natural anchor text within the content
        
        Args:
            link: The internal link
            content: The content to search
            
        Returns:
            Natural anchor text if found, None otherwise
        """
        content_lower = content.lower()
        
        # Priority 1: Look for exact keyword phrases
        for keyword in link.relevance_keywords:
            # Look for the keyword as a complete phrase
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, content_lower):
                # Find the actual case version in content
                matches = re.finditer(pattern, content_lower)
                for match in matches:
                    start = match.start()
                    end = match.end()
                    return content[start:end]
        
        # Priority 2: Look for related phrases
        anchor_candidates = [
            link.title.lower(),
            link.url.split('/')[-1].replace('-', ' ')
        ]
        
        for candidate in anchor_candidates:
            if candidate in content_lower:
                # Find the actual case version
                idx = content_lower.index(candidate)
                return content[idx:idx + len(candidate)]
        
        return None
    
    def place_links_in_content(self, 
                              content: str, 
                              link_suggestions: List[Tuple[InternalLink, str, float]]) -> str:
        """
        Place internal links within content following SOP rules
        
        Args:
            content: The original content
            link_suggestions: List of (InternalLink, anchor_text, relevance_score)
            
        Returns:
            Content with internal links placed
        """
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        links_placed = 0
        modified_paragraphs = []
        
        for para_idx, paragraph in enumerate(paragraphs):
            # Skip if paragraph is too short or is a list
            if len(paragraph.split()) < 20 or paragraph.strip().startswith(('•', '-', '*')):
                modified_paragraphs.append(paragraph)
                continue
            
            # Try to place one link per paragraph maximum
            link_placed_in_para = False
            
            for link, anchor_text, score in link_suggestions:
                if links_placed >= self.max_links_per_section or link_placed_in_para:
                    break
                
                # Check if anchor text exists in paragraph
                if anchor_text.lower() in paragraph.lower():
                    # Find best position (prefer middle of paragraph)
                    paragraph = self._place_link_in_paragraph(
                        paragraph, link, anchor_text
                    )
                    link_placed_in_para = True
                    links_placed += 1
            
            modified_paragraphs.append(paragraph)
        
        return '\n\n'.join(modified_paragraphs)
    
    def _place_link_in_paragraph(self, paragraph: str, link: InternalLink, anchor_text: str) -> str:
        """
        Place a single link within a paragraph at optimal position
        
        Args:
            paragraph: The paragraph text
            link: The internal link
            anchor_text: The anchor text to use
            
        Returns:
            Modified paragraph with link
        """
        # Find all occurrences of anchor text
        pattern = re.compile(re.escape(anchor_text), re.IGNORECASE)
        matches = list(pattern.finditer(paragraph))
        
        if not matches:
            return paragraph
        
        # Prefer middle occurrence if multiple exist
        if len(matches) > 1:
            # Choose the one closest to middle of paragraph
            para_middle = len(paragraph) // 2
            match = min(matches, key=lambda m: abs(m.start() - para_middle))
        else:
            match = matches[0]
        
        # Check if it's already a link
        start = match.start()
        end = match.end()
        
        # Don't link if already in a link or markdown syntax
        before_text = paragraph[:start]
        after_text = paragraph[end:]
        
        if '](' in before_text[-10:] or '](http' in after_text[:10]:
            return paragraph
        
        # Create the link
        actual_anchor = paragraph[start:end]
        link_markdown = f"[{actual_anchor}]({link.url})"
        
        # Replace in paragraph
        modified_paragraph = paragraph[:start] + link_markdown + paragraph[end:]
        
        return modified_paragraph
    
    def generate_link_prompt_section(self, link_suggestions: List[Tuple[InternalLink, str, float]]) -> str:
        """
        Generate prompt section for content generator to include links
        
        Args:
            link_suggestions: List of (InternalLink, anchor_text, relevance_score)
            
        Returns:
            Formatted prompt section for link inclusion
        """
        if not link_suggestions:
            return ""
        
        prompt = "\n\n**Internal Links to Include:**\n"
        prompt += "Include these internal links naturally within the content. "
        prompt += "Place them mid-paragraph where they fit contextually:\n\n"
        
        for link, anchor_text, score in link_suggestions[:3]:  # Limit to top 3
            # Provide context for when to use the link
            context = self._get_link_context(link)
            prompt += f'• When discussing {context}, link to "{link.url}" '
            prompt += f'using the exact anchor text "{anchor_text}"\n'
        
        prompt += "\n**Link Placement Rules:**\n"
        prompt += "- Place links naturally within sentences, NOT at the beginning\n"
        prompt += "- Ensure the anchor text flows with the sentence\n"
        prompt += "- Space links throughout the content (not clustered)\n"
        prompt += "- Only include if contextually relevant\n"
        
        return prompt
    
    def _get_link_context(self, link: InternalLink) -> str:
        """Get contextual description for when to use a link"""
        # Map URLs to contexts
        context_map = {
            '/cdn': 'content delivery or website performance',
            '/cloud': 'cloud computing or infrastructure',
            '/ddos': 'security threats or DDoS attacks',
            '/dns': 'domain management or DNS services',
            '/hosting': 'server hosting or dedicated servers',
            '/streaming': 'video streaming or live broadcasting',
            '/edge': 'edge computing or low latency',
            'learning': 'technical concepts or implementation details'
        }
        
        for key, context in context_map.items():
            if key in link.url:
                return context
        
        # Default context from keywords
        if link.keywords:
            return f"{link.keywords[0]} or related topics"
        
        return "relevant topics"
    
    def validate_link_placement(self, content: str) -> Dict[str, any]:
        """
        Validate that link placement follows SOP rules
        
        Args:
            content: Content with links placed
            
        Returns:
            Validation results dictionary
        """
        results = {
            'valid': True,
            'total_links': 0,
            'issues': [],
            'link_positions': []
        }
        
        # Find all links in content
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = list(re.finditer(link_pattern, content))
        results['total_links'] = len(matches)
        
        paragraphs = content.split('\n\n')
        
        for match in matches:
            anchor_text = match.group(1)
            url = match.group(2)
            position = match.start()
            
            # Find which paragraph contains this link
            current_pos = 0
            for para_idx, paragraph in enumerate(paragraphs):
                para_start = current_pos
                para_end = current_pos + len(paragraph)
                
                if para_start <= position < para_end:
                    # Check position within paragraph
                    relative_pos = position - para_start
                    para_length = len(paragraph)
                    position_ratio = relative_pos / para_length if para_length > 0 else 0
                    
                    # Validate: Not at the very beginning (first 10%)
                    if position_ratio < 0.1:
                        results['issues'].append(
                            f'Link "{anchor_text}" is too close to paragraph start'
                        )
                        results['valid'] = False
                    
                    # Check if it's in a sentence (not standalone)
                    surrounding_text = paragraph[max(0, relative_pos-50):min(para_length, relative_pos+50)]
                    if not any(char in surrounding_text for char in '.!?'):
                        results['issues'].append(
                            f'Link "{anchor_text}" may not be within a proper sentence'
                        )
                    
                    results['link_positions'].append({
                        'anchor': anchor_text,
                        'url': url,
                        'paragraph': para_idx + 1,
                        'position_ratio': position_ratio,
                        'quality': 'good' if 0.3 <= position_ratio <= 0.7 else 'acceptable'
                    })
                    
                    break
                
                current_pos = para_end + 2  # Account for \n\n
        
        # Check link density
        word_count = len(content.split())
        if results['total_links'] > 0:
            words_per_link = word_count / results['total_links']
            if words_per_link < 100:
                results['issues'].append(
                    f'Link density too high: {words_per_link:.0f} words per link (minimum: 100)'
                )
                results['valid'] = False
        
        return results