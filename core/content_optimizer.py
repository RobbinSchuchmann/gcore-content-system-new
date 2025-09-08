"""
Content Optimizer Module
Handles content parsing, optimization, and intelligent merging
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from difflib import SequenceMatcher
from datetime import datetime
import json

from core.quality_checker import QualityChecker
from core.content_generator import ContentGenerator
from core.semantic_patterns import detect_question_type

class ContentOptimizer:
    """Optimize existing content while preserving valuable sections"""
    
    def __init__(self, content_generator: Optional[ContentGenerator] = None):
        self.content_generator = content_generator
        self.quality_checker = QualityChecker()
        self.preservation_threshold = 0.7  # Quality score threshold for preservation
        
    def parse_html_content(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content into structured format
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            Structured content dictionary
        """
        structure = {
            'title': '',
            'meta_description': '',
            'headings': [],
            'sections': {},
            'internal_links': [],
            'external_links': [],
            'word_count': 0,
            'images': []
        }
        
        # Extract title
        title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
        if title_match:
            structure['title'] = title_match.group(1).strip()
        
        # Extract meta description if present
        meta_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html_content, re.IGNORECASE)
        if meta_match:
            structure['meta_description'] = meta_match.group(1).strip()
        
        # Extract all headings with their content
        heading_pattern = r'<(h[1-3])[^>]*>([^<]+)</\1>'
        matches = list(re.finditer(heading_pattern, html_content, re.IGNORECASE))
        
        for i, match in enumerate(matches):
            level = match.group(1).upper()
            text = match.group(2).strip()
            start_pos = match.end()
            
            # Find content between this heading and the next
            if i < len(matches) - 1:
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(html_content)
            
            section_content = html_content[start_pos:end_pos]
            
            # Clean HTML from section content
            clean_content = re.sub(r'<[^>]+>', '', section_content).strip()
            
            # Extract links from section
            internal_links = re.findall(r'href="(/[^"]*)"', section_content)
            external_links = re.findall(r'href="(https?://[^"]*)"', section_content)
            
            # Extract images
            images = re.findall(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"', section_content)
            
            structure['headings'].append({
                'level': level,
                'text': text,
                'original_text': text,
                'content': clean_content,
                'word_count': len(clean_content.split()),
                'internal_links': internal_links,
                'external_links': external_links,
                'images': images
            })
            
            structure['sections'][text] = {
                'content': clean_content,
                'html': section_content,
                'word_count': len(clean_content.split()),
                'links': internal_links + external_links
            }
            
            # Aggregate links
            structure['internal_links'].extend(internal_links)
            structure['external_links'].extend(external_links)
            structure['images'].extend(images)
        
        # Calculate total word count
        structure['word_count'] = sum(h['word_count'] for h in structure['headings'])
        
        return structure
    
    def assess_section_quality(self, section_content: str, heading: str) -> Dict[str, Any]:
        """
        Assess the quality of a content section
        
        Args:
            section_content: The content to assess
            heading: The section heading
            
        Returns:
            Quality assessment results
        """
        # Use existing quality checker
        quality_results = self.quality_checker.check_content_quality(
            section_content,
            {'text': heading}
        )
        
        # Additional optimization-specific checks
        assessment = {
            'overall_score': quality_results['overall_score'],
            'preserve': quality_results['overall_score'] >= self.preservation_threshold,
            'issues': quality_results,
            'recommendations': []
        }
        
        # Check content freshness indicators
        outdated_patterns = [
            r'\b201[0-8]\b',  # Very old years
            r'last year',
            r'recently launched',
            r'new feature',
            r'coming soon'
        ]
        
        for pattern in outdated_patterns:
            if re.search(pattern, section_content, re.IGNORECASE):
                assessment['recommendations'].append('Update outdated references')
                assessment['preserve'] = False
                break
        
        # Check for thin content
        if len(section_content.split()) < 50:
            assessment['recommendations'].append('Expand thin content')
            assessment['preserve'] = False
        
        # Check for keyword relevance
        if heading.lower() not in section_content.lower():
            assessment['recommendations'].append('Improve keyword relevance')
        
        return assessment
    
    def merge_content(self, 
                     original_section: str,
                     new_section: str,
                     merge_strategy: str = 'smart') -> str:
        """
        Merge original and new content based on strategy
        
        Args:
            original_section: Original content
            new_section: New generated content
            merge_strategy: 'replace', 'append', 'smart', 'preserve_valuable'
            
        Returns:
            Merged content
        """
        if merge_strategy == 'replace':
            return new_section
        
        elif merge_strategy == 'append':
            return f"{original_section}\n\n{new_section}"
        
        elif merge_strategy == 'preserve_valuable':
            # For 'optimize' action - keep more original structure but improve quality
            valuable_elements = self._extract_valuable_elements(original_section)
            
            # Start with new content as base
            merged = new_section
            
            # Aggressively preserve ALL valuable elements
            # Preserve all statistics
            for element in valuable_elements.get('statistics', []):
                if element not in merged and len(element) > 10:
                    merged = self._integrate_statistic(merged, element)
            
            # Preserve all examples
            for example in valuable_elements.get('examples', []):
                if example not in merged and len(example) > 20:
                    merged = self._integrate_example(merged, example)
            
            # Preserve all technical specifications
            for spec in valuable_elements.get('technical_specs', []):
                if spec not in merged and len(spec) > 10:
                    merged = self._integrate_technical_spec(merged, spec)
            
            # Preserve quotes
            for quote in valuable_elements.get('quotes', []):
                if quote not in merged and len(quote) > 30:
                    # Try to integrate quote naturally
                    if '"' not in merged[:100]:  # If no quote at beginning
                        merged = f"{merged}\n\n{quote}"
            
            return merged
        
        elif merge_strategy == 'smart':
            # For 'rewrite' action - selective preservation
            valuable_elements = self._extract_valuable_elements(original_section)
            
            # Integrate valuable elements into new content
            merged = new_section
            
            # Preserve specific data points (numbers, statistics)
            for element in valuable_elements.get('statistics', [])[:5]:  # Limit to top 5
                if element not in merged:
                    # Add statistics that aren't in new content
                    merged = self._integrate_statistic(merged, element)
            
            # Preserve unique examples (limit to 3 best)
            for example in valuable_elements.get('examples', [])[:3]:
                if example not in merged and len(example) > 20:
                    merged = self._integrate_example(merged, example)
            
            # Preserve technical specifications (limit to 3)
            for spec in valuable_elements.get('technical_specs', [])[:3]:
                if spec not in merged:
                    merged = self._integrate_technical_spec(merged, spec)
            
            return merged
        
        return new_section
    
    def _extract_valuable_elements(self, content: str) -> Dict[str, List[str]]:
        """
        Extract valuable elements from content that should be preserved
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary of valuable elements
        """
        elements = {
            'statistics': [],
            'examples': [],
            'technical_specs': [],
            'quotes': [],
            'definitions': []
        }
        
        # Extract statistics (numbers with context)
        stat_patterns = [
            r'\d+(?:\.\d+)?%[^.]*',
            r'\d+(?:,\d{3})*(?:\.\d+)?\s+\w+',
            r'[A-Z]+\$?\d+(?:\.\d+)?(?:\s+(?:million|billion|thousand))?'
        ]
        
        for pattern in stat_patterns:
            matches = re.findall(pattern, content)
            elements['statistics'].extend(matches)
        
        # Extract examples (sentences with "for example", "such as", etc.)
        example_patterns = [
            r'[^.]*(?:for example|such as|including|like)[^.]*\.',
            r'[^.]*(?:e\.g\.|i\.e\.)[^.]*\.'
        ]
        
        for pattern in example_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            elements['examples'].extend(matches)
        
        # Extract technical specifications
        tech_patterns = [
            r'[^.]*(?:API|SDK|protocol|format|standard)[^.]*\.',
            r'[^.]*(?:\d+ms|\d+MB|\d+GB|\d+TB)[^.]*\.'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            elements['technical_specs'].extend(matches)
        
        # Extract quotes
        quote_pattern = r'"[^"]{20,}"'
        elements['quotes'] = re.findall(quote_pattern, content)
        
        # Extract definitions
        definition_patterns = [
            r'[^.]*\bis\s+(?:a|an|the)[^.]*\.',
            r'[^.]*refers?\s+to[^.]*\.'
        ]
        
        for pattern in definition_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            elements['definitions'].extend(matches[:2])  # Limit definitions
        
        return elements
    
    def _integrate_statistic(self, content: str, statistic: str) -> str:
        """Integrate a statistic into content intelligently"""
        # Find a good place to add the statistic
        sentences = content.split('. ')
        
        # Look for related context
        for i, sentence in enumerate(sentences):
            if any(keyword in sentence.lower() for keyword in ['performance', 'speed', 'rate', 'percentage']):
                # Insert after this sentence
                sentences.insert(i + 1, statistic)
                return '. '.join(sentences)
        
        # If no good place found, add to end of first paragraph
        return f"{content} {statistic}"
    
    def _integrate_example(self, content: str, example: str) -> str:
        """Integrate an example into content intelligently"""
        # Look for a place where examples would fit
        if 'for example' in content.lower():
            # Add to existing examples
            return content.replace('for example', f'for example, {example.lower()}. Additionally')
        
        # Add after first paragraph
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            paragraphs.insert(1, example)
            return '\n\n'.join(paragraphs)
        
        return f"{content}\n\n{example}"
    
    def _integrate_technical_spec(self, content: str, spec: str) -> str:
        """Integrate technical specification into content"""
        # Look for technical context
        tech_keywords = ['technical', 'specification', 'requirement', 'implementation']
        
        sentences = content.split('. ')
        for i, sentence in enumerate(sentences):
            if any(keyword in sentence.lower() for keyword in tech_keywords):
                sentences.insert(i + 1, spec)
                return '. '.join(sentences)
        
        # Add to end if no technical context found
        return f"{content}\n\n{spec}"
    
    def optimize_content(self,
                         original_structure: Dict[str, Any],
                         optimization_plan: List[Dict[str, Any]],
                         research_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize content based on plan with intelligent preservation
        
        Args:
            original_structure: Parsed original content
            optimization_plan: List of heading optimizations
            research_data: Additional research data
            
        Returns:
            Optimized content structure
        """
        optimized = {
            'title': original_structure.get('title', ''),
            'sections': {},
            'quality_scores': {},
            'preservation_summary': {},
            'change_summary': {
                'kept': 0,
                'optimized': 0,
                'rewritten': 0,
                'added': 0,
                'removed': 0
            }
        }
        
        for heading_plan in optimization_plan:
            heading_text = heading_plan['text']
            action = heading_plan.get('action', 'keep')
            
            # Get original content
            original_text = heading_plan.get('original_text', heading_text)
            original_content = ''
            
            # Try to find content by original text or current text
            if original_text in original_structure.get('sections', {}):
                original_content = original_structure['sections'][original_text].get('content', '')
            elif heading_text in original_structure.get('sections', {}):
                original_content = original_structure['sections'][heading_text].get('content', '')
            
            if action == 'keep':
                # Preserve original content with minor cleaning
                if original_content:
                    # Clean AI words and fix quality issues
                    cleaned_content = self._clean_content(original_content)
                    optimized['sections'][heading_text] = {
                        'content': cleaned_content,
                        'action': 'kept',
                        'changes': self._get_changes(original_content, cleaned_content),
                        'word_count': len(cleaned_content.split())
                    }
                    optimized['change_summary']['kept'] += 1
            
            elif action == 'optimize':
                # NEW: Optimize action - preserve valuable elements while improving quality
                if original_content:
                    # Extract valuable elements to preserve
                    valuable_elements = self._extract_valuable_elements(original_content)
                    
                    # Clean the content
                    cleaned_content = self._clean_content(original_content)
                    
                    # If we have a content generator and the quality is low, partially regenerate
                    if self.content_generator and research_data:
                        # Generate improved version while preserving elements
                        pattern_type = detect_question_type(heading_text)
                        improvement_context = {
                            'original': original_content,
                            'preserve_statistics': valuable_elements.get('statistics', []),
                            'preserve_examples': valuable_elements.get('examples', []),
                            'preserve_technical': valuable_elements.get('technical_specs', []),
                            'action': 'optimize'
                        }
                        
                        new_content_result = self.content_generator.generate_content(
                            heading=heading_text,
                            pattern_type=pattern_type,
                            research_data=research_data,
                            context=improvement_context,
                            function_name=heading_plan.get('function')
                        )
                        
                        if new_content_result['status'] == 'success':
                            # Smart merge: new structure with preserved valuable elements
                            optimized_content = self.merge_content(
                                cleaned_content,
                                new_content_result['content'],
                                merge_strategy='preserve_valuable'
                            )
                        else:
                            optimized_content = cleaned_content
                    else:
                        # No generator available, just clean the content
                        optimized_content = cleaned_content
                    
                    # Store preservation summary
                    optimized['preservation_summary'][heading_text] = {
                        'statistics_preserved': len(valuable_elements.get('statistics', [])),
                        'examples_preserved': len(valuable_elements.get('examples', [])),
                        'technical_preserved': len(valuable_elements.get('technical_specs', [])),
                        'quotes_preserved': len(valuable_elements.get('quotes', []))
                    }
                    
                    optimized['sections'][heading_text] = {
                        'content': optimized_content,
                        'action': 'optimized',
                        'changes': self._get_changes(original_content, optimized_content),
                        'preserved_elements': valuable_elements,
                        'word_count': len(optimized_content.split())
                    }
                    optimized['change_summary']['optimized'] += 1
            
            elif action == 'rewrite':
                # Complete rewrite but still preserve critical elements
                if self.content_generator and research_data:
                    # Extract valuable elements even for rewrites
                    valuable_elements = self._extract_valuable_elements(original_content) if original_content else {}
                    
                    # Generate new content
                    pattern_type = detect_question_type(heading_text)
                    rewrite_context = {
                        'original': original_content,
                        'preserve_critical': valuable_elements.get('statistics', [])[:3],  # Keep top statistics
                        'action': 'rewrite'
                    }
                    
                    new_content_result = self.content_generator.generate_content(
                        heading=heading_text,
                        pattern_type=pattern_type,
                        research_data=research_data,
                        context=rewrite_context,
                        function_name=heading_plan.get('function')
                    )
                    
                    if new_content_result['status'] == 'success':
                        new_content = new_content_result['content']
                        
                        # Merge with only the most valuable original elements
                        merged_content = self.merge_content(
                            original_content,
                            new_content,
                            merge_strategy='smart'
                        )
                        
                        optimized['sections'][heading_text] = {
                            'content': merged_content,
                            'action': 'rewritten',
                            'changes': self._get_changes(original_content, merged_content),
                            'word_count': len(merged_content.split())
                        }
                        optimized['change_summary']['rewritten'] += 1
                else:
                    # Fallback: clean existing content
                    cleaned_content = self._clean_content(original_content) if original_content else ''
                    if cleaned_content:
                        optimized['sections'][heading_text] = {
                            'content': cleaned_content,
                            'action': 'cleaned',
                            'changes': self._get_changes(original_content, cleaned_content),
                            'word_count': len(cleaned_content.split())
                        }
                        optimized['change_summary']['rewritten'] += 1
            
            elif action == 'new':
                # Generate completely new section
                if self.content_generator and research_data:
                    pattern_type = detect_question_type(heading_text)
                    new_content_result = self.content_generator.generate_content(
                        heading=heading_text,
                        pattern_type=pattern_type,
                        research_data=research_data,
                        context={'action': 'new'},
                        function_name=heading_plan.get('function')
                    )
                    
                    if new_content_result['status'] == 'success':
                        optimized['sections'][heading_text] = {
                            'content': new_content_result['content'],
                            'action': 'added',
                            'changes': 'New section added',
                            'word_count': len(new_content_result['content'].split())
                        }
                        optimized['change_summary']['added'] += 1
            
            elif action == 'remove':
                # Mark section as removed
                optimized['change_summary']['removed'] += 1
            
            # Calculate quality score for section
            if heading_text in optimized['sections']:
                quality_assessment = self.assess_section_quality(
                    optimized['sections'][heading_text]['content'],
                    heading_text
                )
                optimized['quality_scores'][heading_text] = quality_assessment
        
        # Calculate overall optimization score
        optimized['overall_improvement'] = self._calculate_improvement_score(
            original_structure,
            optimized
        )
        
        return optimized
    
    def _clean_content(self, content: str) -> str:
        """
        Clean content by removing AI words and fixing quality issues
        
        Args:
            content: Content to clean
            
        Returns:
            Cleaned content
        """
        # Import AI word replacements
        ai_replacements = {
            'leverage': 'use',
            'utilize': 'use',
            'delve': 'explore',
            'moreover': 'also',
            'furthermore': 'additionally',
            'whilst': 'while',
            'thus': 'therefore',
            'hence': 'so'
        }
        
        cleaned = content
        
        # Replace AI words
        for ai_word, replacement in ai_replacements.items():
            pattern = r'\b' + ai_word + r'\b'
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Fix double spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Fix sentence spacing
        cleaned = re.sub(r'\.([A-Z])', r'. \1', cleaned)
        
        return cleaned.strip()
    
    def _get_changes(self, original: str, modified: str) -> str:
        """
        Get a summary of changes between original and modified content
        
        Args:
            original: Original content
            modified: Modified content
            
        Returns:
            Change summary
        """
        if original == modified:
            return "No changes"
        
        # Calculate similarity
        similarity = SequenceMatcher(None, original, modified).ratio()
        
        if similarity > 0.9:
            return "Minor edits"
        elif similarity > 0.7:
            return "Moderate changes"
        elif similarity > 0.5:
            return "Significant changes"
        else:
            return "Major rewrite"
    
    def _calculate_improvement_score(self,
                                    original: Dict[str, Any],
                                    optimized: Dict[str, Any]) -> float:
        """
        Calculate overall improvement score
        
        Args:
            original: Original content structure
            optimized: Optimized content structure
            
        Returns:
            Improvement percentage
        """
        # Calculate average quality scores
        if optimized.get('quality_scores'):
            avg_quality = sum(
                score['overall_score'] 
                for score in optimized['quality_scores'].values()
            ) / len(optimized['quality_scores'])
        else:
            avg_quality = 0
        
        # Factor in structural improvements
        structural_score = 0
        if optimized['change_summary']['added'] > 0:
            structural_score += 10  # Bonus for adding missing sections
        if optimized['change_summary']['removed'] > 0:
            structural_score += 5   # Bonus for removing unnecessary sections
        
        # Calculate word count improvement
        original_words = original.get('word_count', 0)
        optimized_words = sum(
            len(section['content'].split()) 
            for section in optimized['sections'].values()
        )
        
        if original_words > 0:
            word_improvement = ((optimized_words - original_words) / original_words) * 10
            word_improvement = max(-20, min(20, word_improvement))  # Cap at ±20%
        else:
            word_improvement = 20
        
        # Combine scores
        total_improvement = avg_quality + structural_score + word_improvement
        
        return min(100, max(0, total_improvement))
    
    def generate_optimization_report(self,
                                    original: Dict[str, Any],
                                    optimized: Dict[str, Any]) -> str:
        """
        Generate a detailed optimization report
        
        Args:
            original: Original content structure
            optimized: Optimized content structure
            
        Returns:
            Formatted report
        """
        report_lines = [
            "# Content Optimization Report",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Summary",
            f"- Original Word Count: {original.get('word_count', 0)}",
            f"- Optimized Word Count: {sum(len(s['content'].split()) for s in optimized['sections'].values())}",
            f"- Overall Improvement Score: {optimized.get('overall_improvement', 0):.1f}%",
            "\n## Changes Made",
            f"- Sections Kept: {optimized['change_summary']['kept']}",
            f"- Sections Rewritten: {optimized['change_summary']['rewritten']}",
            f"- Sections Added: {optimized['change_summary']['added']}",
            f"- Sections Removed: {optimized['change_summary']['removed']}",
            "\n## Section Details"
        ]
        
        for heading, section in optimized['sections'].items():
            report_lines.append(f"\n### {heading}")
            report_lines.append(f"- Action: {section['action']}")
            report_lines.append(f"- Changes: {section['changes']}")
            
            if heading in optimized.get('quality_scores', {}):
                score = optimized['quality_scores'][heading]['overall_score']
                report_lines.append(f"- Quality Score: {score:.1f}/100")
        
        return "\n".join(report_lines)