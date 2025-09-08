"""
Content Editor with Rich Text Highlighting and Suggestions
Provides interactive editing capabilities for quality improvement
"""

import re
from typing import Dict, List, Tuple, Optional, Any
import difflib

class ContentEditor:
    """Enhanced content editor with issue highlighting and suggestions"""
    
    def __init__(self):
        self.ai_word_replacements = self._load_replacement_dictionary()
        self.highlight_colors = {
            'ai_word': '#ff6b6b',  # Red for AI words
            'long_sentence': '#ffd93d',  # Yellow for long sentences
            'passive_voice': '#6bcf7f',  # Green for passive voice
            'missing_answer': '#4dabf7',  # Blue for missing direct answer
            'promotional': '#e599f7'  # Purple for promotional content
        }
    
    def _load_replacement_dictionary(self) -> Dict[str, List[str]]:
        """Load AI word replacements"""
        return {
            'leverage': ['use', 'apply', 'employ'],
            'leveraging': ['using', 'applying', 'employing'],
            'utilize': ['use', 'apply', 'work with'],
            'utilizing': ['using', 'applying', 'working with'],
            'utilization': ['use', 'usage', 'application'],
            'delve': ['explore', 'examine', 'look into'],
            'delving': ['exploring', 'examining', 'looking into'],
            'moreover': ['also', 'additionally', 'plus'],
            'furthermore': ['also', 'additionally', 'in addition'],
            'notably': ['especially', 'particularly', 'specifically'],
            'essentially': ['basically', 'mainly', 'primarily'],
            'whilst': ['while', 'although', 'whereas'],
            'thus': ['so', 'therefore', 'as a result'],
            'hence': ['so', 'therefore', 'for this reason'],
            'thereby': ['thus', 'so', 'in this way'],
            'aforementioned': ['mentioned', 'previous', 'above'],
            'revolutionize': ['transform', 'change', 'improve'],
            'revolutionary': ['innovative', 'new', 'transformative'],
            'cutting-edge': ['advanced', 'modern', 'latest'],
            'state-of-the-art': ['advanced', 'modern', 'current'],
            'intricate': ['complex', 'detailed', 'involved'],
            'intricacies': ['details', 'complexities', 'aspects'],
            'subsequently': ['then', 'after', 'later'],
            'consequently': ['so', 'therefore', 'as a result'],
            'predominantly': ['mainly', 'mostly', 'primarily'],
            'significantly': ['greatly', 'much', 'considerably']
        }
    
    def highlight_issues(self, content: str, issues: Dict[str, Any]) -> str:
        """
        Add HTML highlighting to content based on identified issues
        
        Args:
            content: Original content text
            issues: Dictionary of identified issues from quality checker
            
        Returns:
            HTML-formatted content with highlights
        """
        html_content = content
        
        # Escape HTML special characters first
        html_content = html_content.replace('&', '&amp;')
        html_content = html_content.replace('<', '&lt;')
        html_content = html_content.replace('>', '&gt;')
        
        # Highlight AI words
        if issues.get('ai_words', {}).get('words'):
            for word in issues['ai_words']['words']:
                pattern = r'\b' + re.escape(word) + r'\b'
                replacement = f'<span style="background-color: {self.highlight_colors["ai_word"]}; padding: 2px 4px; border-radius: 3px; cursor: pointer;" title="AI word - click for suggestions" data-word="{word}" class="ai-word">{word}</span>'
                html_content = re.sub(pattern, replacement, html_content, flags=re.IGNORECASE)
        
        # Highlight long sentences (>30 words)
        sentences = re.split(r'(?<=[.!?])\s+', html_content)
        for sentence in sentences:
            word_count = len(sentence.split())
            if word_count > 30:
                highlighted = f'<span style="border-bottom: 2px wavy {self.highlight_colors["long_sentence"]};" title="Long sentence ({word_count} words) - consider breaking up">{sentence}</span>'
                html_content = html_content.replace(sentence, highlighted)
        
        # Convert line breaks to HTML
        html_content = html_content.replace('\n\n', '</p><p>')
        html_content = html_content.replace('\n', '<br>')
        html_content = f'<p>{html_content}</p>'
        
        # Add CSS for hover effects
        css = """
        <style>
        .ai-word:hover {
            opacity: 0.8;
            text-decoration: underline;
        }
        .suggestion-tooltip {
            position: absolute;
            background: white;
            border: 1px solid #ccc;
            padding: 8px;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        </style>
        """
        
        return css + html_content
    
    def suggest_replacements(self, word: str) -> List[str]:
        """
        Get replacement suggestions for an AI word
        
        Args:
            word: The AI word to replace
            
        Returns:
            List of suggested replacements
        """
        word_lower = word.lower()
        
        # Direct match
        if word_lower in self.ai_word_replacements:
            return self.ai_word_replacements[word_lower]
        
        # Try removing common suffixes to find base word
        suffixes = ['ing', 'ed', 's', 'es', 'ly', 'tion', 'ize', 'ise']
        for suffix in suffixes:
            if word_lower.endswith(suffix):
                base = word_lower[:-len(suffix)]
                if base in self.ai_word_replacements:
                    # Adapt replacements to match suffix if possible
                    base_replacements = self.ai_word_replacements[base]
                    if suffix == 'ing':
                        return [r + 'ing' if not r.endswith('e') else r[:-1] + 'ing' for r in base_replacements[:2]]
                    elif suffix == 'ed':
                        return [r + 'ed' if not r.endswith('e') else r + 'd' for r in base_replacements[:2]]
                    else:
                        return base_replacements
        
        # No replacements found
        return []
    
    def apply_fix(self, content: str, fix_type: str, target: str = None, replacement: str = None) -> str:
        """
        Apply a specific fix to the content
        
        Args:
            content: Original content
            fix_type: Type of fix to apply
            target: Target word/phrase to replace
            replacement: Replacement text
            
        Returns:
            Fixed content
        """
        if fix_type == 'replace_word' and target and replacement:
            # Replace specific word
            pattern = r'\b' + re.escape(target) + r'\b'
            return re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        elif fix_type == 'remove_all_ai_words':
            # Replace all AI words with first suggestion
            for ai_word, suggestions in self.ai_word_replacements.items():
                if suggestions:
                    pattern = r'\b' + re.escape(ai_word) + r'\b'
                    content = re.sub(pattern, suggestions[0], content, flags=re.IGNORECASE)
            return content
        
        elif fix_type == 'split_long_sentences':
            # Split sentences over 30 words
            sentences = re.split(r'(?<=[.!?])\s+', content)
            fixed_sentences = []
            
            for sentence in sentences:
                words = sentence.split()
                if len(words) > 30:
                    # Find a good split point (around middle, at a comma or conjunction)
                    mid_point = len(words) // 2
                    split_index = mid_point
                    
                    # Look for comma or conjunction near middle
                    for i in range(max(0, mid_point - 5), min(len(words), mid_point + 5)):
                        if words[i].endswith(',') or words[i].lower() in ['and', 'but', 'or', 'which', 'that']:
                            split_index = i + 1
                            break
                    
                    # Split the sentence
                    first_part = ' '.join(words[:split_index])
                    second_part = ' '.join(words[split_index:])
                    
                    # Ensure proper capitalization
                    if second_part:
                        second_part = second_part[0].upper() + second_part[1:]
                    
                    # Add period if missing
                    if first_part and not first_part[-1] in '.!?':
                        first_part += '.'
                    
                    fixed_sentences.append(first_part)
                    if second_part:
                        fixed_sentences.append(second_part)
                else:
                    fixed_sentences.append(sentence)
            
            return ' '.join(fixed_sentences)
        
        elif fix_type == 'remove_promotional':
            # Remove promotional language about Gcore
            promotional_patterns = [
                r"Gcore's\s+industry-leading[^.]*\.",
                r"Choose Gcore for[^.]*\.",
                r"Gcore is the best[^.]*\.",
                r"With Gcore, you get[^.]*\.",
                r"Gcore offers[^.]*\.",
                r"Gcore provides[^.]*\."
            ]
            
            for pattern in promotional_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE)
            
            # Clean up double spaces
            content = re.sub(r'\s+', ' ', content)
            return content.strip()
        
        return content
    
    def get_diff(self, original: str, edited: str) -> List[Tuple[str, str]]:
        """
        Get a diff between original and edited content
        
        Args:
            original: Original content
            edited: Edited content
            
        Returns:
            List of (change_type, text) tuples
        """
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            edited.splitlines(keepends=True),
            lineterm=''
        )
        
        changes = []
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                changes.append(('added', line[1:]))
            elif line.startswith('-') and not line.startswith('---'):
                changes.append(('removed', line[1:]))
            elif not line.startswith(('+++', '---', '@@')):
                changes.append(('unchanged', line))
        
        return changes
    
    def calculate_improvement_score(self, original_issues: Dict, current_issues: Dict) -> float:
        """
        Calculate improvement score between original and current issues
        
        Args:
            original_issues: Original quality issues
            current_issues: Current quality issues
            
        Returns:
            Improvement percentage
        """
        original_score = original_issues.get('overall_score', 0)
        current_score = current_issues.get('overall_score', 0)
        
        if original_score == 0:
            return 0.0
        
        improvement = ((current_score - original_score) / original_score) * 100
        return round(improvement, 1)
    
    def batch_fix_content(self, content: str, fix_types: List[str]) -> str:
        """
        Apply multiple fixes to content in sequence
        
        Args:
            content: Original content
            fix_types: List of fix types to apply
            
        Returns:
            Fixed content
        """
        fixed_content = content
        
        for fix_type in fix_types:
            fixed_content = self.apply_fix(fixed_content, fix_type)
        
        return fixed_content
    
    def analyze_sentence_structure(self, content: str) -> Dict[str, Any]:
        """
        Analyze sentence structure for readability
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with sentence analysis
        """
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        analysis = {
            'total_sentences': len(sentences),
            'long_sentences': [],
            'short_sentences': [],
            'average_length': 0,
            'variety_score': 0
        }
        
        word_counts = []
        
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            word_count = len(words)
            word_counts.append(word_count)
            
            if word_count > 30:
                analysis['long_sentences'].append({
                    'index': i,
                    'text': sentence[:50] + '...' if len(sentence) > 50 else sentence,
                    'word_count': word_count
                })
            elif word_count < 10 and word_count > 0:
                analysis['short_sentences'].append({
                    'index': i,
                    'text': sentence,
                    'word_count': word_count
                })
        
        if word_counts:
            analysis['average_length'] = sum(word_counts) / len(word_counts)
            # Calculate variety score (standard deviation)
            mean = analysis['average_length']
            variance = sum((x - mean) ** 2 for x in word_counts) / len(word_counts)
            analysis['variety_score'] = variance ** 0.5
        
        return analysis
    
    def suggest_improvements(self, content: str, issues: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate specific improvement suggestions based on issues
        
        Args:
            content: Content to improve
            issues: Identified issues
            
        Returns:
            List of improvement suggestions with actions
        """
        suggestions = []
        
        # Check for AI words
        if issues.get('ai_words', {}).get('words'):
            ai_words = issues['ai_words']['words']
            suggestions.append({
                'type': 'ai_words',
                'severity': 'high',
                'message': f'Found {len(ai_words)} AI-sounding words',
                'action': 'Click on highlighted words for replacements',
                'quick_fix': 'remove_all_ai_words'
            })
        
        # Check sentence structure
        sentence_analysis = self.analyze_sentence_structure(content)
        if sentence_analysis['long_sentences']:
            suggestions.append({
                'type': 'readability',
                'severity': 'medium',
                'message': f'{len(sentence_analysis["long_sentences"])} sentences over 30 words',
                'action': 'Break up long sentences for better readability',
                'quick_fix': 'split_long_sentences'
            })
        
        # Check for promotional content
        if re.search(r"Gcore's\s+industry-leading|Choose Gcore|Gcore is the best", content, re.IGNORECASE):
            suggestions.append({
                'type': 'promotional',
                'severity': 'high',
                'message': 'Contains promotional language',
                'action': 'Remove promotional phrases',
                'quick_fix': 'remove_promotional'
            })
        
        # Check for direct answer (for certain patterns)
        first_sentence = content.split('.')[0] if '.' in content else content[:100]
        if not any(starter in first_sentence.lower() for starter in ['is', 'are', 'refers to', 'means', 'yes', 'no']):
            suggestions.append({
                'type': 'structure',
                'severity': 'medium',
                'message': 'May not directly answer the heading',
                'action': 'Start with a direct answer to the question',
                'quick_fix': None
            })
        
        return suggestions
    
    def compare_content_versions(self,
                                original: str,
                                optimized: str,
                                heading: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare original and optimized content versions
        
        Args:
            original: Original content
            optimized: Optimized content
            heading: Optional section heading
            
        Returns:
            Comparison results with metrics and visualization
        """
        comparison = {
            'original': {
                'content': original,
                'word_count': len(original.split()),
                'sentence_count': len(re.split(r'[.!?]+', original)),
                'quality_issues': {}
            },
            'optimized': {
                'content': optimized,
                'word_count': len(optimized.split()),
                'sentence_count': len(re.split(r'[.!?]+', optimized)),
                'quality_issues': {}
            },
            'improvements': {},
            'similarity': 0,
            'change_type': '',
            'diff_html': ''
        }
        
        # Check quality of both versions
        from core.quality_checker import QualityChecker
        checker = QualityChecker()
        
        comparison['original']['quality_issues'] = checker.check_content_quality(
            original, {'text': heading or 'Content'}
        )
        comparison['optimized']['quality_issues'] = checker.check_content_quality(
            optimized, {'text': heading or 'Content'}
        )
        
        # Calculate improvements
        orig_score = comparison['original']['quality_issues'].get('overall_score', 0)
        opt_score = comparison['optimized']['quality_issues'].get('overall_score', 0)
        
        comparison['improvements'] = {
            'quality_score': opt_score - orig_score,
            'word_count_change': comparison['optimized']['word_count'] - comparison['original']['word_count'],
            'ai_words_removed': len(comparison['original']['quality_issues'].get('ai_words', {}).get('words', [])) - 
                               len(comparison['optimized']['quality_issues'].get('ai_words', {}).get('words', [])),
            'readability_improvement': self._calculate_readability_improvement(original, optimized)
        }
        
        # Calculate similarity
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, original, optimized).ratio()
        comparison['similarity'] = round(similarity * 100, 1)
        
        # Determine change type
        if similarity > 0.9:
            comparison['change_type'] = 'minor_edits'
        elif similarity > 0.7:
            comparison['change_type'] = 'moderate_changes'
        elif similarity > 0.5:
            comparison['change_type'] = 'significant_changes'
        else:
            comparison['change_type'] = 'complete_rewrite'
        
        # Generate diff HTML
        comparison['diff_html'] = self.generate_diff_html(original, optimized)
        
        return comparison
    
    def _calculate_readability_improvement(self, original: str, optimized: str) -> float:
        """
        Calculate readability improvement between versions
        
        Args:
            original: Original text
            optimized: Optimized text
            
        Returns:
            Readability improvement percentage
        """
        # Simple readability metrics
        def get_readability_score(text):
            sentences = re.split(r'[.!?]+', text)
            words = text.split()
            
            if not sentences or not words:
                return 0
            
            avg_sentence_length = len(words) / len(sentences)
            complex_words = len([w for w in words if len(w) > 8])
            
            # Simple readability formula (lower is better)
            score = avg_sentence_length + (complex_words / len(words) * 100)
            return score
        
        original_score = get_readability_score(original)
        optimized_score = get_readability_score(optimized)
        
        if original_score == 0:
            return 0
        
        # Lower scores are better, so improvement is negative change
        improvement = ((original_score - optimized_score) / original_score) * 100
        return round(improvement, 1)
    
    def generate_diff_html(self, original: str, optimized: str) -> str:
        """
        Generate HTML visualization of content differences
        
        Args:
            original: Original content
            optimized: Optimized content
            
        Returns:
            HTML string with highlighted differences
        """
        from difflib import unified_diff
        import html
        
        # Split into sentences for better diff granularity
        original_sentences = re.split(r'(?<=[.!?])\s+', original)
        optimized_sentences = re.split(r'(?<=[.!?])\s+', optimized)
        
        diff = unified_diff(original_sentences, optimized_sentences, lineterm='')
        
        html_parts = ['<div class="content-diff" style="font-family: monospace; line-height: 1.6;">']
        
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                continue
            elif line.startswith('@@'):
                html_parts.append(f'<div style="color: #666; margin: 10px 0;">{html.escape(line)}</div>')
            elif line.startswith('+'):
                html_parts.append(
                    f'<div style="background-color: #d4edda; padding: 5px; margin: 2px 0; border-left: 3px solid #28a745;">'
                    f'<span style="color: #155724;">+ {html.escape(line[1:])}</span></div>'
                )
            elif line.startswith('-'):
                html_parts.append(
                    f'<div style="background-color: #f8d7da; padding: 5px; margin: 2px 0; border-left: 3px solid #dc3545;">'
                    f'<span style="color: #721c24;">- {html.escape(line[1:])}</span></div>'
                )
            else:
                html_parts.append(f'<div style="padding: 5px; margin: 2px 0;">{html.escape(line)}</div>')
        
        html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def create_side_by_side_view(self,
                                 original: str,
                                 optimized: str,
                                 highlights: bool = True) -> str:
        """
        Create side-by-side comparison view
        
        Args:
            original: Original content
            optimized: Optimized content
            highlights: Whether to highlight changes
            
        Returns:
            HTML for side-by-side view
        """
        html = """
        <div style="display: flex; gap: 20px; font-family: sans-serif;">
            <div style="flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                <h3 style="margin-top: 0; color: #dc3545;">Original Content</h3>
                <div style="line-height: 1.6;">"""
        
        if highlights:
            # Highlight AI words in original
            highlighted_original = self._highlight_text_issues(original, 'original')
            html += highlighted_original
        else:
            html += f'<p>{original}</p>'
        
        html += """
                </div>
            </div>
            <div style="flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                <h3 style="margin-top: 0; color: #28a745;">Optimized Content</h3>
                <div style="line-height: 1.6;">"""
        
        if highlights:
            # Highlight improvements in optimized
            highlighted_optimized = self._highlight_text_issues(optimized, 'optimized')
            html += highlighted_optimized
        else:
            html += f'<p>{optimized}</p>'
        
        html += """
                </div>
            </div>
        </div>
        """
        
        return html
    
    def _highlight_text_issues(self, text: str, version: str) -> str:
        """
        Highlight text issues for comparison
        
        Args:
            text: Text to highlight
            version: 'original' or 'optimized'
            
        Returns:
            HTML with highlighted issues
        """
        import html
        
        # Escape HTML
        text = html.escape(text)
        
        # Highlight AI words differently for each version
        ai_words = list(self.ai_word_replacements.keys())
        
        for word in ai_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            if version == 'original':
                # Red highlight for original
                replacement = f'<span style="background-color: #ffcccc; padding: 2px 4px; border-radius: 3px;">{word}</span>'
            else:
                # Green if removed, yellow if still present
                if re.search(pattern, text, re.IGNORECASE):
                    replacement = f'<span style="background-color: #fff3cd; padding: 2px 4px; border-radius: 3px;">{word}</span>'
                else:
                    continue
            
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Convert line breaks to HTML
        text = text.replace('\n\n', '</p><p>').replace('\n', '<br>')
        text = f'<p>{text}</p>'
        
        return text
    
    def generate_optimization_summary(self, comparison_results: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of all optimizations made
        
        Args:
            comparison_results: List of comparison results for each section
            
        Returns:
            HTML summary of optimizations
        """
        total_original_words = sum(r['original']['word_count'] for r in comparison_results)
        total_optimized_words = sum(r['optimized']['word_count'] for r in comparison_results)
        
        total_quality_improvement = sum(r['improvements']['quality_score'] for r in comparison_results)
        avg_quality_improvement = total_quality_improvement / len(comparison_results) if comparison_results else 0
        
        total_ai_words_removed = sum(r['improvements']['ai_words_removed'] for r in comparison_results)
        
        change_types_count = {}
        for r in comparison_results:
            change_type = r['change_type']
            change_types_count[change_type] = change_types_count.get(change_type, 0) + 1
        
        html = f"""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; font-family: sans-serif;">
            <h2 style="margin-top: 0; color: #333;">Content Optimization Summary</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
                    <div style="color: #666; font-size: 14px;">Word Count</div>
                    <div style="font-size: 24px; font-weight: bold; color: #333;">
                        {total_original_words} → {total_optimized_words}
                    </div>
                    <div style="color: {'#28a745' if total_optimized_words > total_original_words else '#dc3545'}; font-size: 14px;">
                        {'+' if total_optimized_words > total_original_words else ''}{total_optimized_words - total_original_words} words
                    </div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
                    <div style="color: #666; font-size: 14px;">Quality Score</div>
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">
                        +{avg_quality_improvement:.1f}%
                    </div>
                    <div style="color: #666; font-size: 14px;">Average improvement</div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
                    <div style="color: #666; font-size: 14px;">AI Words Removed</div>
                    <div style="font-size: 24px; font-weight: bold; color: #333;">
                        {total_ai_words_removed}
                    </div>
                    <div style="color: #666; font-size: 14px;">Total removed</div>
                </div>
            </div>
            
            <h3 style="color: #333; margin-top: 25px;">Change Distribution</h3>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
        """
        
        change_type_labels = {
            'minor_edits': ('Minor Edits', '#17a2b8'),
            'moderate_changes': ('Moderate Changes', '#ffc107'),
            'significant_changes': ('Significant Changes', '#fd7e14'),
            'complete_rewrite': ('Complete Rewrite', '#dc3545')
        }
        
        for change_type, count in change_types_count.items():
            label, color = change_type_labels.get(change_type, (change_type, '#6c757d'))
            html += f"""
                <div style="background: {color}; color: white; padding: 8px 15px; border-radius: 20px; font-size: 14px;">
                    {label}: {count}
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html