"""
Quality Checker for Generated Content
Validates content against Gcore brand guidelines and SEO requirements
"""

import re
from typing import Dict, List, Any, Tuple
import json
from pathlib import Path
from config import (
    QUALITY_THRESHOLDS,
    CONTENT_SETTINGS,
    GCORE_INFO,
    DATA_DIR
)
from core.semantic_patterns import validate_content as validate_pattern

class QualityChecker:
    """Check and validate content quality"""
    
    def __init__(self):
        self.ai_blacklist = self._load_ai_blacklist()
        self.brand_guidelines = self._load_brand_guidelines()
        self.gcore_products = self._load_gcore_products()
        self.ai_replacements = self._load_ai_replacements()
    
    def _load_ai_blacklist(self) -> List[str]:
        """Load AI words blacklist"""
        blacklist_file = DATA_DIR / 'ai_blacklist.txt'
        if blacklist_file.exists():
            with open(blacklist_file, 'r') as f:
                return [word.strip().lower() for word in f.readlines() if word.strip()]
        else:
            # Default blacklist
            return [
                'delve', 'delving', 'moreover', 'furthermore', 'notably',
                'essentially', 'basically', 'significantly', 'predominantly',
                'consequently', 'subsequently', 'intricate', 'intricacies',
                'revolutionize', 'revolutionary', 'cutting-edge', 'state-of-the-art',
                'leverage', 'leveraging', 'utilize', 'utilization',
                'aforementioned', 'whilst', 'thus', 'hence', 'thereby'
            ]
    
    def _load_brand_guidelines(self) -> Dict[str, Any]:
        """Load Gcore brand guidelines"""
        guidelines_file = DATA_DIR / 'brand_guidelines.json'
        if guidelines_file.exists():
            with open(guidelines_file, 'r') as f:
                return json.load(f)
        else:
            # Default guidelines
            return {
                'style_rules': {
                    'use_contractions': True,
                    'sentence_case_headings': True,
                    'formal_tone': True,
                    'avoid_competitors': True,
                    'max_sentence_length': 30,
                    'max_paragraph_length': 150
                },
                'terminology': {
                    'preferred': {
                        'CDN': 'CDN',
                        'edge_computing': 'edge computing',
                        'points_of_presence': 'Points of Presence',
                        'pops': 'PoPs'
                    },
                    'avoid': {
                        'content_delivery_network': 'Use CDN instead',
                        'edge_nodes': 'Use edge servers or PoPs'
                    }
                }
            }
    
    def _load_gcore_products(self) -> Dict[str, Any]:
        """Load Gcore product information"""
        products_file = DATA_DIR / 'gcore_products.json'
        if products_file.exists():
            with open(products_file, 'r') as f:
                return json.load(f)
        else:
            return GCORE_INFO['services']
    
    def _load_ai_replacements(self) -> Dict[str, str]:
        """Load AI word replacements from shared JSON file"""
        replacements_file = DATA_DIR / 'ai_word_replacements.json'
        if replacements_file.exists():
            with open(replacements_file, 'r') as f:
                data = json.load(f)
                
                # Build a flat dictionary of all replacements
                flat_replacements = {}
                
                # Add simple replacements
                if 'simple_replacements' in data:
                    flat_replacements.update(data['simple_replacements'])
                
                # Add word group replacements (using first replacement option)
                if 'word_groups' in data:
                    for group in data['word_groups'].values():
                        words = group.get('words', [])
                        replacements = group.get('replacements', [])
                        if words and replacements:
                            for word in words:
                                flat_replacements[word.lower()] = replacements[0]
                
                return flat_replacements
        
        # Fallback to hardcoded replacements
        return {
            'leverage': 'use',
            'utilize': 'use',
            'delve': 'explore',
            'moreover': 'also',
            'furthermore': 'additionally'
        }
    
    def check_quality(self, 
                      content: str, 
                      heading: str,
                      pattern_type: str = None) -> Dict[str, Any]:
        """
        Comprehensive quality check for content
        
        Args:
            content: The content to check
            heading: The heading this content answers
            pattern_type: The pattern type of the content
            
        Returns:
            Dictionary with quality scores and issues
        """
        results = {
            'overall_score': 100,
            'checks': {},
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 1. Check for AI words
        ai_check = self._check_ai_words(content)
        results['checks']['ai_words'] = ai_check
        if ai_check['found']:
            results['issues'].append(f"Found {len(ai_check['words'])} AI-sounding words")
            results['overall_score'] -= min(len(ai_check['words']) * 5, 30)
        
        # 2. Check for competitor mentions (critical brand violation)
        competitor_check = self._check_competitor_mentions(content)
        results['checks']['competitor_mentions'] = competitor_check
        if competitor_check['found']:
            results['issues'].append(f"Found {len(competitor_check['mentions'])} competitor mentions")
            results['overall_score'] -= len(competitor_check['mentions']) * 10  # Heavy penalty
        
        # 3. Check Gcore compliance
        gcore_check = self._check_gcore_compliance(content)
        results['checks']['gcore_compliance'] = gcore_check
        results['overall_score'] = min(results['overall_score'], gcore_check['score'])
        
        # 3. Check SEO optimization
        seo_check = self._check_seo_optimization(content, heading)
        results['checks']['seo'] = seo_check
        if seo_check['score'] < QUALITY_THRESHOLDS['min_seo_score']:
            results['warnings'].append(f"SEO score below threshold: {seo_check['score']}%")
        
        # 4. Check readability
        readability_check = self._check_readability(content)
        results['checks']['readability'] = readability_check
        
        # 5. Check pattern compliance
        if pattern_type:
            pattern_check = validate_pattern(content, heading)
            results['checks']['pattern_compliance'] = pattern_check
            if not pattern_check['valid']:
                results['issues'].extend(pattern_check['errors'])
                results['warnings'].extend(pattern_check.get('warnings', []))
        
        # 6. Check direct answer
        direct_answer_check = self._check_direct_answer(content, heading)
        results['checks']['direct_answer'] = direct_answer_check
        if not direct_answer_check['has_direct_answer']:
            results['issues'].append("Content doesn't directly answer the heading question")
            results['overall_score'] -= 20
        
        # 7. Check answer pattern compliance
        pattern_compliance = self._check_answer_pattern(content, heading, pattern_type)
        results['checks']['pattern_compliance'] = pattern_compliance
        if not pattern_compliance['compliant']:
            results['issues'].extend(pattern_compliance['issues'])
            results['overall_score'] -= 15
        
        # Calculate final score
        results['overall_score'] = max(0, results['overall_score'])
        
        # Generate suggestions
        results['suggestions'] = self._generate_suggestions(results)
        
        return results
    
    def _check_ai_words(self, content: str) -> Dict[str, Any]:
        """Check for AI-sounding words in content"""
        content_lower = content.lower()
        found_words = []
        word_positions = {}
        
        for ai_word in self.ai_blacklist:
            # Use word boundary regex to avoid partial matches
            pattern = r'\b' + re.escape(ai_word) + r'\b'
            matches = list(re.finditer(pattern, content_lower))
            if matches:
                found_words.append(ai_word)
                word_positions[ai_word] = [(m.start(), m.end()) for m in matches]
        
        return {
            'found': len(found_words) > 0,
            'count': len(found_words),
            'words': found_words,
            'positions': word_positions,
            'threshold_exceeded': len(found_words) > QUALITY_THRESHOLDS['max_ai_words']
        }
    
    def _check_competitor_mentions(self, content: str) -> Dict[str, Any]:
        """Check for competitor mentions (critical brand violation)"""
        competitors = [
            'AWS', 'Amazon Web Services', 'Amazon EC2', 'Amazon', 
            'Microsoft Azure', 'Azure GPU', 'Azure ML', 'Azure',
            'Google Cloud', 'Google Cloud Platform', 'GCP', 'Google',
            'Oracle Cloud', 'IBM Cloud', 'Alibaba Cloud', 'DigitalOcean',
            'Cloudflare', 'Fastly', 'Akamai', 'KeyCDN'
        ]
        
        found_competitors = []
        content_lower = content.lower()
        
        for competitor in competitors:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(competitor.lower()) + r'\b'
            if re.search(pattern, content_lower):
                # Find actual positions for reporting
                matches = list(re.finditer(pattern, content_lower))
                for match in matches:
                    found_competitors.append({
                        'competitor': competitor,
                        'position': match.start(),
                        'context': content[max(0, match.start()-30):match.end()+30]
                    })
        
        return {
            'found': len(found_competitors) > 0,
            'mentions': found_competitors,
            'count': len(found_competitors),
            'violation': len(found_competitors) > 0  # Any competitor mention is a violation
        }
    
    def _check_gcore_compliance(self, content: str) -> Dict[str, Any]:
        """Check compliance with Gcore brand guidelines"""
        score = 100
        issues = []
        
        guidelines = self.brand_guidelines.get('style_rules', {})
        
        # Check sentence length
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > guidelines.get('max_sentence_length', 30)]
        if long_sentences:
            score -= min(len(long_sentences) * 2, 20)
            issues.append(f"{len(long_sentences)} sentences exceed max length")
        
        # Check paragraph length
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > guidelines.get('max_paragraph_length', 150)]
        if long_paragraphs:
            score -= min(len(long_paragraphs) * 5, 15)
            issues.append(f"{len(long_paragraphs)} paragraphs exceed max length")
        
        # Check for Gcore context inclusion
        gcore_mentioned = any(term in content.lower() for term in ['gcore', '210+ pops', '30ms'])
        if not gcore_mentioned:
            issues.append("No Gcore-specific context included")
            score -= 10
        
        # Check terminology usage
        terminology = self.brand_guidelines.get('terminology', {})
        for avoid_term, suggestion in terminology.get('avoid', {}).items():
            if avoid_term.lower() in content.lower():
                issues.append(f"Avoid '{avoid_term}' - {suggestion}")
                score -= 5
        
        return {
            'score': max(0, score),
            'compliant': score >= QUALITY_THRESHOLDS['min_gcore_compliance'],
            'issues': issues
        }
    
    def _check_seo_optimization(self, content: str, heading: str) -> Dict[str, Any]:
        """Check SEO optimization of content"""
        score = 100
        issues = []
        metrics = {}
        
        # Extract primary keyword from heading
        primary_keyword = self._extract_keyword(heading)
        content_lower = content.lower()
        
        # Calculate keyword density
        if primary_keyword:
            keyword_count = content_lower.count(primary_keyword.lower())
            word_count = len(content.split())
            keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
            metrics['keyword_density'] = round(keyword_density, 2)
            
            # Check if keyword density is appropriate (2-3%)
            if keyword_density < 1:
                score -= 20
                issues.append("Keyword density too low")
            elif keyword_density > 5:
                score -= 15
                issues.append("Keyword density too high (keyword stuffing)")
        
        # Check if content starts with keyword/topic
        if primary_keyword and not content_lower[:100].count(primary_keyword.lower()):
            score -= 10
            issues.append("Primary keyword not in opening")
        
        # Check for semantic keywords
        semantic_keywords = self._get_semantic_keywords(primary_keyword)
        semantic_count = sum(1 for kw in semantic_keywords if kw in content_lower)
        metrics['semantic_keywords'] = semantic_count
        
        if semantic_count < 2:
            score -= 10
            issues.append("Insufficient semantic keywords")
        
        # Check content length
        if word_count < 100:
            score -= 20
            issues.append("Content too short for SEO")
        
        return {
            'score': max(0, score),
            'optimized': score >= QUALITY_THRESHOLDS['min_seo_score'],
            'metrics': metrics,
            'issues': issues
        }
    
    def _check_readability(self, content: str) -> Dict[str, Any]:
        """Check content readability"""
        # Simple readability metrics
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Count complex words (3+ syllables)
        complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
        complex_word_percentage = (complex_words / len(words)) * 100 if words else 0
        
        # Simple readability score
        readability_score = 100
        if avg_sentence_length > 20:
            readability_score -= 20
        if complex_word_percentage > 15:
            readability_score -= 15
        
        return {
            'score': readability_score,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'complex_word_percentage': round(complex_word_percentage, 1),
            'readable': readability_score >= QUALITY_THRESHOLDS['min_readability_score']
        }
    
    def _check_direct_answer(self, content: str, heading: str) -> Dict[str, Any]:
        """Check if content directly answers the heading question"""
        heading_lower = heading.lower().strip('?')
        content_start = content[:200].lower()
        
        # Special handling for "What are" questions (listicles)
        if heading_lower.startswith('what are '):
            # For listicles, check if it defines what the items are and mentions them
            has_definition = any(phrase in content_start for phrase in ['refer to', 'types', 'are', 'include'])
            has_list_intro = 'listed below' in content_start
            has_direct_answer = has_definition or has_list_intro
            
            return {
                'has_direct_answer': has_direct_answer,
                'key_terms_found': 1 if has_direct_answer else 0,
                'total_key_terms': 1
            }
        
        # Extract key terms from heading
        key_terms = [term for term in heading_lower.split() 
                    if term not in ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'does', 'do']]
        
        # Check if key terms appear in opening
        terms_found = sum(1 for term in key_terms if term in content_start)
        has_direct_answer = terms_found >= len(key_terms) * 0.5
        
        # Special checks for Yes/No questions
        if heading_lower.startswith(('is ', 'are ', 'can ', 'does ', 'do ', 'will ', 'should ')):
            has_direct_answer = content_start.startswith(('yes', 'no'))
        
        return {
            'has_direct_answer': has_direct_answer,
            'key_terms_found': terms_found,
            'total_key_terms': len(key_terms)
        }
    
    def _extract_keyword(self, heading: str) -> str:
        """Extract primary keyword from heading"""
        # Remove question words and get main topic
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'does', 'do']
        words = heading.lower().strip('?').split()
        keywords = [w for w in words if w not in question_words and len(w) > 3]
        return ' '.join(keywords[:2]) if keywords else heading.split()[-1]
    
    def _get_semantic_keywords(self, primary_keyword: str) -> List[str]:
        """Get semantic/related keywords"""
        # Simple semantic keyword generation
        semantic_map = {
            'cdn': ['content delivery', 'edge server', 'cache', 'latency', 'performance'],
            'edge': ['computing', 'distributed', 'latency', 'processing', 'infrastructure'],
            'cloud': ['infrastructure', 'scalable', 'virtual', 'computing', 'resources'],
            'cache': ['storage', 'performance', 'speed', 'memory', 'data'],
            'security': ['protection', 'ddos', 'firewall', 'encryption', 'threat']
        }
        
        keywords = []
        for key, related in semantic_map.items():
            if key in primary_keyword.lower():
                keywords.extend(related)
        
        return keywords[:5]  # Return top 5 semantic keywords
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple estimation)"""
        word = word.lower()
        vowels = 'aeiou'
        syllables = sum(1 for char in word if char in vowels)
        # Adjust for common patterns
        if word.endswith('e'):
            syllables -= 1
        if syllables == 0:
            syllables = 1
        return syllables
    
    def _check_answer_pattern(self, content: str, heading: str, pattern_type: str = None) -> Dict[str, Any]:
        """Check if content follows the correct answer pattern based on heading type"""
        issues = []
        compliant = True
        heading_lower = heading.lower().strip('?')
        content_start = content[:300].strip()
        
        # Check for What + singular pattern (should start with "X is...")
        if heading_lower.startswith('what is ') and ' are ' not in heading_lower:
            subject = heading_lower.replace('what is ', '').strip('?')
            expected_start = f"{subject} is"
            if not content_start.lower().startswith(expected_start):
                issues.append(f"Definition should start with '{subject.title()} is...'")
                compliant = False
        
        # Check for What + plural pattern (should have definition + "are listed below")
        elif heading_lower.startswith('what are '):
            items = heading_lower.replace('what are ', '').replace('the ', '').strip('?')
            content_lower = content_start.lower()
            
            # Check if it has the correct structure: definition of what items refer to + "are listed below"
            has_definition = any(phrase in content_lower[:150] for phrase in ['refer to', 'include', 'are', 'represent', 'types'])
            has_list_intro = 'are listed below' in content_lower[:200]
            
            if not (has_definition and has_list_intro):
                # Only flag if it doesn't follow the pattern at all
                if not has_list_intro and not has_definition:
                    issues.append(f"List should define what the {items} refer to, then say 'The {items} are listed below.'")
                    compliant = False
            
            # Check for bullet points
            if '•' not in content and '-' not in content[:500]:
                issues.append("List format requires bullet points")
                compliant = False
        
        # Check for Yes/No questions
        elif any(heading_lower.startswith(q) for q in ['is ', 'are ', 'can ', 'does ', 'do ', 'will ', 'should ']):
            if not content_start.startswith(('Yes,', 'No,')):
                issues.append("Yes/No questions must start with 'Yes,' or 'No,' followed by the answer")
                compliant = False
        
        # Check for How does/do pattern
        elif heading_lower.startswith(('how does ', 'how do ')):
            subject = re.sub(r'^how (does?|do) ', '', heading_lower).strip('?')
            if 'works by' not in content_start.lower() and 'work by' not in content_start.lower():
                issues.append(f"Should explain how '{subject}' works by...")
                compliant = False
        
        # Check for How to pattern
        elif heading_lower.startswith('how to '):
            action = heading_lower.replace('how to ', '').strip('?')
            if not any(phrase in content_start.lower() for phrase in [f"you {action}", f"to {action}", action[:20]]):
                issues.append(f"Instructions should start by restating the action: 'You {action} by...'")
                compliant = False
            # Check for numbered steps
            if not any(marker in content for marker in ['1.', '2.', 'First,', 'Step 1']):
                issues.append("How-to content should include numbered steps or transition words")
                compliant = False
        
        # Check for statistics questions (How common/often/many)
        elif any(word in heading_lower for word in ['how common', 'how often', 'how many', 'how much']):
            # Check if first sentence contains numbers
            first_sentence = content_start.split('.')[0] if '.' in content_start else content_start[:100]
            if not re.search(r'\d+', first_sentence):
                issues.append("Statistical answers should include numbers in the first sentence")
                compliant = False
        
        return {
            'compliant': compliant,
            'issues': issues,
            'pattern_type': pattern_type or 'detected'
        }
    
    def _generate_suggestions(self, check_results: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on check results"""
        suggestions = []
        
        # AI words suggestions
        if check_results['checks'].get('ai_words', {}).get('found'):
            ai_words = check_results['checks']['ai_words']['words']
            suggestions.append(f"Replace AI words: {', '.join(ai_words[:3])}")
        
        # SEO suggestions
        seo_check = check_results['checks'].get('seo', {})
        if seo_check.get('metrics', {}).get('keyword_density', 0) < 1:
            suggestions.append("Increase keyword usage in content")
        
        # Readability suggestions
        readability = check_results['checks'].get('readability', {})
        if readability.get('avg_sentence_length', 0) > 20:
            suggestions.append("Shorten sentences for better readability")
        
        # Direct answer suggestions
        if not check_results['checks'].get('direct_answer', {}).get('has_direct_answer'):
            suggestions.append("Start with a direct answer to the heading question")
        
        return suggestions
    
    def fix_ai_words(self, content: str) -> Tuple[str, List[str]]:
        """Replace AI words with natural alternatives using shared replacements"""
        fixed_content = content
        replaced_words = []
        
        # Use the loaded replacements from the JSON file
        for ai_word, replacement in self.ai_replacements.items():
            pattern = r'\b' + re.escape(ai_word) + r'\b'
            if re.search(pattern, fixed_content, re.IGNORECASE):
                fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.IGNORECASE)
                replaced_words.append(f"{ai_word} → {replacement}")
        
        return fixed_content, replaced_words

# Convenience functions
def check_content_quality(content: str, heading: str) -> Dict[str, Any]:
    """Check content quality"""
    checker = QualityChecker()
    return checker.check_quality(content, heading)

def fix_ai_words(content: str) -> Tuple[str, List[str]]:
    """Fix AI words in content"""
    checker = QualityChecker()
    return checker.fix_ai_words(content)