"""
Gap Analyzer Module
Analyzes content gaps, keyword coverage, and suggests improvements
"""

import re
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import Counter
import json
from pathlib import Path

class GapAnalyzer:
    """Analyze content gaps and suggest optimizations"""
    
    def __init__(self):
        self.common_topic_patterns = self._load_topic_patterns()
        self.competitor_keywords = set()
        self.industry_terms = self._load_industry_terms()
        
    def _load_topic_patterns(self) -> Dict[str, List[str]]:
        """Load common topic patterns for different content types"""
        return {
            'definition': [
                'what is', 'what are', 'definition of', 'meaning of',
                'understanding', 'introduction to', 'overview of'
            ],
            'how_to': [
                'how to', 'guide to', 'tutorial', 'step by step',
                'instructions', 'setup', 'configure', 'implement'
            ],
            'comparison': [
                'vs', 'versus', 'comparison', 'difference between',
                'compare', 'better than', 'alternative to'
            ],
            'benefits': [
                'benefits', 'advantages', 'pros and cons', 'why use',
                'reasons to', 'importance of', 'value of'
            ],
            'best_practices': [
                'best practices', 'tips', 'recommendations', 'guidelines',
                'dos and donts', 'common mistakes', 'optimization'
            ],
            'use_cases': [
                'use cases', 'examples', 'applications', 'scenarios',
                'when to use', 'real world', 'case study'
            ],
            'troubleshooting': [
                'troubleshooting', 'fix', 'solve', 'error', 'issue',
                'problem', 'debug', 'resolve'
            ],
            'technical': [
                'architecture', 'implementation', 'technical',
                'specification', 'api', 'integration', 'deployment'
            ]
        }
    
    def _load_industry_terms(self) -> Set[str]:
        """Load industry-specific terms for Gcore"""
        return {
            # CDN/Edge terms
            'cdn', 'content delivery', 'edge computing', 'edge server',
            'cache', 'caching', 'purge', 'invalidation', 'origin server',
            'pop', 'point of presence', 'anycast', 'geo-routing',
            
            # Cloud/Infrastructure terms
            'cloud computing', 'iaas', 'paas', 'saas', 'virtual machine',
            'container', 'kubernetes', 'docker', 'orchestration',
            'load balancing', 'auto-scaling', 'high availability',
            
            # Security terms
            'ddos protection', 'waf', 'web application firewall',
            'ssl', 'tls', 'certificate', 'encryption', 'security',
            'firewall rules', 'rate limiting', 'bot protection',
            
            # Performance terms
            'latency', 'bandwidth', 'throughput', 'performance',
            'optimization', 'speed', 'response time', 'uptime',
            'sla', 'qos', 'monitoring', 'analytics',
            
            # Storage terms
            'object storage', 's3', 'block storage', 'backup',
            'replication', 'redundancy', 'durability', 'availability',
            
            # AI/GPU terms
            'gpu', 'ai infrastructure', 'machine learning', 'inference',
            'training', 'cuda', 'tensor', 'model serving'
        }
    
    def analyze_keyword_gaps(self,
                            content: str,
                            target_keywords: List[str],
                            headings: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze keyword gaps in content
        
        Args:
            content: The full content text
            target_keywords: List of target keywords
            headings: List of heading dictionaries
            
        Returns:
            Gap analysis results
        """
        content_lower = content.lower()
        heading_text = ' '.join([h.get('text', '').lower() for h in headings])
        
        analysis = {
            'keyword_coverage': {},
            'missing_keywords': [],
            'keyword_density': {},
            'suggestions': [],
            'coverage_score': 0
        }
        
        # Analyze each target keyword
        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            
            # Count occurrences in content
            content_count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', content_lower))
            
            # Count occurrences in headings
            heading_count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', heading_text))
            
            # Calculate density (per 100 words)
            word_count = len(content.split())
            density = (content_count / word_count * 100) if word_count > 0 else 0
            
            analysis['keyword_coverage'][keyword] = {
                'in_content': content_count,
                'in_headings': heading_count,
                'total': content_count + heading_count,
                'density': round(density, 2)
            }
            
            analysis['keyword_density'][keyword] = density
            
            # Check if keyword is missing or underused
            if content_count == 0 and heading_count == 0:
                analysis['missing_keywords'].append(keyword)
                analysis['suggestions'].append({
                    'type': 'missing_keyword',
                    'keyword': keyword,
                    'recommendation': f"Add content about '{keyword}' - currently not covered"
                })
            elif content_count < 3:
                analysis['suggestions'].append({
                    'type': 'low_density',
                    'keyword': keyword,
                    'recommendation': f"Increase mentions of '{keyword}' - currently only {content_count} times"
                })
            elif density > 3:
                analysis['suggestions'].append({
                    'type': 'keyword_stuffing',
                    'keyword': keyword,
                    'recommendation': f"Reduce mentions of '{keyword}' - density too high at {density:.1f}%"
                })
        
        # Calculate overall coverage score
        if target_keywords:
            covered = len([k for k in target_keywords if analysis['keyword_coverage'][k]['total'] > 0])
            analysis['coverage_score'] = (covered / len(target_keywords)) * 100
        
        return analysis
    
    def suggest_missing_sections(self,
                                existing_headings: List[Dict[str, str]],
                                primary_keyword: str,
                                content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Suggest missing sections based on content type and keyword
        
        Args:
            existing_headings: Current heading structure
            primary_keyword: Main topic keyword
            content_type: Type of content (optional)
            
        Returns:
            List of suggested sections
        """
        suggestions = []
        existing_text = ' '.join([h.get('text', '').lower() for h in existing_headings])
        
        # Detect content type if not provided
        if not content_type:
            content_type = self._detect_content_type(primary_keyword, existing_text)
        
        # Get expected sections for content type
        expected_sections = self._get_expected_sections(content_type, primary_keyword)
        
        # Check which expected sections are missing
        for section in expected_sections:
            section_keywords = section['keywords']
            found = any(kw in existing_text for kw in section_keywords)
            
            if not found:
                suggestions.append({
                    'heading': section['heading'],
                    'level': section['level'],
                    'reason': section['reason'],
                    'priority': section['priority'],
                    'function': section.get('function', 'generate_definition')
                })
        
        # Sort by priority
        suggestions.sort(key=lambda x: x['priority'])
        
        return suggestions
    
    def _detect_content_type(self, keyword: str, existing_content: str) -> str:
        """Detect the type of content based on keyword and existing content"""
        keyword_lower = keyword.lower()
        content_lower = existing_content.lower()
        
        # Check for pattern matches
        for content_type, patterns in self.common_topic_patterns.items():
            if any(pattern in keyword_lower or pattern in content_lower for pattern in patterns):
                return content_type
        
        return 'general'
    
    def _get_expected_sections(self, content_type: str, primary_keyword: str) -> List[Dict[str, Any]]:
        """Get expected sections based on content type"""
        sections = []
        
        # Common sections for all content types
        common_sections = [
            {
                'heading': f"What is {primary_keyword}?",
                'keywords': ['what is', 'definition', 'introduction'],
                'level': 'H2',
                'reason': 'Essential definition section',
                'priority': 1,
                'function': 'generate_definition'
            }
        ]
        
        # Type-specific sections
        type_sections = {
            'definition': [
                {
                    'heading': f"How does {primary_keyword} work?",
                    'keywords': ['how does', 'how it works', 'mechanism'],
                    'level': 'H2',
                    'reason': 'Explain the mechanism',
                    'priority': 2,
                    'function': 'generate_process_explanation'
                },
                {
                    'heading': f"Benefits of {primary_keyword}",
                    'keywords': ['benefits', 'advantages', 'pros'],
                    'level': 'H2',
                    'reason': 'Highlight value proposition',
                    'priority': 3,
                    'function': 'generate_benefits'
                },
                {
                    'heading': f"Use cases for {primary_keyword}",
                    'keywords': ['use cases', 'applications', 'examples'],
                    'level': 'H2',
                    'reason': 'Provide practical examples',
                    'priority': 4,
                    'function': 'generate_use_cases'
                }
            ],
            'how_to': [
                {
                    'heading': "Prerequisites",
                    'keywords': ['prerequisites', 'requirements', 'before you start'],
                    'level': 'H2',
                    'reason': 'Set up reader for success',
                    'priority': 1,
                    'function': 'generate_prerequisites'
                },
                {
                    'heading': "Step-by-step guide",
                    'keywords': ['steps', 'instructions', 'procedure'],
                    'level': 'H2',
                    'reason': 'Core instructional content',
                    'priority': 2,
                    'function': 'generate_steps'
                },
                {
                    'heading': "Troubleshooting",
                    'keywords': ['troubleshooting', 'common issues', 'problems'],
                    'level': 'H2',
                    'reason': 'Help users resolve issues',
                    'priority': 5,
                    'function': 'generate_troubleshooting'
                }
            ],
            'comparison': [
                {
                    'heading': "Key differences",
                    'keywords': ['differences', 'comparison', 'versus'],
                    'level': 'H2',
                    'reason': 'Core comparison content',
                    'priority': 2,
                    'function': 'generate_comparison'
                },
                {
                    'heading': "When to use each option",
                    'keywords': ['when to use', 'use cases', 'scenarios'],
                    'level': 'H2',
                    'reason': 'Decision guidance',
                    'priority': 3,
                    'function': 'generate_decision_guide'
                },
                {
                    'heading': "Performance comparison",
                    'keywords': ['performance', 'benchmark', 'speed'],
                    'level': 'H2',
                    'reason': 'Data-driven comparison',
                    'priority': 4,
                    'function': 'generate_performance_comparison'
                }
            ],
            'technical': [
                {
                    'heading': "Technical architecture",
                    'keywords': ['architecture', 'design', 'structure'],
                    'level': 'H2',
                    'reason': 'Technical deep dive',
                    'priority': 2,
                    'function': 'generate_architecture'
                },
                {
                    'heading': "Implementation details",
                    'keywords': ['implementation', 'configuration', 'setup'],
                    'level': 'H2',
                    'reason': 'Practical implementation',
                    'priority': 3,
                    'function': 'generate_implementation'
                },
                {
                    'heading': "API reference",
                    'keywords': ['api', 'endpoints', 'methods'],
                    'level': 'H2',
                    'reason': 'Developer documentation',
                    'priority': 4,
                    'function': 'generate_api_reference'
                },
                {
                    'heading': "Best practices",
                    'keywords': ['best practices', 'recommendations', 'guidelines'],
                    'level': 'H2',
                    'reason': 'Optimization guidance',
                    'priority': 5,
                    'function': 'generate_best_practices'
                }
            ]
        }
        
        # Add common sections
        sections.extend(common_sections)
        
        # Add type-specific sections
        if content_type in type_sections:
            sections.extend(type_sections[content_type])
        
        # Add Gcore-specific sections if relevant
        if any(term in primary_keyword.lower() for term in self.industry_terms):
            sections.append({
                'heading': "Why choose Gcore?",
                'keywords': ['why gcore', 'gcore benefits', 'gcore features'],
                'level': 'H2',
                'reason': 'Gcore value proposition',
                'priority': 10,
                'function': 'generate_gcore_service'
            })
        
        return sections
    
    def analyze_content_depth(self,
                            sections: Dict[str, str],
                            word_count_threshold: int = 150) -> Dict[str, Any]:
        """
        Analyze the depth of content in each section
        
        Args:
            sections: Dictionary of section headings to content
            word_count_threshold: Minimum words for adequate depth
            
        Returns:
            Depth analysis results
        """
        analysis = {
            'shallow_sections': [],
            'adequate_sections': [],
            'comprehensive_sections': [],
            'average_depth': 0,
            'recommendations': []
        }
        
        total_words = 0
        
        for heading, content in sections.items():
            word_count = len(content.split())
            total_words += word_count
            
            if word_count < word_count_threshold * 0.5:
                analysis['shallow_sections'].append({
                    'heading': heading,
                    'word_count': word_count,
                    'recommendation': 'Expand significantly - very thin content'
                })
                analysis['recommendations'].append(
                    f"Expand '{heading}' - only {word_count} words (target: {word_count_threshold}+)"
                )
            elif word_count < word_count_threshold:
                analysis['adequate_sections'].append({
                    'heading': heading,
                    'word_count': word_count,
                    'recommendation': 'Could benefit from expansion'
                })
            else:
                analysis['comprehensive_sections'].append({
                    'heading': heading,
                    'word_count': word_count
                })
        
        # Calculate average depth
        if sections:
            analysis['average_depth'] = total_words / len(sections)
        
        return analysis
    
    def suggest_semantic_improvements(self,
                                     content: str,
                                     primary_keyword: str) -> List[Dict[str, str]]:
        """
        Suggest semantic SEO improvements
        
        Args:
            content: Current content
            primary_keyword: Main topic
            
        Returns:
            List of semantic improvements
        """
        improvements = []
        content_lower = content.lower()
        
        # Check for LSI keywords
        lsi_keywords = self._get_lsi_keywords(primary_keyword)
        missing_lsi = [kw for kw in lsi_keywords if kw not in content_lower]
        
        if missing_lsi:
            improvements.append({
                'type': 'lsi_keywords',
                'suggestion': f"Add LSI keywords: {', '.join(missing_lsi[:5])}",
                'priority': 'medium'
            })
        
        # Check for question-based headings
        questions = ['what', 'how', 'why', 'when', 'where', 'which']
        has_questions = any(q in content_lower for q in questions)
        
        if not has_questions:
            improvements.append({
                'type': 'question_headings',
                'suggestion': 'Add question-based headings for better semantic SEO',
                'priority': 'high'
            })
        
        # Check for entity mentions
        entities = self._extract_entities(content)
        if len(entities) < 5:
            improvements.append({
                'type': 'entities',
                'suggestion': 'Add more specific entities (products, technologies, companies)',
                'priority': 'medium'
            })
        
        # Check for structured data opportunities
        if 'step' not in content_lower and 'how to' in primary_keyword.lower():
            improvements.append({
                'type': 'structured_data',
                'suggestion': 'Add numbered steps for HowTo schema markup',
                'priority': 'high'
            })
        
        return improvements
    
    def _get_lsi_keywords(self, primary_keyword: str) -> List[str]:
        """Get LSI (Latent Semantic Indexing) keywords"""
        # This would ideally connect to an API or database
        # For now, return common related terms based on keyword
        
        lsi_map = {
            'cdn': ['content delivery', 'caching', 'edge server', 'latency', 'performance'],
            'cloud': ['virtual machine', 'scalability', 'infrastructure', 'deployment', 'resources'],
            'security': ['firewall', 'protection', 'encryption', 'threat', 'compliance'],
            'storage': ['backup', 'replication', 'durability', 'availability', 'redundancy']
        }
        
        for key, values in lsi_map.items():
            if key in primary_keyword.lower():
                return values
        
        return []
    
    def _extract_entities(self, content: str) -> Set[str]:
        """Extract named entities from content"""
        entities = set()
        
        # Extract capitalized words (simple NER)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        matches = re.findall(pattern, content)
        entities.update(matches)
        
        # Extract known technical terms
        for term in self.industry_terms:
            if term.lower() in content.lower():
                entities.add(term)
        
        return entities
    
    def generate_gap_report(self,
                           keyword_analysis: Dict[str, Any],
                           missing_sections: List[Dict[str, Any]],
                           depth_analysis: Dict[str, Any]) -> str:
        """
        Generate a comprehensive gap analysis report
        
        Args:
            keyword_analysis: Keyword gap analysis results
            missing_sections: Suggested missing sections
            depth_analysis: Content depth analysis
            
        Returns:
            Formatted report
        """
        report_lines = [
            "# Content Gap Analysis Report",
            "\n## Keyword Coverage",
            f"- Overall Coverage Score: {keyword_analysis.get('coverage_score', 0):.1f}%",
            f"- Missing Keywords: {len(keyword_analysis.get('missing_keywords', []))}",
            "\n### Keyword Details:"
        ]
        
        for keyword, coverage in keyword_analysis.get('keyword_coverage', {}).items():
            report_lines.append(
                f"- **{keyword}**: {coverage['total']} mentions "
                f"(density: {coverage['density']:.2f}%)"
            )
        
        if keyword_analysis.get('missing_keywords'):
            report_lines.append("\n### Missing Keywords:")
            for keyword in keyword_analysis['missing_keywords']:
                report_lines.append(f"- {keyword}")
        
        report_lines.extend([
            "\n## Missing Sections",
            f"Found {len(missing_sections)} recommended sections to add:"
        ])
        
        for section in missing_sections[:5]:  # Top 5 suggestions
            report_lines.append(
                f"\n### {section['heading']} ({section['level']})"
            )
            report_lines.append(f"- Reason: {section['reason']}")
            report_lines.append(f"- Priority: {section['priority']}")
        
        report_lines.extend([
            "\n## Content Depth Analysis",
            f"- Average Section Depth: {depth_analysis.get('average_depth', 0):.0f} words",
            f"- Shallow Sections: {len(depth_analysis.get('shallow_sections', []))}",
            f"- Adequate Sections: {len(depth_analysis.get('adequate_sections', []))}",
            f"- Comprehensive Sections: {len(depth_analysis.get('comprehensive_sections', []))}"
        ])
        
        if depth_analysis.get('shallow_sections'):
            report_lines.append("\n### Sections Needing Expansion:")
            for section in depth_analysis['shallow_sections']:
                report_lines.append(
                    f"- {section['heading']}: {section['word_count']} words"
                )
        
        return "\n".join(report_lines)