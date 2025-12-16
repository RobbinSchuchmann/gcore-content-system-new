"""
Semantic Pattern Detection and Templates
Based on Koray Tuğberk GÜBÜR's Holistic SEO methodology
"""

import re
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

@dataclass
class PatternTemplate:
    """Template for a specific content pattern"""
    pattern_type: str
    opening_template: str
    structure: str
    example: str
    min_words: int
    max_words: int

class SemanticPatternDetector:
    """Detect and classify question patterns for semantic SEO"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.templates = self._initialize_templates()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize pattern detection rules"""
        return {
            'definition_singular': [
                r'^what is\s+(?:a\s+|an\s+|the\s+)?(.+?)(?:\?)?$',
                r'^define\s+(.+?)(?:\?)?$',
                r'^explain\s+what\s+(.+?)\s+is(?:\?)?$'
            ],
            'definition_plural': [
                r'^what are\s+(?:the\s+)?(.+?)(?:\?)?$',
                r'^what\s+(.+?)\s+are there(?:\?)?$'
            ],
            'how_to': [
                r'^how to\s+(.+?)(?:\?)?$',
                r'^how can (?:i|you|we|one)\s+(.+?)(?:\?)?$',
                r'^steps to\s+(.+?)(?:\?)?$'
            ],
            'how_process': [
                r'^how does\s+(.+?)(?:\?)?$',
                r'^how do\s+(.+?)(?:\?)?$',
                r'^how\s+(.+?)\s+works?(?:\?)?$'
            ],
            'how_common': [
                r'^how common (?:is|are)\s+(.+?)(?:\?)?$',
                r'^how often\s+(.+?)(?:\?)?$',
                r'^how frequently\s+(.+?)(?:\?)?$'
            ],
            'yes_no': [
                r'^(?:is|are|was|were|will|would|can|could|should|does|do|did|has|have|had)\s+(.+?)(?:\?)?$'
            ],
            'why': [
                r'^why\s+(?:is|are|does|do|should|would|can)\s+(.+?)(?:\?)?$',
                r'^why\s+(.+?)(?:\?)?$'
            ],
            'when': [
                r'^when\s+(?:is|are|does|do|should|would|can)\s+(.+?)(?:\?)?$',
                r'^when\s+(.+?)(?:\?)?$'
            ],
            'where': [
                r'^where\s+(?:is|are|does|do|should|would|can)\s+(.+?)(?:\?)?$',
                r'^where\s+(.+?)(?:\?)?$'
            ],
            'who': [
                r'^who\s+(?:is|are|was|were)\s+(.+?)(?:\?)?$',
                r'^who\s+(.+?)(?:\?)?$'
            ],
            'which': [
                r'^which\s+(.+?)(?:\?)?$'
            ]
        }
    
    def _initialize_templates(self) -> Dict[str, PatternTemplate]:
        """Initialize content templates for each pattern type"""
        return {
            'definition_singular': PatternTemplate(
                pattern_type='definition_singular',
                opening_template='{subject} is {definition}. {expansion}',
                structure='Direct definition + 2-3 sentences of expansion in paragraph form.',
                example='CDN caching is the process of storing copies of content at edge locations. This reduces latency by serving content from servers closer to users. The cached content is automatically updated based on configured TTL values.',
                min_words=50,
                max_words=150
            ),
            'definition_plural': PatternTemplate(
                pattern_type='definition_plural',
                opening_template='The {subject} are listed below.\n\n{list_items}',
                structure='List definition statement followed by bullet points with bold term + colon + explanation.',
                example='The benefits of CDN caching are listed below.\n\n• **Reduced Latency**: Content is served from edge locations closer to users.\n• **Lower Bandwidth Costs**: Origin server load is significantly reduced.\n• **Improved Reliability**: Multiple cache locations provide redundancy.',
                min_words=100,
                max_words=300
            ),
            'how_to': PatternTemplate(
                pattern_type='how_to',
                opening_template='To {action}, {process}. {steps}',
                structure='Opening sentence repeating the premise, then step-by-step instructions.',
                example='To implement CDN caching, you first need to configure your origin server. Then, set up cache rules based on content type. Finally, test the configuration using cache headers.',
                min_words=100,
                max_words=250
            ),
            'how_process': PatternTemplate(
                pattern_type='how_process',
                opening_template='{subject} works by {mechanism}. {detailed_explanation}',
                structure='Direct mechanism explanation followed by detailed process breakdown.',
                example='CDN caching works by storing copies of content at edge servers distributed globally. When a user requests content, the CDN routes them to the nearest edge server. If the content is cached, it\'s served immediately; otherwise, it\'s fetched from the origin.',
                min_words=100,
                max_words=200
            ),
            'how_common': PatternTemplate(
                pattern_type='how_common',
                opening_template='{subject} is {frequency_statement}, with {statistics}. {context}',
                structure='Direct frequency answer with statistics and supporting context.',
                example='CDN usage is extremely common, with over 70% of internet traffic delivered through CDNs. Studies show that major websites experience 50% faster load times with CDN implementation.',
                min_words=75,
                max_words=150
            ),
            'yes_no': PatternTemplate(
                pattern_type='yes_no',
                opening_template='{yes_no}, {subject} {predicate}. {explanation}',
                structure='Yes/No answer followed by explanation in paragraph form.',
                example='Yes, CDN caching significantly improves website performance. It reduces server load by up to 60% and decreases page load times by serving content from geographically distributed edge locations.',
                min_words=50,
                max_words=150
            ),
            'why': PatternTemplate(
                pattern_type='why',
                opening_template='{subject} {predicate} because {reason}. {detailed_explanation}',
                structure='Direct causal answer followed by detailed reasoning.',
                example='CDN caching is important because it dramatically reduces latency for global users. By storing content at edge locations, users receive data from nearby servers rather than distant origin servers, improving user experience and reducing bandwidth costs.',
                min_words=75,
                max_words=150
            ),
            'when': PatternTemplate(
                pattern_type='when',
                opening_template='{subject} should be {action} when {condition}. {context}',
                structure='Direct timing answer with conditions and context.',
                example='CDN caching should be implemented when your website serves global audiences. This is particularly important for sites with high traffic volumes, large media files, or users distributed across multiple geographic regions.',
                min_words=75,
                max_words=150
            ),
            'where': PatternTemplate(
                pattern_type='where',
                opening_template='{subject} is located {location}. {additional_details}',
                structure='Direct location answer with additional context.',
                example='CDN edge servers are located in data centers across major cities worldwide. Gcore maintains 210+ Points of Presence strategically positioned to ensure optimal coverage and minimal latency for all users.',
                min_words=50,
                max_words=100
            ),
            'who': PatternTemplate(
                pattern_type='who',
                opening_template='{subject} is {identification}. {background}',
                structure='Direct identification followed by relevant background.',
                example='Gcore is a global edge computing and content delivery company. Founded in 2014, the company provides CDN, edge cloud, and AI infrastructure services to businesses worldwide.',
                min_words=50,
                max_words=100
            ),
            'which': PatternTemplate(
                pattern_type='which',
                opening_template='{comparison_answer}. {justification}',
                structure='Direct answer to comparison/selection followed by justification.',
                example='The best CDN for gaming applications is one that offers low latency and high availability. Gcore\'s CDN provides 30ms average latency globally with 210+ PoPs, making it ideal for real-time gaming requirements.',
                min_words=75,
                max_words=150
            ),
            'general': PatternTemplate(
                pattern_type='general',
                opening_template='{topic_introduction}. {main_points}',
                structure='Topic introduction followed by main points.',
                example='CDN caching strategies vary based on content type and business requirements. Static content benefits from long cache times, while dynamic content requires careful cache invalidation strategies.',
                min_words=100,
                max_words=200
            )
        }
    
    def detect_pattern(self, heading: str) -> Tuple[str, Optional[str]]:
        """
        Detect the semantic pattern of a heading
        
        Args:
            heading: The heading text to analyze
            
        Returns:
            Tuple of (pattern_type, extracted_subject)
        """
        heading_lower = heading.lower().strip()
        
        for pattern_type, regexes in self.patterns.items():
            for regex in regexes:
                match = re.match(regex, heading_lower, re.IGNORECASE)
                if match:
                    subject = match.group(1) if match.groups() else None
                    return pattern_type, subject
        
        return 'general', None
    
    def get_template(self, pattern_type: str) -> PatternTemplate:
        """Get the template for a specific pattern type"""
        return self.templates.get(pattern_type, self.templates['general'])
    
    def get_semantic_triple(self, heading: str, pattern_type: str) -> Dict[str, str]:
        """
        Extract semantic triple (subject-predicate-object) from heading
        
        Args:
            heading: The heading text
            pattern_type: The detected pattern type
            
        Returns:
            Dictionary with subject, predicate, and object
        """
        triple = {
            'subject': '',
            'predicate': '',
            'object': ''
        }
        
        # Extract based on pattern type
        if pattern_type == 'definition_singular':
            triple['subject'] = self._extract_subject(heading)
            triple['predicate'] = 'is'
            triple['object'] = '[definition]'
        elif pattern_type == 'definition_plural':
            triple['subject'] = self._extract_subject(heading)
            triple['predicate'] = 'are'
            triple['object'] = '[list of items]'
        elif pattern_type == 'how_process':
            triple['subject'] = self._extract_subject(heading)
            triple['predicate'] = 'works by'
            triple['object'] = '[mechanism]'
        elif pattern_type == 'why':
            triple['subject'] = self._extract_subject(heading)
            triple['predicate'] = 'is important because'
            triple['object'] = '[reason]'
        
        return triple
    
    def _extract_subject(self, heading: str) -> str:
        """Extract the main subject from a heading"""
        # Remove question words and auxiliary verbs
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 
                         'is', 'are', 'does', 'do', 'can', 'should', 'will']
        
        words = heading.lower().split()
        filtered_words = []
        
        skip_next = False
        for word in words:
            if skip_next:
                skip_next = False
                continue
            if word not in question_words:
                filtered_words.append(word)
            elif word in ['is', 'are', 'does', 'do']:
                skip_next = True
        
        subject = ' '.join(filtered_words).strip('?').strip()
        return subject if subject else heading
    
    def get_content_requirements(self, pattern_type: str) -> Dict[str, any]:
        """Get specific content requirements for a pattern type"""
        template = self.get_template(pattern_type)
        
        requirements = {
            'min_words': template.min_words,
            'max_words': template.max_words,
            'structure': template.structure,
            'needs_list': pattern_type == 'definition_plural',
            'needs_steps': pattern_type == 'how_to',
            'needs_statistics': pattern_type == 'how_common',
            'needs_yes_no': pattern_type == 'yes_no',
            'needs_direct_answer': True  # Always true for semantic SEO
        }
        
        return requirements
    
    def validate_content_structure(self, content: str, pattern_type: str) -> Dict[str, any]:
        """
        Validate if content follows the required structure for its pattern type
        
        Args:
            content: The generated content
            pattern_type: The pattern type to validate against
            
        Returns:
            Dictionary with validation results
        """
        template = self.get_template(pattern_type)
        word_count = len(content.split())
        
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check word count
        if word_count < template.min_words:
            validation['errors'].append(f"Content too short: {word_count} words (minimum: {template.min_words})")
            validation['valid'] = False
        elif word_count > template.max_words:
            validation['warnings'].append(f"Content too long: {word_count} words (maximum: {template.max_words})")
        
        # Check pattern-specific requirements
        if pattern_type == 'definition_plural' and '• ' not in content:
            validation['errors'].append("List pattern requires bullet points")
            validation['valid'] = False
        
        if pattern_type == 'yes_no':
            first_word = content.split()[0].lower() if content else ''
            if first_word not in ['yes', 'no']:
                validation['errors'].append("Yes/No pattern must start with 'Yes' or 'No'")
                validation['valid'] = False
        
        if pattern_type == 'how_to' and not any(step in content.lower() for step in ['first', 'then', 'next', 'finally', 'step']):
            validation['warnings'].append("How-to pattern should include step indicators")
        
        return validation

# Singleton instance
detector = SemanticPatternDetector()

# Convenience functions
def detect_question_type(heading: str) -> str:
    """Detect the question type of a heading"""
    pattern_type, _ = detector.detect_pattern(heading)
    return pattern_type

def get_pattern_template(pattern_type: str) -> PatternTemplate:
    """Get the template for a pattern type"""
    return detector.get_template(pattern_type)

def get_semantic_triple(heading: str) -> Dict[str, str]:
    """Extract semantic triple from a heading"""
    pattern_type, _ = detector.detect_pattern(heading)
    return detector.get_semantic_triple(heading, pattern_type)

def validate_content(content: str, heading: str) -> Dict[str, any]:
    """Validate content against its pattern requirements"""
    pattern_type, _ = detector.detect_pattern(heading)
    return detector.validate_content_structure(content, pattern_type)