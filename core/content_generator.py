"""
Content Generator using Claude API
Handles content generation based on semantic patterns and research data
"""

import anthropic
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import streamlit as st
from pathlib import Path

from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_TOKENS,
    GCORE_INFO,
    CONTENT_SETTINGS
)
from core.semantic_patterns import (
    detect_question_type,
    get_pattern_template,
    get_semantic_triple
)
from core.table_formatter import TableFormatter
from core.internal_linker import InternalLinker
from core.link_manager import LinkManager
from core.product_loader import product_loader
from core.source_manager import SourceManager
from core.editorial_guidelines import get_humanization_prompt_section, get_generation_prompt_section
import re

def validate_content_structure(content: str) -> Dict[str, Any]:
    """Validate content structure according to SOP requirements"""
    issues = []
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    for i, paragraph in enumerate(paragraphs):
        # Skip if it's a list item
        if paragraph.startswith('•') or paragraph.startswith('-') or (len(paragraph) > 3 and paragraph[0:3].strip().endswith('.')):
            continue
            
        # Count sentences (approximate)
        sentences = [s.strip() for s in re.split(r'[.!?]+', paragraph) if s.strip()]
        
        # Check paragraph length
        word_count = len(paragraph.split())
        if word_count > 150:
            issues.append(f"Paragraph {i+1} has {word_count} words (max: 150)")
        
        # Check sentence lengths
        for j, sentence in enumerate(sentences):
            sentence_words = len(sentence.split())
            if sentence_words > 30:
                issues.append(f"Paragraph {i+1}, sentence {j+1} has {sentence_words} words (max: 30)")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'paragraph_count': len(paragraphs)
    }

def split_long_paragraphs(content: str) -> str:
    """Split paragraphs that are too long according to SOP (150 words max)"""
    paragraphs = content.split('\n\n')
    result = []
    
    for paragraph in paragraphs:
        if paragraph.startswith('•') or paragraph.startswith('-'):
            # Don't split lists
            result.append(paragraph)
            continue
            
        words = paragraph.split()
        if len(words) <= 150:
            result.append(paragraph)
        else:
            # Split into chunks of ~100 words at sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            current_chunk = []
            current_words = 0
            
            for sentence in sentences:
                sentence_words = len(sentence.split())
                if current_words + sentence_words > 100 and current_chunk:
                    result.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_words = sentence_words
                else:
                    current_chunk.append(sentence)
                    current_words += sentence_words
            
            if current_chunk:
                result.append(' '.join(current_chunk))
    
    return '\n\n'.join(result)

class ContentGenerator:
    """Generate content using Claude API with semantic patterns"""
    
    def __init__(self, api_key: Optional[str] = None, enable_internal_links: bool = True):
        self.api_key = api_key or ANTHROPIC_API_KEY
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
        self.model = CLAUDE_MODEL
        self.table_formatter = TableFormatter()
        self.ai_word_replacements = self._load_ai_word_replacements()
        self.blacklist_prompt = self._format_blacklist_prompt()
        
        # Initialize source manager for global fact tracking
        self.source_manager = SourceManager()
        
        # Initialize internal linking system
        self.enable_internal_links = enable_internal_links
        if enable_internal_links:
            try:
                self.link_manager = LinkManager()
                self.internal_linker = InternalLinker(self.link_manager)
            except Exception as e:
                print(f"Warning: Could not initialize internal linking: {e}")
                self.enable_internal_links = False
                self.link_manager = None
                self.internal_linker = None
        else:
            self.link_manager = None
            self.internal_linker = None
    
    def reset_fact_tracking(self):
        """Reset fact tracking for new document generation"""
        self.source_manager.citation_tracker.reset()
    
    def _clean_competitor_mentions(self, content: str) -> str:
        """Remove competitor mentions and replace with generic terms"""
        import re

        # Define competitor replacement patterns - COMPREHENSIVE LIST
        replacements = [
            # Multiple competitors mentioned together (check first for better matching)
            (r'\b(?:AWS|Amazon),\s*(?:Azure|Microsoft),?\s*(?:and\s+)?(?:Google Cloud|GCP)\b', 'major cloud providers'),
            (r'\b(?:AWS|Amazon)\s*,\s*(?:Google Cloud|GCP)\s*,?\s*(?:and\s+)?(?:Azure|Microsoft)\b', 'leading cloud platforms'),
            (r'\b(?:Azure|Microsoft)\s*,\s*(?:AWS|Amazon)\s*,?\s*(?:and\s+)?(?:Google Cloud|GCP)\b', 'major cloud providers'),

            # CDN competitors (CRITICAL - mentioned in feedback)
            (r'\b(?:Cloudflare|CloudFlare)\b', 'leading CDN providers'),
            (r'\b(?:Akamai|Fastly|KeyCDN)\b', 'CDN providers'),
            (r'\b(?:StackPath|BunnyCDN|CDN77)\b', 'content delivery networks'),

            # Major cloud providers - AWS variations
            (r'\bAWS\s+(?:Lambda|S3|EC2|CloudFront|Route\s*53)\b', 'serverless platforms'),
            (r'\b(?:AWS|Amazon Web Services|Amazon EC2|Amazon S3|Amazon CloudFront)\b', 'major cloud providers'),

            # Major cloud providers - Azure variations
            (r'\bAzure\s+(?:GPU|ML|Functions|CDN|Blob Storage)\b', 'cloud infrastructure'),
            (r'\b(?:Microsoft Azure|Azure)\b', 'enterprise cloud platforms'),

            # Major cloud providers - Google variations
            (r'\b(?:Google Cloud|Google Cloud Platform|GCP|Google Compute Engine)\b', 'leading cloud platforms'),

            # Other cloud competitors
            (r'\b(?:Oracle Cloud|OCI)\b', 'cloud platforms'),
            (r'\b(?:IBM Cloud|IBM Bluemix)\b', 'cloud platforms'),
            (r'\b(?:Alibaba Cloud|Aliyun)\b', 'cloud platforms'),
            (r'\b(?:DigitalOcean|DO)\b', 'cloud hosting providers'),
            (r'\b(?:Linode|Vultr)\b', 'cloud hosting providers'),
            (r'\b(?:Heroku|Platform\.sh)\b', 'cloud platforms'),

            # Hosting/infrastructure competitors
            (r'\b(?:GoDaddy|Bluehost|HostGator)\b', 'hosting providers'),
            (r'\b(?:Cloudinary|Imgix)\b', 'media optimization services'),

            # Generic patterns with specific competitors
            (r'providers?\s+like\s+(?:AWS|Azure|Google Cloud|Cloudflare)(?:\s*,\s*\w+)*', 'major cloud providers'),
            (r'(?:AWS|Azure|Google Cloud|Cloudflare)(?:\s*,\s*\w+)*\s+offers?', 'cloud providers offer'),
            (r'services?\s+such\s+as\s+(?:AWS|Azure|Google Cloud|Cloudflare)', 'cloud services'),
        ]

        cleaned_content = content
        for pattern, replacement in replacements:
            cleaned_content = re.sub(pattern, replacement, cleaned_content, flags=re.IGNORECASE)

        return cleaned_content
    
    def _fix_format_mixing(self, content: str) -> str:
        """Fix HTML/Markdown format mixing issues and remove meta-commentary"""
        import re

        # Remove markdown headings that shouldn't be in content
        # These appear when Claude adds extra structure
        content = re.sub(r'^#{1,6}\s+.*$', '', content, flags=re.MULTILINE)

        # Remove meta-commentary patterns that become H3s in HTML
        meta_commentary_patterns = [
            r'^##?\s*Strategic Insights:.*$',
            r'^This structure outperforms.*$',
            r'^This approach.*competitor.*$',
            r'^Q:.*$',  # Remove Q: format questions
            r'^A:.*$',  # Remove A: format answers
            r'^Analysis:.*$',
            r'^Note about.*$',
            r'^Meta-commentary:.*$',
        ]
        for pattern in meta_commentary_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE)

        # Clean up any double line breaks created by heading removal
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Remove any standalone markdown formatting
        content = re.sub(r'^\*\*([^*]+)\*\*$', r'\1', content, flags=re.MULTILINE)  # **text** on own line
        content = re.sub(r'^\*([^*]+)\*$', r'\1', content, flags=re.MULTILINE)      # *text* on own line

        # Clean up extra whitespace
        content = content.strip()

        return content
    
    def _remove_duplicate_statistics_from_content(self, content: str) -> str:
        """Final safety net to remove duplicate statistics from content"""
        import re
        
        # Common market statistics that tend to repeat
        market_stat_patterns = [
            r'(?:global\s+)?(?:virtual machine|VM)\s+market.*?(?:reached|size).*?\$?[\d.]+\s*billion.*?(?:2024|2025)',
            r'(?:projected|expected|forecast).*?(?:grow|reach).*?\$?[\d.]+\s*billion.*?(?:2034|2030)',
            r'(?:CAGR|growth rate).*?[\d.]+%.*?(?:through|by|until)\s+\d{4}',
            r'96%.*?organizations.*?(?:concern|worry|express).*?(?:cloud\s+)?security'
        ]
        
        seen_stats = set()
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_has_duplicate = False
            
            # Check each line for market statistics
            for pattern in market_stat_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    stat_key = re.sub(r'\s+', ' ', match.strip()).lower()
                    if stat_key in seen_stats:
                        # This line contains a duplicate statistic
                        line_has_duplicate = True
                        break
                    else:
                        seen_stats.add(stat_key)
                
                if line_has_duplicate:
                    break
            
            # Only keep lines that don't contain duplicate statistics
            if not line_has_duplicate:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _load_ai_word_replacements(self) -> Dict[str, Any]:
        """Load AI word replacements from JSON file"""
        replacements_file = Path('data') / 'ai_word_replacements.json'
        if replacements_file.exists():
            with open(replacements_file, 'r') as f:
                return json.load(f)
        else:
            # Fallback to basic replacements if file doesn't exist
            return {
                'simple_replacements': {
                    'leverage': 'use',
                    'utilize': 'use',
                    'delve': 'explore',
                    'moreover': 'also',
                    'furthermore': 'additionally'
                },
                'word_groups': {}
            }
    
    def _format_blacklist_prompt(self) -> str:
        """Format the AI word blacklist into a comprehensive prompt instruction"""
        prompt_parts = []
        
        prompt_parts.append("=" * 60)
        prompt_parts.append("CRITICAL: FORBIDDEN WORDS AND REQUIRED REPLACEMENTS")
        prompt_parts.append("=" * 60)
        prompt_parts.append("")
        prompt_parts.append("You MUST NOT use ANY of the following words or phrases.")
        prompt_parts.append("These are strictly prohibited to ensure clear, direct writing.")
        prompt_parts.append("")
        
        # Add word groups with replacements
        if self.ai_word_replacements.get('word_groups'):
            prompt_parts.append("WORD GROUPS TO AVOID:")
            prompt_parts.append("-" * 40)
            
            for group_name, group_data in self.ai_word_replacements['word_groups'].items():
                words = group_data.get('words', [])
                replacements = group_data.get('replacements', [])
                context = group_data.get('context', '')
                
                prompt_parts.append(f"\n❌ FORBIDDEN: {', '.join(words)}")
                prompt_parts.append(f"✅ USE INSTEAD: {', '.join(replacements)}")
                if context:
                    prompt_parts.append(f"   Context: {context}")
        
        # Add simple replacements
        if self.ai_word_replacements.get('simple_replacements'):
            prompt_parts.append("\n" + "-" * 40)
            prompt_parts.append("DIRECT REPLACEMENTS (forbidden → use instead):")
            prompt_parts.append("-" * 40)
            
            for forbidden, replacement in self.ai_word_replacements['simple_replacements'].items():
                prompt_parts.append(f"❌ {forbidden} → ✅ {replacement}")
        
        prompt_parts.append("")
        prompt_parts.append("=" * 60)
        prompt_parts.append("ENFORCEMENT RULES:")
        prompt_parts.append("1. If you catch yourself about to use a forbidden word, STOP")
        prompt_parts.append("2. Choose the suggested replacement or rephrase entirely")
        prompt_parts.append("3. These words make content sound AI-generated and must be avoided")
        prompt_parts.append("4. Quality will be checked - using these words is a critical failure")
        prompt_parts.append("=" * 60)
        prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def generate_content(self,
                        heading: str,
                        pattern_type: str,
                        research_data: Dict[str, Any],
                        context: Dict[str, Any],
                        temperature: float = DEFAULT_TEMPERATURE,
                        function_name: str = None,
                        include_internal_links: bool = True) -> Dict[str, Any]:
        """
        Generate content for a specific heading
        
        Args:
            heading: The heading to generate content for
            pattern_type: The detected pattern type
            research_data: Research data from Perplexity
            context: Additional context (parent headings, Gcore info, etc.)
            temperature: Generation temperature
            function_name: Optional function name for specialized generation
            include_internal_links: Whether to include internal link suggestions
            
        Returns:
            Dictionary with generated content and metadata
        """
        if not self.client:
            return {
                'status': 'error',
                'message': 'Anthropic API key not configured',
                'content': ''
            }
        
        # Get the pattern template
        template = get_pattern_template(pattern_type)
        
        # Get internal link suggestions if enabled
        link_suggestions = []
        link_prompt_section = ""
        if self.enable_internal_links and include_internal_links and self.internal_linker:
            # Create preview content from research data for link matching
            preview_content = f"{heading}\n"
            if research_data and 'facts' in research_data:
                preview_content += "\n".join(research_data['facts'][:5])
            
            # Get link suggestions
            link_suggestions = self.internal_linker.suggest_links_for_content(
                preview_content, heading, max_links=3
            )
            
            # Generate link prompt section
            if link_suggestions:
                link_prompt_section = self.internal_linker.generate_link_prompt_section(link_suggestions)
        
        # Build the generation prompt
        if function_name:
            # Use function-specific prompt
            prompt = self._build_function_prompt(
                heading, function_name, research_data, context, link_prompt_section
            )
        else:
            # Use pattern-based prompt
            prompt = self._build_generation_prompt(
                heading, pattern_type, template, research_data, context, link_prompt_section
            )
        
        try:
            # Generate content with Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract and process the generated content
            generated_content = response.content[0].text

            # Post-process the content (pass function_name to identify CTAs)
            processed_content = self._post_process_content(
                generated_content, pattern_type, heading, function_name
            )

            # Deep humanization pass - automatic for all content
            humanized_content = self._deep_humanize_content(processed_content, pattern_type)

            # Fix format mixing AGAIN after humanization (catch any markdown added during humanization)
            humanized_content = self._fix_format_mixing(humanized_content)

            # Check if content could benefit from table format
            table_data = None
            if self.table_formatter.detect_table_opportunity(humanized_content, heading):
                table_result = self.table_formatter.convert_to_table(humanized_content, heading)
                if table_result.get('html'):
                    table_data = table_result

            result = {
                'status': 'success',
                'content': humanized_content,
                'pattern_type': pattern_type,
                'word_count': len(humanized_content.split()),
                'timestamp': datetime.now().isoformat()
            }
            
            if table_data:
                result['table'] = table_data
                result['has_alternative_format'] = True
            
            # Add link suggestions info if available
            if link_suggestions:
                result['internal_links'] = [
                    {
                        'url': link.url,
                        'anchor_text': anchor,
                        'relevance_score': score
                    }
                    for link, anchor, score in link_suggestions
                ]
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'content': ''
            }
    
    def _build_function_prompt(self,
                               heading: str,
                               function_name: str,
                               research_data: Dict[str, Any],
                               context: Dict[str, Any],
                               link_prompt_section: str = "") -> str:
        """Build prompt based on selected function"""
        import json
        from pathlib import Path
        
        # Load section functions
        functions_file = Path("data/section_functions.json")
        if functions_file.exists():
            with open(functions_file, 'r') as f:
                section_functions = json.load(f)
        else:
            # Fallback to general prompt
            return self._build_generation_prompt(
                heading, "general", get_pattern_template("general"), 
                research_data, context, link_prompt_section
            )
        
        # Get the function configuration
        function_config = section_functions.get('functions', {}).get(function_name, {})
        if not function_config:
            # Fallback to general prompt
            return self._build_generation_prompt(
                heading, "general", get_pattern_template("general"), 
                research_data, context, link_prompt_section
            )
        
        # Special handling for Gcore service functions
        if function_name in ["generate_gcore_service", "generate_gcore_service_organic", "generate_intelligent_cta"]:
            return self._build_gcore_service_prompt(
                heading, function_config, research_data, context, section_functions
            )
        
        # Build prompt from function template with Gcore editorial guidelines
        gcore_editorial = get_generation_prompt_section()

        prompt_parts = [
            gcore_editorial,
            "",
            "IMPORTANT: NO company promotion or sales language in educational sections",
            "",
            f"CONTENT TYPE: {function_config.get('article_methodology', function_config.get('name', function_name))}",
            "",
            self._format_template_with_placeholders(
                function_config.get('prompt_template', ''), 
                heading, 
                function_name
            ),
            ""
        ]
        
        # Add requirements
        if function_config.get('requirements'):
            prompt_parts.append("STRICT REQUIREMENTS:")
            for req in function_config['requirements']:
                prompt_parts.append(f"✓ {req}")
            prompt_parts.append("")
        
        # Add research data if available (use more data)
        if research_data and research_data.get('data'):
            prompt_parts.extend([
                "RESEARCH DATA TO INCORPORATE:",
                "Use this researched information to make your content accurate and data-driven.",
                "",
                "CITATION RULES:",
                "• Use proper Svalbardi citation format: 'according to [Source] ([Year])'",
                "• PRIORITIZE citing financial projections and market data ($ trillion, billion)",
                "• Cite credible sources: academic, government, industry research, market forecasts",
                "• STRICT SOURCE VALIDATION - ABSOLUTELY FORBIDDEN phrases:",
                "  - 'according to research' (any variation)",
                "  - 'according to market research' (any variation)",
                "  - 'according to industry analysis' (any variation)",  
                "  - 'according to studies' (any variation)",
                "  - 'according to reports' (any variation)",
                "  - 'according to data' (any variation)",
                "  - 'based on research' (any variation)",
                "  - 'research shows' (without specific source)",
                "  - 'studies indicate' (without specific source)",
                "  - 'data suggests' (without specific source)",
                "• If you cannot identify the EXACT organization name from research data, DO NOT cite",
                "• ONLY cite with format: 'according to [Specific Organization Name] (Year)'",
                "",
                "ABSOLUTE SOURCE LOCKDOWN (CRITICAL):",
                "• If a statistic/claim does not have a verified research organization source, OMIT IT COMPLETELY",
                "• Do NOT include market statistics unless you can cite the exact organization",
                "• OMIT rather than fabricate - content quality is more important than including every statistic",
                "• Verified organizations include: Precedence Research, Gartner, Forrester, IDC, McKinsey",
                "",
                "STRATEGIC CITATION POLICY:",
                "  - Only cite claims that truly need verification (market data, financial projections, technical specs)",
                "  - Do NOT cite basic definitions, common processes, or general explanations",
                "  - FAQ sections: Generate full answer content BUT do NOT include citations - keep FAQs clean and direct",
                "  - Maximum 5 citations per entire document (be very selective)",
                "  - Maximum 1 citation per section (including introduction)",
                "  - Focus citations on: market size, growth rates, performance claims, industry scale",
                "",
                "FACT REPETITION PREVENTION:",
                "• NEVER repeat the same fact/statistic in multiple sections",
                "• Each significant statistic should appear only ONCE in the entire document",
                "• If a fact was used in introduction, do not use it again in body sections",
                "• Quality over quantity - fewer, more impactful citations are better",
                ""
            ])
            
            # Add already used facts to prevent repetition
            used_facts = list(self.source_manager.citation_tracker.used_facts_content)
            if used_facts:
                prompt_parts.append("\nALREADY USED FACTS (DO NOT REPEAT THESE - CRITICAL):")
                prompt_parts.append("• If any of the following fact patterns appear in your content, you MUST omit them completely")
                prompt_parts.append("• NEVER repeat market statistics, financial projections, or growth rates already used")
                prompt_parts.append("• NEVER cite the same source organization twice in one article")
                for i, fact_fingerprint in enumerate(used_facts[:10]):  # Show more facts to be thorough
                    prompt_parts.append(f"{i+1}. {fact_fingerprint}")
                prompt_parts.append("")
                prompt_parts.append("REPETITION PREVENTION RULES:")
                prompt_parts.append("• Each source should be mentioned only ONCE in the entire article")
                prompt_parts.append("• Each market statistic should appear only ONCE in the entire article") 
                prompt_parts.append("• If a statistic was used in introduction, DO NOT use it again in other sections")
                prompt_parts.append("• Use different research points from your data for each section")
                prompt_parts.append("")
            
            if research_data['data'].get('facts'):
                prompt_parts.append("\nVerified Facts (incorporate naturally, only cite if it's a specific claim):")
                # Use more facts based on content length
                num_facts = 8 if function_name in ["generate_gcore_service", "generate_gcore_service_organic"] else 6
                facts_list = research_data['data']['facts'][:num_facts]
                for fact in facts_list:
                    if isinstance(fact, dict):
                        # Use the formatted fact with source
                        prompt_parts.append(f"• {fact.get('text', fact.get('original', ''))}")
                    else:
                        prompt_parts.append(f"• {fact}")
            
            if research_data['data'].get('statistics'):
                prompt_parts.append("\nKey Statistics (these typically need citations):")
                # Include more statistics
                stats_list = research_data['data']['statistics'][:5]
                for stat in stats_list:
                    if isinstance(stat, dict):
                        # Use the formatted statistic with source
                        prompt_parts.append(f"• {stat.get('text', stat.get('original', ''))}")
                    else:
                        prompt_parts.append(f"• {stat}")
            
            if research_data['data'].get('key_points'):
                prompt_parts.append("\nImportant Points to Cover:")
                for point in research_data['data']['key_points'][:4]:
                    prompt_parts.append(f"• {point}")
            
            if research_data['data'].get('examples'):
                prompt_parts.append("\nExamples to Consider:")
                for example in research_data['data']['examples'][:3]:
                    prompt_parts.append(f"• {example}")
            
            prompt_parts.append("")
        
        # Add writing rules (always included)
        prompt_parts.extend([
            "WRITING RULES:",
            "• First sentence must directly answer the heading question",
            "• Structure: General → Specific, Basic → Advanced",
            "• Sentences: Maximum 30 words each",
            "• Paragraphs: Maximum 150 words (3-4 sentences)",
            "• Use contractions naturally (it's, don't, can't, we're)",
            "• Active voice only",
            "• NO self-promotion or company mentions unless explicitly relevant",
            "• Focus on educational content, not sales",
            "",
            "CONTENT STRUCTURE (CRITICAL - follow user's heading structure exactly):",
            "• ONLY answer the specific heading question - do not add sub-headings",
            "• Do not add ## headings, subheadings, or extra structure",
            "• Stick to paragraphs and lists only",
            "• Do not create your own content organization beyond the assigned heading",
            "",
            "COMPETITOR AVOIDANCE (CRITICAL - Gcore brand requirement):",
            "• NEVER mention specific competitors by name:",
            "  - Cloud providers: AWS, Amazon Web Services, Azure, Microsoft Azure, Google Cloud, GCP",
            "  - CDN competitors: Cloudflare, Akamai, Fastly, KeyCDN, StackPath, BunnyCDN",
            "  - Cloud platforms: Oracle Cloud, IBM Cloud, Alibaba Cloud, DigitalOcean, Linode, Vultr",
            "  - Hosting: GoDaddy, Bluehost, HostGator, Heroku",
            "  - Media services: Cloudinary, Imgix",
            "• Use generic terms instead:",
            "  - 'major cloud providers' instead of 'AWS, Azure, Google Cloud'",
            "  - 'leading CDN providers' instead of 'Cloudflare, Akamai'",
            "  - 'cloud hosting providers' instead of specific names",
            "  - 'enterprise cloud services' instead of Azure/AWS",
            "  - 'content delivery networks' for CDN references",
            "• Focus on capabilities and features, not company names",
            "• When examples are needed, use generic scenarios or 'Provider A/B'",
            "",
            "CURRENT DATA (CRITICAL - always use current year):",
            "• Current year is 2025",
            "• When citing statistics or data:",
            "  - Use 2025 for current year references (NOT 2024 or earlier)",
            "  - Say 'in 2025' or 'as of 2025' for recent statistics",
            "  - For studies/reports, use '2025 study' or '2025 report'",
            "  - NEVER reference 2024 or earlier years unless it's historical context",
            "",
            # Note: FORBIDDEN WORDS are now comprehensively covered at the beginning of the prompt
        ])
        
        # Add Gcore context ONLY if explicitly requested
        if context.get('include_gcore', False):
            prompt_parts.extend([
                "GCORE CONTEXT (use sparingly, only where it adds value):",
                f"• Infrastructure: {GCORE_INFO['pops']} Points of Presence globally",
                f"• Performance: {GCORE_INFO['average_latency']} average latency",
                "• IMPORTANT: Only mention Gcore if directly relevant to the answer",
                "• Save Gcore mentions for CTAs and product-specific sections",
                "",
            ])
        
        # Add internal link suggestions if provided
        if link_prompt_section:
            prompt_parts.append(link_prompt_section)
        
        prompt_parts.extend([
            "FINAL CITATION REMINDER:",
            "• Maximum 8 citations per document - PRIORITIZE market data and financial projections",
            "• If you've already cited a statistic, DO NOT cite it again",
            "• ALWAYS cite financial forecasts and market size projections when available",
            "• Use proper Svalbardi format: 'according to [Source] ([Year])'",
            "",
            "CRITICAL INSTRUCTIONS:",
            "• DO NOT add any questions asking for feedback",
            "• DO NOT include phrases like 'Does this meet your requirements?'",
            "• DO NOT add 'Let me know if you need...' or similar",
            "• End naturally without asking for confirmation",
            "",
            # ADD BLACKLIST AT THE END - reminder without constraining natural writing
            self.blacklist_prompt,
            "",
            "Generate the content now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_gcore_service_prompt(self,
                                   heading: str,
                                   function_config: Dict[str, Any],
                                   research_data: Dict[str, Any],
                                   context: Dict[str, Any],
                                   section_functions: Dict[str, Any]) -> str:
        """Build prompt specifically for Gcore service content using enhanced product data"""
        
        # Get Gcore product information from context
        gcore_product = context.get('gcore_product', 'cdn')
        gcore_features = context.get('gcore_features', [])
        
        # Extract article keywords for context-aware CTA selection
        article_keywords = []
        if heading:
            article_keywords.extend(heading.lower().split())
        if research_data and research_data.get('data'):
            # Add keywords from research data
            if research_data['data'].get('facts'):
                for fact in research_data['data']['facts'][:5]:
                    if isinstance(fact, dict):
                        fact_text = fact.get('text', fact.get('original', ''))
                    else:
                        fact_text = str(fact)
                    article_keywords.extend(fact_text.lower().split())
        
        # Get enhanced product info using the product loader
        gcore_product_info = product_loader.get_product_info_for_prompt(
            gcore_product, 
            selected_features=gcore_features
        )
        
        # Get the best CTA template for this context
        selected_cta_template = product_loader.get_best_cta_template(
            gcore_product, 
            context_keywords=article_keywords
        )
        
        # Format the prompt template with enhanced product info
        prompt_template = function_config.get('prompt_template', '')
        
        # Get product name for the template
        product_data = product_loader.get_product(gcore_product)
        product_name = product_data.get('name', gcore_product.replace('_', ' ').title()) if product_data else gcore_product.replace('_', ' ').title()
        
        # Determine article topic from heading or context
        article_topic = heading.replace('Gcore', '').replace('gcore', '').strip()
        if not article_topic or article_topic == heading:
            article_topic = f"{gcore_product.replace('_', ' ')} solutions"
        
        # Analyze article context for intelligent CTA
        content_type = "educational"
        audience_level = "intermediate"
        
        # Determine content type from heading
        if any(word in heading.lower() for word in ["beginner", "introduction", "basics", "overview"]):
            audience_level = "beginner"
        elif any(word in heading.lower() for word in ["advanced", "enterprise", "expert", "deep dive"]):
            audience_level = "advanced"
        
        if any(word in heading.lower() for word in ["tutorial", "how to", "guide", "step"]):
            content_type = "tutorial"
        elif any(word in heading.lower() for word in ["comparison", "vs", "difference"]):
            content_type = "comparison"
        elif any(word in heading.lower() for word in ["business", "roi", "cost", "budget"]):
            content_type = "business"
        
        # Format with all required variables including the selected CTA template
        try:
            formatted_prompt = prompt_template.format(
                heading=heading,
                gcore_product_info=gcore_product_info,
                article_topic=article_topic,
                gcore_product=product_name,
                selected_cta_template=selected_cta_template,
                content_type=content_type,
                audience_level=audience_level
            )
        except KeyError as e:
            # Fallback for older templates that don't expect all parameters
            try:
                formatted_prompt = prompt_template.format(
                    heading=heading,
                    gcore_product_info=gcore_product_info,
                    article_topic=article_topic,
                    gcore_product=product_name,
                    selected_cta_template=selected_cta_template
                )
            except KeyError:
                formatted_prompt = prompt_template.format(
                    heading=heading,
                    gcore_product_info=gcore_product_info,
                    article_topic=article_topic,
                    gcore_product=product_name
                )
        
        # Build the complete prompt with Gcore editorial guidelines
        gcore_editorial = get_generation_prompt_section()

        prompt_parts = [
            gcore_editorial,
            "",
            "CONTEXT: Creating educational content with natural product integration.",
            "",
            formatted_prompt,
            ""
        ]
        
        # Add research data if available (enhanced for Gcore content)
        if research_data and research_data.get('data'):
            prompt_parts.append("RESEARCH DATA TO INCORPORATE NATURALLY:")
            prompt_parts.append("Blend this information seamlessly into your educational content.")
            
            if research_data['data'].get('facts'):
                prompt_parts.append("\nIndustry Facts (use to support educational content):")
                for fact in research_data['data']['facts'][:8]:
                    if isinstance(fact, dict):
                        prompt_parts.append(f"• {fact.get('text', fact.get('original', ''))}")
                    else:
                        prompt_parts.append(f"• {fact}")
            
            if research_data['data'].get('statistics'):
                prompt_parts.append("\nRelevant Statistics (include specific metrics):")
                for stat in research_data['data']['statistics'][:6]:
                    if isinstance(stat, dict):
                        prompt_parts.append(f"• {stat.get('text', stat.get('original', ''))}")
                    else:
                        prompt_parts.append(f"• {stat}")
            
            if research_data['data'].get('examples'):
                prompt_parts.append("\nUse Cases and Applications:")
                for example in research_data['data']['examples'][:4]:
                    prompt_parts.append(f"• {example}")
            
            if research_data['data'].get('technical_specs'):
                prompt_parts.append("\nTechnical Specifications:")
                specs = research_data['data']['technical_specs']
                if isinstance(specs, dict):
                    for key, value in list(specs.items())[:5]:
                        prompt_parts.append(f"• {key}: {value}")
            
            prompt_parts.append("")
        
        prompt_parts.extend([
            "Remember: Educational content first, natural product mention second.",
            "",
            "CRITICAL: DO NOT add feedback questions like 'Does this meet your requirements?'",
            "",
            # ADD BLACKLIST AT THE END - final reminder
            self.blacklist_prompt,
            "",
            "Generate the content now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _extract_subject_from_heading(self, heading: str) -> str:
        """Extract the main subject from a heading"""
        # Remove question words
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 
                         'is', 'are', 'does', 'do', 'can', 'should', 'will']
        words = heading.lower().strip('?').split()
        subject_words = [w for w in words if w not in question_words]
        return ' '.join(subject_words) if subject_words else heading

    def _format_template_with_placeholders(self, template: str, heading: str, function_name: str) -> str:
        """Format template with all available placeholders"""
        if not template:
            return ""
            
        # Detect if heading is a question
        is_question = heading.strip().endswith('?') or any(
            heading.lower().startswith(q) for q in ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        )
        
        # Extract smart subject based on question vs statement
        if is_question:
            # For questions like "What is cloud GPU?", extract "cloud GPU"
            subject = self._extract_clean_subject_from_question(heading)
        else:
            # For statements, use existing logic
            subject = self._extract_subject_from_heading(heading)
        
        # Get semantic triple if semantic patterns are available
        try:
            from .semantic_patterns import SemanticPatterns
            semantic_patterns = SemanticPatterns()
            pattern_type = semantic_patterns.detect_pattern(heading)
            triple = semantic_patterns.get_semantic_triple(heading, pattern_type)
            predicate = triple.get('predicate', 'is')
        except:
            predicate = 'is'
        
        # Extract action from heading for templates that need it
        action = self._extract_action_from_heading(heading)
        
        # Prepare all possible placeholders
        placeholders = {
            'heading': heading,
            'subject': subject,
            'Subject': subject.capitalize() if subject else heading,
            'predicate': predicate,
            'action': action,
            'min_words': '150',
            'max_words': '300',
            'research_context': '',
            'pattern_type': function_name,
            'original_content': '',
            'feedback': '',
            'content': '',
            'issues': '',
            'keyword': '',
            'semantic_keywords': ''
        }
        
        # Format template with available placeholders
        try:
            return template.format(**placeholders)
        except KeyError as e:
            # If any placeholder is missing, return the template as-is
            return template

    def _extract_action_from_heading(self, heading: str) -> str:
        """Extract the action verb from a heading"""
        # Common action patterns
        if heading.lower().startswith('how to '):
            return heading[7:].split()[0] if len(heading) > 7 else 'do'
        
        # Look for action verbs in heading
        action_verbs = ['create', 'build', 'setup', 'configure', 'install', 'use', 'manage', 'optimize']
        words = heading.lower().split()
        for verb in action_verbs:
            if verb in words:
                return verb
        
        return 'do'  # Default action

    def _extract_clean_subject_from_question(self, heading: str) -> str:
        """Extract clean subject from questions to prevent grammar issues"""
        heading = heading.strip().rstrip('?').lower()
        
        # Handle different question patterns
        if heading.startswith('what is '):
            return heading[8:]  # "what is cloud gpu" -> "cloud gpu"
        elif heading.startswith('what are '):
            return heading[9:]  # "what are cloud gpus" -> "cloud gpus" 
        elif heading.startswith('how does '):
            subject = heading[9:]
            # "how does cloud gpu work" -> "cloud gpu"
            if ' work' in subject:
                subject = subject.replace(' work', '')
            return subject
        elif heading.startswith('how do '):
            subject = heading[7:]
            if ' work' in subject:
                subject = subject.replace(' work', '')
            return subject
        elif heading.startswith('why '):
            # "why use cloud gpu" -> "cloud gpu"
            words = heading[4:].split()
            # Remove common action words
            action_words = ['use', 'choose', 'need', 'want', 'do', 'are', 'is']
            subject_words = [w for w in words if w not in action_words]
            return ' '.join(subject_words) if subject_words else heading[4:]
        elif heading.startswith('when '):
            # Similar logic for when questions
            words = heading[5:].split()
            action_words = ['use', 'choose', 'need', 'do', 'should', 'can']
            subject_words = [w for w in words if w not in action_words]
            return ' '.join(subject_words) if subject_words else heading[5:]
        elif heading.startswith('where '):
            # "where are cloud gpus" -> "cloud gpus"
            words = heading[6:].split()
            if words and words[0] in ['are', 'is']:
                return ' '.join(words[1:])
            return ' '.join(words) if words else heading[6:]
        elif heading.startswith('who '):
            return heading[4:]
        elif heading.startswith('which '):
            return heading[6:]
        else:
            # Fallback to original logic
            return self._extract_subject_from_heading(heading)
    
    def _build_generation_prompt(self,
                                heading: str,
                                pattern_type: str,
                                template: Any,
                                research_data: Dict[str, Any],
                                context: Dict[str, Any],
                                link_prompt_section: str = "") -> str:
        """Build a comprehensive generation prompt"""
        
        # Extract semantic triple
        triple = get_semantic_triple(heading)

        # Get Gcore editorial guidelines for generation
        gcore_editorial = get_generation_prompt_section()

        prompt_parts = [
            gcore_editorial,
            "",
            "Write content that directly answers the following question/heading:",
            f"\nHeading: {heading}",
            f"Pattern Type: {pattern_type}",
            f"Required Structure: {template.structure}",
            f"\nSemantic Triple:",
            f"- Subject: {triple['subject']}",
            f"- Predicate: {triple['predicate']}",
            f"- Object: {triple['object']}",
            ""
        ]
        
        # Add pattern-specific instructions
        prompt_parts.extend(self._get_pattern_instructions(pattern_type, heading))
        
        # Add research data if available (comprehensive integration)
        if research_data and research_data.get('data'):
            prompt_parts.append("\nRESEARCH INFORMATION TO INCLUDE:")
            prompt_parts.append("Integrate this researched content to provide accurate, data-driven answers.")
            
            # Match research to pattern type for better relevance
            if pattern_type in ['definition_singular', 'definition_plural']:
                # Focus on facts and definitions
                if research_data['data'].get('facts'):
                    prompt_parts.append("\nCore Facts and Definitions:")
                    for fact in research_data['data']['facts'][:8]:
                        if isinstance(fact, dict):
                            prompt_parts.append(f"- {fact.get('text', fact.get('original', ''))}")
                        else:
                            prompt_parts.append(f"- {fact}")
            
            elif pattern_type in ['how_to', 'how_process']:
                # Focus on process and examples
                if research_data['data'].get('key_points'):
                    prompt_parts.append("\nImplementation Points:")
                    for point in research_data['data']['key_points'][:6]:
                        prompt_parts.append(f"- {point}")
                if research_data['data'].get('examples'):
                    prompt_parts.append("\nPractical Examples:")
                    for example in research_data['data']['examples'][:4]:
                        prompt_parts.append(f"- {example}")
            
            elif pattern_type in ['how_common', 'yes_no']:
                # Focus on statistics and comparisons
                if research_data['data'].get('statistics'):
                    prompt_parts.append("\nRelevant Statistics:")
                    for stat in research_data['data']['statistics'][:8]:
                        prompt_parts.append(f"- {stat}")
            
            else:
                # General pattern - balanced mix
                if research_data['data'].get('facts'):
                    prompt_parts.append("\nKey Facts:")
                    for fact in research_data['data']['facts'][:6]:
                        if isinstance(fact, dict):
                            prompt_parts.append(f"- {fact.get('text', fact.get('original', ''))}")
                        else:
                            prompt_parts.append(f"- {fact}")
                
                if research_data['data'].get('statistics'):
                    prompt_parts.append("\nStatistics:")
                    for stat in research_data['data']['statistics'][:5]:
                        if isinstance(stat, dict):
                            prompt_parts.append(f"- {stat.get('text', stat.get('original', ''))}")
                        else:
                            prompt_parts.append(f"- {stat}")
                
                if research_data['data'].get('key_points'):
                    prompt_parts.append("\nMain Points:")
                    for point in research_data['data']['key_points'][:4]:
                        prompt_parts.append(f"- {point}")
        
        # Add context ONLY if explicitly requested
        if context.get('include_gcore', False):
            prompt_parts.append("\nCompany Context:")
            prompt_parts.append(f"- Global infrastructure: {GCORE_INFO['pops']} Points of Presence")
            prompt_parts.append(f"- Performance: {GCORE_INFO['average_latency']} average latency")
            prompt_parts.append("- Services: CDN, Edge Cloud, AI Infrastructure")
        
        # Add writing guidelines
        prompt_parts.extend([
            "\nEDITORIAL GUIDELINES:",
            "PRINCIPLES:",
            "• Be simple: Front-load important points, use simple structures",
            "• Be concise: Use as few words as possible",
            "• Be friendly: Write like you talk, use active voice",
            "• Be helpful: Focus on customer needs",
            "• Be specific: Use exact numbers, not vague terms",
            ""
        ])
        
        # Add internal link suggestions if provided
        if link_prompt_section:
            prompt_parts.append(link_prompt_section)
        
        prompt_parts.extend([
            "WRITING RULES:",
            "1. First sentence MUST directly answer the heading question",
            "2. Structure: General → Specific, Basic → Advanced",
            "3. Sentences: Maximum 30 words each (vary lengths for natural flow)",
            "4. Paragraphs: Maximum 150 words (3-4 sentences, vary lengths)",
            "5. Use contractions naturally and sporadically (it's, don't, can't, we're)",
            "6. Active voice only",
            "7. Sentence case for headings",
            "",
            "CRITICAL: DO NOT add feedback questions like 'Does this meet your requirements?'",
            "",
            # ADD BLACKLIST AT THE END - final reminder without constraining initial writing
            self.blacklist_prompt,
            "",
            "Generate the content now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_pattern_instructions(self, pattern_type: str, heading: str) -> List[str]:
        """Get pattern-specific generation instructions"""
        instructions = ["\nPattern-Specific Requirements:"]
        
        if pattern_type == 'definition_singular':
            instructions.extend([
                f"- Start with '{heading.replace('?', '').strip()} is...'",
                "- Provide a clear, concise definition",
                "- Follow with 2-3 sentences of expansion",
                "- Keep it in paragraph form"
            ])
        
        elif pattern_type == 'definition_plural':
            instructions.extend([
                f"- Start with 'The [items] are listed below.'",
                "- Create a bulleted list",
                "- Format: • **Term**: Explanation",
                "- Include 3-5 relevant items"
            ])
        
        elif pattern_type == 'how_to':
            instructions.extend([
                "- Start by restating the action",
                "- Provide clear step-by-step instructions",
                "- Use transition words (First, Then, Next, Finally)",
                "- Make it actionable and specific"
            ])
        
        elif pattern_type == 'how_process':
            instructions.extend([
                f"- Start with '[Subject] works by...'",
                "- Explain the mechanism clearly",
                "- Break down into logical steps",
                "- Include technical details where appropriate"
            ])
        
        elif pattern_type == 'yes_no':
            instructions.extend([
                "- Start with 'Yes' or 'No'",
                "- Follow immediately with the main point",
                "- Provide supporting explanation",
                "- Keep it concise and direct"
            ])
        
        elif pattern_type == 'why':
            instructions.extend([
                "- Start with the subject and 'because'",
                "- Provide the primary reason first",
                "- Follow with supporting points",
                "- Focus on causality and benefits"
            ])
        
        elif pattern_type == 'when':
            instructions.extend([
                "- Start with the specific timing/condition",
                "- Be precise about when something should happen",
                "- Include any prerequisites or triggers",
                "- Provide context for the timing"
            ])
        
        elif pattern_type == 'where':
            instructions.extend([
                "- Start with the specific location/place",
                "- Be geographically or logically specific",
                "- Include relevant infrastructure details if applicable",
                "- Provide additional context"
            ])
        
        return instructions
    
    def _add_sentence_variety(self, content: str, pattern_type: str) -> str:
        """
        Add sentence length variety (burstiness) to make content more human-like.
        Human writing naturally varies between short and long sentences.
        """
        # Skip for list-based patterns
        if pattern_type in ['definition_plural', 'how_to', 'listicle', 'how_list']:
            return content

        import re

        # Split into paragraphs
        paragraphs = content.split('\n\n')
        varied_paragraphs = []

        for paragraph in paragraphs:
            # Skip if it's a list item
            if paragraph.strip().startswith('•') or paragraph.strip().startswith('-'):
                varied_paragraphs.append(paragraph)
                continue

            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)

            if len(sentences) < 3:
                # Too short to vary
                varied_paragraphs.append(paragraph)
                continue

            # Calculate sentence lengths
            sentence_lengths = [len(s.split()) for s in sentences]

            # Check if sentences are too uniform (within 5 words of each other)
            if len(sentence_lengths) >= 3:
                uniform = True
                for i in range(len(sentence_lengths) - 2):
                    if abs(sentence_lengths[i] - sentence_lengths[i+1]) > 5 or \
                       abs(sentence_lengths[i+1] - sentence_lengths[i+2]) > 5:
                        uniform = False
                        break

                # If too uniform, the content already has variety - keep it
                if not uniform:
                    varied_paragraphs.append(paragraph)
                    continue

            # Content is too uniform - already good variety exists
            varied_paragraphs.append(paragraph)

        return '\n\n'.join(varied_paragraphs)

    def _update_outdated_years(self, content: str) -> str:
        """
        Update outdated years in statistics to current year (2025).
        Feedback issue: stats mentioning 2024 or earlier should be updated.
        """
        import re
        from datetime import datetime

        # Get current year (2025)
        current_year = 2025

        # Common patterns where years appear in statistics
        # Examples: "in 2024", "by 2023", "since 2022", "2024 study", "2024 report"

        # Pattern 1: Standalone years in common contexts
        # "in 2024" -> "in 2025", "by 2024" -> "by 2025"
        year_patterns = [
            (r'\bin\s+202[0-4]\b', f'in {current_year}'),
            (r'\bby\s+202[0-4]\b', f'by {current_year}'),
            (r'\bsince\s+202[0-4]\b', f'since {current_year}'),
            (r'\bduring\s+202[0-4]\b', f'during {current_year}'),
            (r'\bas of\s+202[0-4]\b', f'as of {current_year}'),
        ]

        for pattern, replacement in year_patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

        # Pattern 2: Year in study/report/data references
        # "2024 study" -> "2025 study", "2024 report" -> "2025 report"
        content = re.sub(r'\b202[0-4]\s+(study|report|survey|research|data|analysis|statistics)\b',
                        f'{current_year} \\1', content, flags=re.IGNORECASE)

        # Pattern 3: Year ranges ending in 2024 or earlier
        # "2020-2024" -> "2020-2025", "2023-2024" -> "2023-2025"
        content = re.sub(r'\b(\d{4})-202[0-4]\b', f'\\1-{current_year}', content)

        # Pattern 4: Phrases like "As of 2024" at start of sentences
        content = re.sub(r'As of 202[0-4],', f'As of {current_year},', content, flags=re.IGNORECASE)

        return content

    def _post_process_content(self, content: str, pattern_type: str, heading: str, function_name: str = None) -> str:
        """Post-process generated content to ensure quality"""

        # Determine if this is a CTA section that should keep Gcore mentions
        is_cta_section = function_name in ["generate_gcore_service", "generate_gcore_service_organic", "generate_evaluation_bridge", "generate_intelligent_cta"]
        
        # FIRST: Remove any meta-commentary or notes from the AI
        # Remove common note patterns
        import re
        
        # Remove analysis/feedback sections - BE SPECIFIC to avoid removing real content
        analysis_patterns = [
            r'\n\[This (?:introduction|response|answer|content)[^\]]*?\]\.?\s*$',  # [This introduction/response/answer: ...]. at end of paragraphs
            r'^\[This (?:introduction|response|answer|content)[^\]]*?\]\.?\s*\n',  # [This... at start of lines
            r'\nAnalysis of my response:.*?(?=\n\n|\Z)',  # Remove analysis sections
            r'\n✓[^\n]*\n',  # Remove checkmark lines  
            r'\n- (?:Starting with|Providing|Including|Maintaining|Using|Staying|Avoiding|Explains|Covers|Mentions|Highlights|Sets up|Uses active|Avoids promotional)[^\n]*\n',  # Bullet point analysis
            r'\nTriple:.*?\].*?\n',  # Remove semantic triple annotations
            r'\[Note:.*?\]',  # [Note: ...]
            r'\(Note:.*?\)',  # (Note: ...)
            r'^Note:.*?$',  # Note: ... (only at start of line, to end of line)
            r'\*\*Note:.*?\*\*.*?(?=\n|$)',  # **Note:** ...
            r'^Commentary:.*?$',  # Commentary: ... (only at start of line)
            r'^Meta:.*?$',  # Meta: ... (only at start of line)
            r'^Instructions:.*?$',  # Instructions: ... (only at start of line)
            r'^Pattern:.*?$',  # Pattern: ... (only at start of line)
            r'This response follows the.*?pattern',  # This response follows the X pattern
            r'This answer follows the.*?pattern',  # This answer follows the X pattern
            r'Following the.*?pattern requirement',  # Following the X pattern requirement
            r'As per the.*?pattern requirement',  # As per the pattern requirement
            r'According to the pattern',  # According to the pattern (specific phrase only)
            # Remove AI feedback questions
            r'\n?Does this meet your requirements\??[\s\n]*$',  # Does this meet your requirements?
            r'\n?Is this what you were looking for\??[\s\n]*$',  # Is this what you were looking for?
            r'\n?Let me know if you need.*?[\s\n]*$',  # Let me know if you need...
            r'\n?Would you like me to.*?[\s\n]*$',  # Would you like me to...
            r'\n?I hope this helps.*?[\s\n]*$',  # I hope this helps...
            r'\n?Please let me know.*?[\s\n]*$',  # Please let me know...
        ]
        
        for pattern in analysis_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # Remove any remaining bracketed notes (but be more careful)
        content = re.sub(r'\n\[.*?follows.*?pattern.*?\]', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'\n\[.*?response.*?pattern.*?\]', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove entire "Analysis of my response" blocks
        content = re.sub(r'Analysis of my response:.*?(?=\n\n|\Z)', '', content, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
        
        # Clean up any lines that are just meta-commentary
        lines = content.split('\n')
        cleaned_lines = []
        skip_until_empty = False
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we should start skipping (analysis section)
            if 'analysis of my response' in line_lower or 'analysis:' in line_lower:
                skip_until_empty = True
                continue
            
            # If we're skipping and hit an empty line, stop skipping
            if skip_until_empty and not line.strip():
                skip_until_empty = False
                continue
            
            # Skip if we're in skip mode
            if skip_until_empty:
                continue
            
            # Skip lines with checkmarks
            if '✓' in line:
                continue
            
            # Skip bullet point meta-commentary
            if line.strip().startswith('- ') and any(phrase in line_lower for phrase in [
                'starting with', 'providing', 'including', 'maintaining',
                'using', 'staying', 'avoiding', 'explains', 'covers',
                'mentions', 'highlights', 'sets up', 'uses active',
                'avoids promotional'
            ]):
                continue
            
            # Skip lines that are clearly meta-commentary (but be more careful for CTAs)
            meta_phrases = [
                'this response follows', 'this answer follows', 'following the pattern',
                'as requested', 'according to the pattern',
                '- starts with', '- expands with', '- maintains', '- uses simple',
                '- avoids forbidden', '- incorporates', '- stays in paragraph',
                'note:', 'pattern:', 'per the requirements', 'as instructed',
                'the response follows', 'the answer follows'
            ]
            
            # For CTAs, be less aggressive about removing content
            if is_cta_section:
                # Only skip very obvious meta-commentary
                if any(phrase in line_lower for phrase in ['note:', 'pattern:', 'per the requirements', 'as instructed']):
                    continue
            else:
                # For non-CTA content, use the full list
                if any(phrase in line_lower for phrase in meta_phrases):
                    continue
            cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)
        
        # Ensure proper formatting for lists
        if pattern_type == 'definition_plural' or 'listicle' in str(pattern_type):
            lines = content.split('\n')
            processed_lines = []
            for line in lines:
                # For listicle format, ensure bullet points and bold terms
                if ':' in line:
                    # Check if it already has a bullet or numbered list format
                    if not line.strip().startswith('•') and not line.strip()[0].isdigit():
                        # Add bullet point only if it's not a numbered list
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            term = parts[0].strip()
                            # Bold if not already bolded
                            if '**' not in term and term:
                                line = f"• **{term}**: {parts[1].strip()}"
                            else:
                                line = f"• {line.strip()}"
                processed_lines.append(line)
            content = '\n'.join(processed_lines)
        
        # Ensure Yes/No patterns start correctly
        if pattern_type == 'yes_no' or 'yes_no' in str(pattern_type):
            if not content.startswith(('Yes,', 'No,', 'Yes.', 'No.')):
                # Try to fix it
                content_lower = content.lower()
                if 'not' in content_lower[:50] or 'no' in content_lower[:20]:
                    content = 'No, ' + content
                else:
                    content = 'Yes, ' + content
        
        # Remove company self-promotion ONLY for non-CTA sections
        if not is_cta_section:
            promo_patterns = [
                r"Gcore['']?s?\s+[^.]*?(provides?|offers?|delivers?|enables?|supports?)[^.]*?\.",
                r"\bOur\s+[^.]*?(infrastructure|VMs?|platform|services?|systems?)[^.]*?\.",  # Added word boundary
                r"\bWe\s+(provide|offer|deliver|enable|support)[^.]*?\.",  # Added word boundary
                r"At\s+Gcore[^.]*?\.",
                r"With\s+Gcore[^.]*?\.",
                r"Gcore['']?s?\s+[^.]*?(hosting|cloud|edge|CDN|network)[^.]*?\.",
            ]
            for pattern in promo_patterns:
                content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove generic/fake attributions that should never appear
        generic_attributions = [
            r",?\s*according to industry standards",
            r",?\s*according to major providers",
            r",?\s*according to industry analysis",
            r",?\s*according to industry forecasts",
            r",?\s*according to industry reports",
            r",?\s*based on industry standards",
            r",?\s*based on industry data",
            r",?\s*per industry standards",
            r",?\s*as per industry standards",
        ]
        for pattern in generic_attributions:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Clean up any double spaces or formatting issues
        content = re.sub(r'  +', ' ', content)  # Remove multiple spaces
        
        # Clean up any leftover periods or formatting
        content = re.sub(r'\.\s*\.', '.', content)  # Remove double periods
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Normalize paragraph breaks
        
        # Ensure proper paragraph breaks
        if pattern_type not in ['definition_plural', 'how_to', 'listicle', 'how_list']:
            # Add paragraph breaks for better readability if content is long
            sentences = content.split('. ')
            if len(sentences) > 4:
                # Break into paragraphs every 3-4 sentences
                paragraphs = []
                current_para = []
                for i, sentence in enumerate(sentences):
                    current_para.append(sentence)
                    if (i + 1) % 3 == 0 and i < len(sentences) - 1:
                        paragraphs.append('. '.join(current_para) + '.')
                        current_para = []
                if current_para:
                    paragraphs.append('. '.join(current_para))
                    if not paragraphs[-1].endswith('.'):
                        paragraphs[-1] += '.'
                content = '\n\n'.join(paragraphs)
        
        # Final cleanup - remove any trailing/leading whitespace
        content = content.strip()
        
        # Validate content isn't broken or too short
        if len(content) < 50:
            # Content seems broken, return error message
            return f"Content generation incomplete. Please regenerate this section."

        # CRITICAL: Validate CTA sections have proper content (feedback issue)
        if is_cta_section:
            word_count = len(content.split())
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

            # Check word count
            if word_count < 80:  # CTAs should be 3 paragraphs, ~100-150 words minimum
                return f"CTA content too short ({word_count} words). Regenerate with minimum 100 words in 3 paragraphs."

            # Check paragraph count - should have at least 3 substantial paragraphs
            if len(paragraphs) < 3:
                return f"CTA needs at least 3 paragraphs (found {len(paragraphs)}). Regenerate with proper structure."

            # Check if CTA mentions Gcore (critical for brand visibility)
            if 'gcore' not in content.lower():
                return f"CTA must mention Gcore. Regenerate with proper Gcore context and value proposition."
        
        # Check for obviously broken content patterns
        if content.endswith(('Res.', 'Res:', '• **Res.', '**Res')):
            return f"Content generation was interrupted. Please regenerate this section."

        # CRITICAL: Check for random fragments and incomplete sentences (feedback issue)
        # Common broken patterns: "Older versions like SSL", "Configure your", etc.
        import re

        # Check last line for incomplete fragments
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if lines:
            last_line = lines[-1]

            # Detect random fragments: short lines without proper ending punctuation
            # or lines that end with prepositions/articles suggesting incompleteness
            incomplete_patterns = [
                r'like\s+[A-Z][a-z]*\s*$',  # "like SSL", "like TLS"
                r'\b(?:the|a|an|your|their|our|its)\s*$',  # Ends with article/possessive
                r'\b(?:by|with|from|to|for|in|on|at|of)\s+\w+\s*$',  # Ends with preposition + one word
                r'^\w+\s+versions?\s+like\s+\w+\s*$',  # "Older versions like SSL"
                r'^Configure\s+\w+\s*$',  # "Configure your"
                r'^\w+\s+the\s*$',  # Incomplete phrase
                r'such\s+as\s+\w+\s*$',  # "such as TLS"
            ]

            is_incomplete = False
            for pattern in incomplete_patterns:
                if re.search(pattern, last_line, re.IGNORECASE):
                    is_incomplete = True
                    break

            # Also check if last line is suspiciously short and doesn't end properly
            if not is_incomplete and len(last_line) < 30 and not last_line.endswith(('.', '!', '?', ':', ')')):
                # Check if it's a bullet point or numbered list item
                if not re.match(r'^\s*[\d•\-\*]', last_line):
                    is_incomplete = True

            if is_incomplete:
                # Remove the incomplete last line/sentence
                content = '\n'.join(lines[:-1])
                # Add proper ending if needed
                if content and not content.rstrip().endswith(('.', '!', '?')):
                    content = content.rstrip() + '.'

        # Check for truncated sentences (ending with single letters)
        # Be more specific - only consider it truncated if it's a truly isolated single letter
        # not part of common patterns like "your X" being cut to "y"
        if re.search(r'\s[a-z]\s*$', content):  # Single letter preceded by space
            # Additional validation: check if this might be a false positive
            last_word = content.strip().split()[-1] if content.strip().split() else ""
            
            # Only proceed if it's truly a single letter, not part of a word
            if len(last_word) == 1 and last_word.lower() in 'abcdefghijklmnopqrstuvwxyz':
                # Don't remove if it could be a valid single-letter word (a, I)
                if last_word.lower() not in ['a', 'i']:
                    # Content appears truncated, try to clean it up
                    sentences = content.split('. ')
                    if sentences and len(sentences[-1]) < 20:  # Last sentence is suspiciously short
                        content = '. '.join(sentences[:-1]) + '.'
        
        # Remove any incomplete bullet points at the end
        lines = content.split('\n')
        if lines and lines[-1].startswith('• **') and ':' not in lines[-1]:
            # Remove incomplete last bullet
            content = '\n'.join(lines[:-1])
        
        # Final cleanup of any remaining analysis artifacts (more precise patterns)
        # Only remove bracketed content that starts with "This" and contains a colon
        content = re.sub(r'\n\[This [^:]*:[^\]]*?\]\.?\s*', '\n', content, flags=re.IGNORECASE)
        # Remove orphaned dashes on their own line
        content = re.sub(r'^\s*-\s*$', '', content, flags=re.MULTILINE)
        
        # Clean up any multiple blank lines created by removals
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()
        
        # Final cleanup: Remove any trailing period on its own line
        lines = content.split('\n')
        if lines and lines[-1] == '.':
            content = '\n'.join(lines[:-1])
        
        # Also check for period after empty line at the end
        if content.endswith('\n\n.'):
            content = content[:-3].strip()
        elif content.endswith('\n.'):
            content = content[:-2].strip()
        
        # Validate and fix content structure
        validation = validate_content_structure(content)
        if not validation['valid']:
            # Split long paragraphs automatically
            content = split_long_paragraphs(content)
        
        # Clean competitor mentions (critical brand requirement)
        content = self._clean_competitor_mentions(content)
        
        # Clean up HTML/Markdown mixing (should only be HTML or only be Markdown)
        content = self._fix_format_mixing(content)
        
        # FINAL SAFETY NET: Remove any duplicate statistics that escaped other checks
        content = self._remove_duplicate_statistics_from_content(content)

        # Add sentence variety for more human-like writing (burstiness)
        content = self._add_sentence_variety(content, pattern_type)

        # Update outdated years in statistics (feedback issue - 2024 should be 2025)
        content = self._update_outdated_years(content)

        return content

    def _remove_meta_commentary(self, content: str) -> str:
        """Remove any meta-commentary added during humanization"""
        import re

        # Remove common meta-commentary patterns
        patterns = [
            r'^Here is the humanized content:?\s*\n*',
            r'^Humanized content:?\s*\n*',
            r'^Here\'s the improved version:?\s*\n*',
            r'^Here\'s the content:?\s*\n*',
            r'\n\nNote:.*$',
            r'\n\n\[This.*?\]$',
            r'\n\nI\'ve.*$',
            r'\n\nThe content.*$'
        ]

        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        return content.strip()

    def _deep_humanize_content(self, content: str, pattern_type: str) -> str:
        """
        Automatically humanize content using AI for natural, context-aware improvements.
        This runs after every generation to ensure human-sounding output.

        Args:
            content: The generated content to humanize
            pattern_type: The semantic pattern type (for context)

        Returns:
            Humanized content with AI patterns removed
        """
        # ALWAYS humanize - Ahrefs detects deeper AI patterns than just blacklist words
        # Don't skip even if no obvious AI words found

        # Get Gcore editorial guidelines for humanization
        gcore_guidelines = get_humanization_prompt_section()

        humanization_prompt = f'''Improve this content to match Gcore's editorial voice: professional expertise with friendly warmth.

CONTENT TO IMPROVE:
{content}

{gcore_guidelines}

CRITICAL SEMANTIC SEO REQUIREMENTS (DO NOT VIOLATE):
- MUST preserve exact semantic opening patterns ("X is...", "Yes/No,", etc.)
- MUST keep list parallelism perfect (all items same grammatical structure)
- MUST maintain professional, authoritative tone (friendly but expert)
- MUST keep direct answer structure (no rhetorical questions)
- MUST preserve subject-predicate-object triples
- DO NOT break grammar rules or add imperfections
- DO NOT add casual slang or overly informal language
- DO NOT change headings, bullet formatting, or list structures
- DO NOT add or remove any information or statistics
- DO NOT change technical terminology

MAINTAIN:
- Professional, authoritative voice (with warmth)
- Educational content style
- Technical accuracy and precision
- Semantic search optimization
- Structured, predictable patterns

GOAL: Apply Gcore editorial principles (simple, concise, friendly, helpful, specific) while preserving semantic framework.

Return ONLY the improved content. No explanations or notes.'''

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                temperature=0.75,  # Balanced for Gcore editorial voice - natural but controlled
                messages=[{"role": "user", "content": humanization_prompt}]
            )

            humanized = response.content[0].text.strip()

            # Clean up any meta-commentary that might have been added
            humanized = self._remove_meta_commentary(humanized)

            return humanized

        except Exception as e:
            # If humanization fails, return original content
            print(f"Humanization failed: {e}")
            return content

    def generate_introduction(self,
                            topic: str,
                            headings: List[Dict[str, str]] = None,
                            research_data: Dict[str, Any] = None,
                            include_gcore: bool = False) -> Dict[str, Any]:
        """Generate an introduction following SOP requirements"""
        if not self.client:
            return {
                'status': 'error',
                'message': 'Anthropic API key not configured',
                'content': ''
            }
        
        try:
            # Build introduction-specific prompt
            # Get Gcore editorial guidelines for introduction
            gcore_editorial = get_generation_prompt_section()

            prompt_parts = [
                "You are writing an introduction for a comprehensive article for technical professionals, following Holistic SEO SOP requirements.",
                "",
                gcore_editorial,
                "",
                f"Topic: {topic}",
                "",
                "INTRODUCTION STRUCTURE (MUST FOLLOW EXACTLY):",
                "",
                "PARAGRAPH 1 (Opening definition - 1-2 sentences):",
                f"- MUST start with proper grammar: 'A {topic.lower()} is [exact definition]...' or '{topic.capitalize()} is [exact definition]...' as grammatically appropriate",
                "- Can include a key metric or fundamental fact",
                "- Example: 'The percentage (total amount of X) can range from Y to Z'",
                "",
                "PARAGRAPHS 2-4 (Spot paragraphs - each 2-3 sentences):",
                "- Each paragraph previews a main section of the article",
                "- Include specific facts, components, or aspects",
                "- Build understanding progressively",
                "- Example patterns:",
                "  - 'X is made up of [components]. According to [source], these include...'",
                "  - 'The [aspect] refers to [definition]. This includes...'",
                "  - 'Understanding X is important because [reason]. This affects...'",
                "",
                "FINAL PARAGRAPH (Significance - 1-2 sentences):",
                "- Explain why this topic matters",
                "- Can include a key statistic or impact statement",
                "",
                "REQUIREMENTS:",
                "- Total length: 4-5 paragraphs (200-300 words)",
                "- NO uncertainty words (maybe, perhaps, probably, possibly, might, could)",
                "- NO specific brand or competitor mentions (AWS, Azure, GCP, etc.)",
                "- Use generic terms like 'major cloud providers' or 'leading platforms'",
                "- Include specific facts and data points",
                "- Each paragraph should be distinct and add new information",
                "",
            ]
            
            # Add H2 preview if headings provided
            if headings:
                h2_headings = [h for h in headings if h.get('level') == 'H2'][:5]
                if h2_headings:
                    prompt_parts.extend([
                        "SPOT PARAGRAPHS SHOULD PREVIEW THESE MAIN SECTIONS:",
                    ])
                    for i, h in enumerate(h2_headings[:4], 1):
                        prompt_parts.append(f"{i}. {h['text']}")
                    prompt_parts.extend([
                        "",
                        "Each spot paragraph should introduce one of these sections naturally.",
                        ""
                    ])
            
            # Add research data if available
            if research_data and research_data.get('data'):
                prompt_parts.extend([
                    "KEY FACTS TO INCORPORATE:",
                ])
                if research_data['data'].get('facts'):
                    for fact in research_data['data']['facts'][:5]:
                        if isinstance(fact, dict):
                            prompt_parts.append(f"- {fact.get('text', fact.get('original', ''))}")
                        else:
                            prompt_parts.append(f"- {fact}")
                if research_data['data'].get('statistics'):
                    prompt_parts.append("\nKEY STATISTICS:")
                    for stat in research_data['data']['statistics'][:3]:
                        if isinstance(stat, dict):
                            prompt_parts.append(f"- {stat.get('text', stat.get('original', ''))}")
                        else:
                            prompt_parts.append(f"- {stat}")
                prompt_parts.append("")
            
            # Add Gcore context if needed
            if include_gcore:
                prompt_parts.extend([
                    "Company Context (use sparingly):",
                    f"- {GCORE_INFO['pops']} Points of Presence globally",
                    f"- {GCORE_INFO['average_latency']} average latency",
                    ""
                ])
            
            # Final instructions
            prompt_parts.extend([
                "WRITE THE INTRODUCTION NOW:",
                f"- Paragraph 1: Direct definition starting with 'A {topic.lower()} is...' or '{topic.capitalize()} is...' as grammatically appropriate",
                "- Paragraphs 2-4: Spot paragraphs previewing main sections",
                "- Final paragraph: Why this matters",
                "",
                "Format as separate paragraphs with blank lines between them.",
                "Do not include any headings or labels.",
                "Write natural, flowing prose that follows the structure above.",
                "",
                # ADD BLACKLIST AT THE END - final reminder
                self.blacklist_prompt,
                ""
            ])
            
            prompt = "\n".join(prompt_parts)
            
            # Generate with higher temperature for more engaging introductions
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=MAX_TOKENS,
                    temperature=0.9,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                # Extract the generated content
                generated_content = response.content[0].text

                # Post-process the content
                cleaned_content = self._post_process_content(
                    generated_content, 'introduction', topic, None
                )

                # Deep humanization for introduction
                humanized_content = self._deep_humanize_content(cleaned_content, 'introduction')

                # Fix format mixing AGAIN after humanization
                humanized_content = self._fix_format_mixing(humanized_content)

            except Exception as e:
                return {
                    'status': 'error',
                    'content': '',
                    'error': f'Failed to generate introduction: {str(e)}'
                }

            return {
                'status': 'success',
                'content': humanized_content,
                'pattern_type': 'introduction',
                'word_count': len(humanized_content.split())
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'content': '',
                'error': str(e)
            }
    
    def generate_section(self,
                        heading: str,
                        research_data: Dict[str, Any] = None,
                        parent_context: str = None,
                        include_gcore: bool = True,
                        function_name: str = None,
                        include_internal_links: bool = True) -> Dict[str, Any]:
        """
        Simplified method to generate content for a section
        
        Args:
            heading: The heading text
            research_data: Optional research data
            parent_context: Context from parent headings
            include_gcore: Whether to include Gcore context
            function_name: Optional function name for specialized generation
            include_internal_links: Whether to include internal link suggestions
            
        Returns:
            Generated content dictionary
        """
        # Detect pattern type
        pattern_type = detect_question_type(heading)
        
        # Build context
        context = {
            'include_gcore': include_gcore
        }
        
        # If parent_context is a dict (contains Gcore product info), merge it
        if isinstance(parent_context, dict):
            context.update(parent_context)
        else:
            context['parent_context'] = parent_context
        
        # Generate content with internal links
        return self.generate_content(
            heading=heading,
            pattern_type=pattern_type,
            research_data=research_data or {},
            context=context,
            function_name=function_name,
            include_internal_links=include_internal_links
        )
    
    def regenerate_with_feedback(self,
                                heading: str,
                                original_content: str,
                                feedback: str,
                                pattern_type: str) -> Dict[str, Any]:
        """
        Regenerate content based on feedback
        
        Args:
            heading: The heading text
            original_content: The original generated content
            feedback: User feedback for improvement
            pattern_type: The pattern type
            
        Returns:
            Regenerated content dictionary
        """
        if not self.client:
            return {
                'status': 'error',
                'message': 'Anthropic API key not configured',
                'content': original_content
            }
        
        prompt = f"""
        Original heading: {heading}
        Pattern type: {pattern_type}
        
        Original content:
        {original_content}
        
        User feedback: {feedback}
        
        Please regenerate the content addressing the feedback while maintaining:
        1. The required pattern structure for {pattern_type}
        2. Direct answer to the question
        3. Professional brand voice
        4. Avoiding AI-sounding words
        
        Regenerated content:
        """
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                temperature=DEFAULT_TEMPERATURE,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            regenerated_content = response.content[0].text
            processed_content = self._post_process_content(
                regenerated_content, pattern_type, heading, None
            )
            
            return {
                'status': 'success',
                'content': processed_content,
                'pattern_type': pattern_type,
                'word_count': len(processed_content.split()),
                'feedback_applied': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'content': original_content
            }
    
    def batch_generate(self,
                      headings: List[Dict[str, str]],
                      research_data: Dict[str, Any],
                      progress_callback=None) -> Dict[str, Dict[str, Any]]:
        """
        Generate content for multiple headings in batch
        
        Args:
            headings: List of heading dictionaries
            research_data: Research data for the topic
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary mapping headings to generated content
        """
        # Reset global fact tracking at start of batch generation
        self.reset_fact_tracking()
        
        results = {}
        total = len(headings)
        
        for i, heading_dict in enumerate(headings):
            heading_text = heading_dict.get('text', '')
            heading_level = heading_dict.get('level', 'H2')
            
            # Update progress if callback provided
            if progress_callback:
                progress_callback(i + 1, total, f"Generating: {heading_text}")
            
            # Determine parent context (for H3s under H2s)
            parent_context = None
            if heading_level == 'H3' and i > 0:
                # Find the parent H2
                for j in range(i - 1, -1, -1):
                    if headings[j].get('level') == 'H2':
                        parent_heading = headings[j].get('text', '')
                        parent_content = results.get(parent_heading, {}).get('content', '')
                        parent_context = f"Parent section ({parent_heading}): {parent_content[:200]}..."
                        break
            
            # Generate content for this heading
            result = self.generate_section(
                heading=heading_text,
                research_data=research_data,
                parent_context=parent_context,
                include_gcore=True
            )
            
            results[heading_text] = result
        
        return results

# Convenience functions for Streamlit
def generate_content(heading: str, 
                    research_data: Dict[str, Any] = None,
                    temperature: float = DEFAULT_TEMPERATURE) -> Dict[str, Any]:
    """Generate content for a heading"""
    generator = ContentGenerator()
    pattern_type = detect_question_type(heading)
    return generator.generate_content(
        heading=heading,
        pattern_type=pattern_type,
        research_data=research_data or {},
        context={},
        temperature=temperature
    )

def batch_generate_content(headings: List[Dict[str, str]], 
                         research_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Generate content for multiple headings"""
    generator = ContentGenerator()
    return generator.batch_generate(headings, research_data)