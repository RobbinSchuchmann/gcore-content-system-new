"""
Research Engine using Perplexity API
Handles topic research, fact extraction, and source compilation
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st
from config import (
    PERPLEXITY_API_KEY, 
    PERPLEXITY_API_URL, 
    PERPLEXITY_MODEL,
    RESEARCH_SETTINGS,
    GCORE_INFO
)
from core.source_manager import SourceManager

class ResearchEngine:
    """Handle research operations using Perplexity API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        self.api_url = PERPLEXITY_API_URL
        self.model = PERPLEXITY_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.source_manager = SourceManager()
    
    def _detect_content_type(self, headings: List[Dict[str, str]]) -> str:
        """Detect the type of content based on headings"""
        heading_texts = ' '.join([h.get('text', '').lower() for h in headings])
        
        if any(term in heading_texts for term in ['how to', 'steps', 'guide', 'tutorial', 'implement']):
            return 'how_to'
        elif any(term in heading_texts for term in ['vs', 'versus', 'compare', 'difference', 'better']):
            return 'comparison'
        elif any(term in heading_texts for term in ['architecture', 'technical', 'specification', 'protocol', 'algorithm']):
            return 'technical'
        else:
            return 'general'
    
    def _build_technical_query(self, topic: str, questions: List[str]) -> List[str]:
        """Build query for technical topics"""
        return [
            f"Provide comprehensive technical research on: {topic}",
            "",
            "TECHNICAL RESEARCH FOCUS:",
            "1. Core technical concepts and architectures",
            "2. Implementation details and specifications",
            "3. Performance metrics and benchmarks",
            "4. Technical requirements and dependencies",
            "5. Security considerations and best practices",
            "6. Scalability and optimization techniques",
            "7. Integration patterns and APIs",
            "8. Troubleshooting common issues"
        ]
    
    def _build_comparison_query(self, topic: str, questions: List[str]) -> List[str]:
        """Build query for comparison topics"""
        return [
            f"Provide detailed comparison research on: {topic}",
            "",
            "COMPARISON RESEARCH FOCUS:",
            "1. Key differences and similarities",
            "2. Performance benchmarks and metrics",
            "3. Cost analysis and pricing models",
            "4. Use case suitability",
            "5. Pros and cons of each option",
            "6. Market share and adoption rates",
            "7. Feature comparison matrix",
            "8. Decision criteria and recommendations"
        ]
    
    def _build_howto_query(self, topic: str, questions: List[str]) -> List[str]:
        """Build query for how-to topics"""
        return [
            f"Provide step-by-step research on: {topic}",
            "",
            "HOW-TO RESEARCH FOCUS:",
            "1. Prerequisites and requirements",
            "2. Step-by-step implementation process",
            "3. Tools and technologies needed",
            "4. Common configuration options",
            "5. Best practices and optimization tips",
            "6. Troubleshooting and error handling",
            "7. Testing and validation methods",
            "8. Maintenance and updates"
        ]
    
    def _build_general_query(self, topic: str, questions: List[str]) -> List[str]:
        """Build query for general topics"""
        return [
            f"Research the topic: {topic}",
            "",
            "COMPREHENSIVE RESEARCH FOCUS:",
            "1. Key definitions and core concepts",
            "2. Current industry statistics and trends",
            "3. Benefits and advantages",
            "4. Common use cases and applications",
            "5. Implementation considerations",
            "6. Industry best practices",
            "7. Future outlook and emerging trends"
        ]
    
    def research_topic(self, 
                      primary_keyword: str, 
                      headings: List[Dict[str, str]], 
                      context: Optional[str] = None) -> Dict[str, Any]:
        """
        Research a topic using Perplexity API
        
        Args:
            primary_keyword: Main topic to research
            headings: List of headings to research
            context: Additional context (e.g., Gcore-specific focus)
            
        Returns:
            Dictionary with research results
        """
        if not self.api_key:
            return {
                'status': 'error',
                'message': 'Perplexity API key not configured',
                'data': {}
            }
        
        # Build research query
        research_query = self._build_research_query(primary_keyword, headings, context)
        
        try:
            # Make API request with topic for smart filtering
            response = self._make_perplexity_request(research_query, primary_keyword)
            
            # Process and structure the response
            research_data = self._process_research_response(response, primary_keyword)
            
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'topic': primary_keyword,
                'data': research_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'data': {}
            }
    
    def _build_research_query(self, 
                             primary_keyword: str, 
                             headings: List[Dict[str, str]], 
                             context: Optional[str] = None) -> str:
        """Build a simple, specific research query following Perplexity best practices"""
        
        # Build a specific, search-friendly query (not complex instructions)
        query = f"Research {primary_keyword}: provide 10-15 key facts, current statistics with sources, technical specifications, and real-world examples. Focus on 2024-2025 data and industry standards."
        
        # Add top 3-5 specific questions if provided (not all headings)
        questions = [h['text'] for h in headings if h.get('text')]
        if questions:
            # Only include the most important questions to keep query focused
            top_questions = questions[:5]
            query += " Specifically answer: " + ", ".join(top_questions)
        
        # Add brief context if it's about Gcore-relevant topics
        if any(term in primary_keyword.lower() for term in ['cdn', 'edge', 'cloud', 'gpu', 'ai']):
            query += " Include performance metrics, scalability considerations, and best practices."
        
        return query
    
    def _make_perplexity_request(self, query: str, topic: str = None) -> Dict[str, Any]:
        """Make a request to Perplexity API with structured output and smart filtering"""
        
        # Determine if we should use academic mode
        use_academic = any(term in (topic or query).lower() for term in 
                          ['research', 'study', 'science', 'technical', 'algorithm', 
                           'architecture', 'protocol', 'specification'])
        
        # Build payload with structured output for reliable extraction
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant. Be concise and factual."
                },
                {
                    "role": "user",
                    "content": query + "\n\nReturn the research as a JSON object with these fields: facts (array of key facts), statistics (array of objects with 'value' and 'context'), key_points (array of important points), examples (array of real-world examples)."
                }
            ],
            "temperature": 0.1,  # Low temperature for factual accuracy
            "max_tokens": 3000,
            # Add structured output with JSON schema
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "facts": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "10-15 key facts about the topic"
                            },
                            "statistics": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "value": {"type": "string", "description": "The statistical value"},
                                        "context": {"type": "string", "description": "What the statistic represents"}
                                    },
                                    "required": ["value", "context"]
                                },
                                "description": "Relevant statistics with context"
                            },
                            "key_points": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Main takeaways and important points"
                            },
                            "examples": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Real-world examples and use cases"
                            }
                        },
                        "required": ["facts", "statistics", "key_points", "examples"]
                    }
                }
            }
        }
        
        # Add academic mode if appropriate
        if use_academic:
            payload["search_mode"] = "academic"
            payload["web_search_options"] = {
                "search_context_size": "high"
            }
        
        # Add domain filtering for quality sources
        # Include reliable sources
        quality_domains = [
            "wikipedia.org",
            "arxiv.org",
            "ieee.org",
            "acm.org",
            "nature.com",
            "sciencedirect.com",
            "stackoverflow.com",
            "github.com",
            "docs.microsoft.com",
            "aws.amazon.com/documentation"
        ]
        
        # Exclude low-quality sources
        exclude_domains = [
            "-pinterest.com",
            "-quora.com"
        ]
        
        # For technical topics, use quality filtering
        if any(term in (topic or query).lower() for term in ['cloud', 'cdn', 'gpu', 'ai', 'technical']):
            # Don't filter too strictly - just exclude the worst sources
            payload["search_domain_filter"] = exclude_domains
        
        # Add debug logging
        import logging
        logging.debug(f"Perplexity Request Query: {query}")
        if use_academic:
            logging.debug("Using academic mode for research")
        
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")
        
        # Log response for debugging
        response_json = response.json()
        logging.debug(f"Perplexity Response Structure: {list(response_json.keys())}")
        if 'citations' in response_json:
            logging.debug(f"Citations found: {len(response_json.get('citations', []))}")
        
        return response_json
    
    def _deduplicate_statistics(self, statistics: List[Any]) -> List[Any]:
        """Remove duplicate statistics based on key numbers"""
        seen_keys = set()
        deduped = []
        
        for stat in statistics:
            # Extract the key number from the statistic
            stat_text = stat.get('text', '') if isinstance(stat, dict) else str(stat)
            
            # Look for key patterns to identify duplicates
            import re
            key_patterns = [
                r'99\.9+%',  # High availability percentages
                r'\d+(?:\.\d+)?%',  # Any percentage
                r'\d+\s*(?:billion|million)',  # Large numbers
                r'\$[\d.]+',  # Money amounts
            ]
            
            stat_key = None
            for pattern in key_patterns:
                match = re.search(pattern, stat_text.lower())
                if match:
                    stat_key = match.group(0)
                    break
            
            # If we found a key and haven't seen it, keep the stat
            if stat_key:
                if stat_key not in seen_keys:
                    seen_keys.add(stat_key)
                    deduped.append(stat)
            else:
                # No clear key, keep it (but limit total)
                if len(deduped) < 5:
                    deduped.append(stat)
        
        return deduped
    
    def _process_research_response(self, response: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Process and structure the Perplexity API response with enhanced source tracking"""
        
        # Extract the main content
        content = ""
        if 'choices' in response and len(response['choices']) > 0:
            content = response['choices'][0]['message']['content']
        
        # Extract sources using source manager with enhanced extraction
        sources = self.source_manager.extract_sources_from_perplexity(response)
        
        # Store raw response for debugging
        self._store_raw_response(response, topic)
        
        # Try to parse structured JSON output
        structured_data = None
        if content:
            try:
                import json
                # If content is JSON, parse it directly
                structured_data = json.loads(content)
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code blocks or mixed content
                import re
                # Look for JSON in code blocks
                json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
                json_match = re.search(json_pattern, content, re.DOTALL)
                if json_match:
                    try:
                        structured_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass

                # Try to find raw JSON object in content
                if not structured_data:
                    json_obj_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                    json_matches = re.findall(json_obj_pattern, content, re.DOTALL)
                    for match in json_matches:
                        try:
                            structured_data = json.loads(match)
                            # Validate it has expected fields
                            if 'facts' in structured_data or 'statistics' in structured_data:
                                break
                            structured_data = None
                        except json.JSONDecodeError:
                            continue

                # If still no structured data, log and use fallback
                if not structured_data:
                    import logging
                    logging.warning(f"Failed to parse JSON from Perplexity response. Content preview: {content[:200]}")
                    logging.debug(f"JSON parsing error: {str(e)}")
        
        # If we have structured data, use it directly
        if structured_data and isinstance(structured_data, dict):
            # Deduplicate statistics FIRST
            deduped_stats = self._deduplicate_statistics(structured_data.get('statistics', []))
            
            # Format statistics with selective source attribution
            formatted_stats = []
            for i, stat in enumerate(deduped_stats):
                if isinstance(stat, dict):
                    stat_text = f"{stat.get('value', '')} - {stat.get('context', '')}"
                    # Only add sources to the first few most important statistics
                    source = None
                    if sources and i < 3:  # Only cite first 3 stats
                        source = sources[min(i, len(sources) - 1)]
                    if source:
                        formatted_stat = self.source_manager.format_statistic_with_source(stat_text, source)
                    else:
                        formatted_stat = stat_text if stat_text.endswith('.') else f"{stat_text}."
                    formatted_stats.append({'text': formatted_stat, 'original': stat_text, 'source': source})
                else:
                    formatted_stats.append({'text': str(stat), 'original': str(stat), 'source': None})
            
            # Process facts - clean competitors and format with citations
            formatted_facts = []
            for fact in structured_data.get('facts', []):
                # Clean competitor mentions from fact first
                cleaned_fact = self._clean_competitor_mentions_from_research(fact)
                
                # Check if this fact needs a citation
                if self.source_manager.needs_citation(cleaned_fact):
                    # Only cite the most important facts with specific data
                    source = sources[0] if sources else None
                    if source:
                        formatted_fact = self.source_manager.format_inline_citation(cleaned_fact, source)
                    else:
                        formatted_fact = cleaned_fact
                else:
                    formatted_fact = cleaned_fact if cleaned_fact.endswith('.') else f"{cleaned_fact}."
                formatted_facts.append({'text': formatted_fact, 'original': fact})
            
            research_data = {
                'raw_content': content,
                'facts': formatted_facts,
                'statistics': formatted_stats,
                'key_points': structured_data.get('key_points', []),
                'examples': structured_data.get('examples', []),
                'technical_specs': self._extract_technical_specs(content, topic),
                'sources': sources,
                'formatted_sources': self.source_manager.generate_source_reference_section(sources)
            }
        else:
            # Fallback to regex extraction if structured output fails
            # Extract raw statistics first, then deduplicate
            raw_stats = self._extract_statistics_with_sources(content, sources)
            deduped_stats = self._deduplicate_statistics(raw_stats)
            
            research_data = {
                'raw_content': content,
                'facts': self._extract_facts_with_sources(content, sources),
                'statistics': deduped_stats,  # Use deduplicated statistics
                'key_points': self._extract_key_points(content),
                'examples': self._extract_examples(content),
                'technical_specs': self._extract_technical_specs(content, topic),
                'sources': sources,
                'formatted_sources': self.source_manager.generate_source_reference_section(sources)
            }
        
        # Validate and score the research quality
        research_data['quality_score'] = self._validate_research_quality(research_data)
        research_data['coverage_gaps'] = self._identify_coverage_gaps(research_data, topic)
        
        # Store sources for later reference
        if sources:
            source_file = self.source_manager.store_sources(sources)
            research_data['source_file'] = source_file
        
        return research_data
    
    def _store_raw_response(self, response: Dict[str, Any], topic: str):
        """Store raw API response for debugging source attribution issues"""
        try:
            import json
            from pathlib import Path
            from datetime import datetime
            
            debug_dir = Path("debug_responses")
            debug_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = debug_dir / f"research_{topic.replace(' ', '_')}_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(response, f, indent=2)
                
        except Exception as e:
            # Don't fail research if debug storage fails
            print(f"Debug storage failed: {e}")
    
    def _clean_competitor_mentions_from_research(self, text: str) -> str:
        """Remove competitor mentions from research data to prevent them appearing in content"""
        import re
        
        # Define competitor replacement patterns for research data
        replacements = [
            # Major cloud providers
            (r'\b(?:AWS|Amazon Web Services|Amazon EC2)\b', 'major cloud providers'),
            (r'\b(?:Microsoft Azure|Azure GPU|Azure ML|Azure)\b', 'enterprise cloud platforms'),
            (r'\b(?:Google Cloud|Google Cloud Platform|GCP)\b', 'leading cloud platforms'),
            
            # Multiple competitors mentioned together  
            (r'\b(?:AWS|Amazon),?\s*(?:Azure|Microsoft),?\s*(?:and\s+)?(?:Google Cloud|GCP)\b', 'major cloud providers'),
            (r'\b(?:AWS|Amazon)\s*,\s*(?:Google Cloud|GCP)\s*,?\s*(?:and\s+)?(?:Azure|Microsoft)\b', 'leading cloud platforms'),
            
            # Other competitors
            (r'\b(?:Oracle Cloud|IBM Cloud|Alibaba Cloud|DigitalOcean)\b', 'cloud platforms'),
            (r'\b(?:Cloudflare|Fastly|Akamai|KeyCDN)\b', 'CDN providers'),
        ]
        
        cleaned_text = text
        for pattern, replacement in replacements:
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
        
        return cleaned_text
    
    def _extract_facts_with_sources(self, content: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract facts with selective source attribution"""
        facts = self._extract_facts(content)
        
        # Clean competitor mentions from facts first
        cleaned_facts = [self._clean_competitor_mentions_from_research(fact) for fact in facts]
        
        # Format facts with source attribution only when needed
        formatted_facts = []
        for i, fact in enumerate(cleaned_facts):
            # Check if fact contains citation numbers like [1], [2], etc.
            import re
            citation_pattern = r'\[(\d+)\]'
            citations = re.findall(citation_pattern, fact)
            
            source = None
            # Only look for source if the fact actually needs one
            if self.source_manager.needs_citation(fact):
                if citations and sources:
                    # Try to match citation number to source
                    citation_num = int(citations[0])
                    # Check if we have a source with this citation index
                    for s in sources:
                        if s.get('citation_index') == citation_num:
                            source = s
                            break
                    # Fallback to index-based matching
                    if not source and citation_num <= len(sources):
                        source = sources[citation_num - 1]
                elif sources:
                    # Only assign source if fact truly needs citation
                    # Check if this fact contains specific data that needs verification
                    if re.search(r'\d+(?:\.\d+)?(?:%|ms|GB|billion|million|\$)', fact):
                        source = sources[i % len(sources)]
            
            if source:
                # Format with inline citation
                formatted_fact = self.source_manager.format_inline_citation(fact, source)
            else:
                # Return fact without citation
                formatted_fact = fact if fact.endswith('.') else f"{fact}."
            
            formatted_facts.append({
                'text': formatted_fact,
                'original': fact,
                'source': source if source else None
            })
        
        return formatted_facts
    
    def _extract_statistics_with_sources(self, content: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract statistics with source attribution"""
        stats = self._extract_statistics(content)
        
        # Format statistics with source attribution (stats usually need sources)
        formatted_stats = []
        for i, stat in enumerate(stats):
            # Check if stat contains citation numbers like [1], [2], etc.
            import re
            citation_pattern = r'\[(\d+)\]'
            citations = re.findall(citation_pattern, stat)
            
            source = None
            if citations and sources:
                # Try to match citation number to source
                citation_num = int(citations[0])
                # Check if we have a source with this citation index
                for s in sources:
                    if s.get('citation_index') == citation_num:
                        source = s
                        break
                # Fallback to index-based matching
                if not source and citation_num <= len(sources):
                    source = sources[citation_num - 1]
            elif sources and len(sources) > 0:
                # For statistics, we want to be selective about which ones get citations
                # Only assign source to the most significant statistics
                if i < 3:  # Only cite the first few most important stats
                    source = sources[min(i, len(sources) - 1)]
            
            if source:
                # Format with proper attribution
                formatted_stat = self.source_manager.format_statistic_with_source(stat, source)
            else:
                formatted_stat = stat if stat.endswith('.') else f"{stat}."
            
            formatted_stats.append({
                'text': formatted_stat,
                'original': stat,
                'source': source if source else None
            })
        
        return formatted_stats
    
    def _extract_facts(self, content: str) -> List[str]:
        """Extract factual statements from content with improved NLP patterns"""
        import re
        facts = []
        seen_facts = set()  # Avoid duplicates

        # Split content into sentences first (better than lines)
        # Handle multiple sentence endings and preserve structure
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', content)

        # Pattern 1: Definition patterns (complete sentences)
        definition_patterns = [
            r'^[A-Z][\w\s,]+ (?:is|are|refers to|means|involves|consists of|represents) [^.]+\.',
            r'^[A-Z][\w\s,]+ (?:can be defined as|is defined as|is known as) [^.]+\.',
            r'^(?:A |An |The )?[A-Z][\w\s,]+ (?:is a|is an|are) [^.]+\.'
        ]

        # Pattern 2: Statistical/numerical facts (complete sentences)
        stat_fact_pattern = r'^[A-Z][^.]*\d+(?:\.\d+)?(?:%|\s*percent|\s*times|x|\s*fold)[^.]*\.'

        # Pattern 3: Feature/characteristic descriptions (complete sentences)
        feature_patterns = [
            r'^[A-Z][^.]*(?:provides|offers|enables|allows|supports|includes|features) [^.]+\.',
            r'^[A-Z][^.]*(?:capable of|used for|designed for|suitable for) [^.]+\.'
        ]

        # Pattern 4: Process and action facts
        process_patterns = [
            r'^[A-Z][^.]*(?:works by|operates by|functions by|processes|handles) [^.]+\.',
            r'^(?:The|This) (?:system|technology|method|approach) [^.]*\.'
        ]

        # Process each sentence
        for sentence in sentences:
            sentence = sentence.strip()

            # Skip too short or too long sentences
            if len(sentence) < 20 or len(sentence) > 400:
                continue

            # Ensure sentence ends with punctuation
            if not sentence.endswith(('.', '!', '?')):
                sentence = sentence + '.'

            # Check if sentence matches any pattern
            is_fact = False

            # Check definition patterns
            for pattern in definition_patterns:
                if re.match(pattern, sentence):
                    is_fact = True
                    break

            # Check statistical pattern
            if not is_fact and re.match(stat_fact_pattern, sentence):
                is_fact = True

            # Check feature patterns
            if not is_fact:
                for pattern in feature_patterns:
                    if re.match(pattern, sentence):
                        is_fact = True
                        break

            # Check process patterns
            if not is_fact:
                for pattern in process_patterns:
                    if re.match(pattern, sentence):
                        is_fact = True
                        break

            # Add unique facts
            if is_fact and sentence not in seen_facts:
                facts.append(sentence)
                seen_facts.add(sentence)

        # Also extract from numbered/bulleted lists in original content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()

            # Check for numbered lists
            numbered_match = re.match(r'^\d+\.\s+(.+)', line)
            if numbered_match:
                fact = numbered_match.group(1).strip()
                if not fact.endswith('.'):
                    fact += '.'
                if fact and fact not in seen_facts and len(fact) > 20:
                    facts.append(fact)
                    seen_facts.add(fact)

            # Check for bulleted lists
            bullet_match = re.match(r'^[•\-\*]\s+(.+)', line)
            if bullet_match:
                fact = bullet_match.group(1).strip()
                if not fact.endswith('.'):
                    fact += '.'
                if fact and fact not in seen_facts and len(fact) > 20:
                    facts.append(fact)
                    seen_facts.add(fact)
        
        return facts[:25]  # Return more facts
    
    def _extract_statistics(self, content: str) -> List[str]:
        """Extract statistics and numerical data with enhanced patterns"""
        import re

        statistics = []
        seen_stats = set()
        lines = content.split('\n')

        # Enhanced patterns for different types of statistics
        # Use full line capture to avoid truncation
        stat_patterns = [
            # Percentages with context
            (r'[^.]*\d+(?:\.\d+)?\s*(?:%|percent)[^.]*\.', 'percentage'),
            # Time measurements with context
            (r'[^.]*\d+(?:\.\d+)?\s*(?:ms|milliseconds?|seconds?|minutes?|hours?|days?|weeks?|months?|years?)[^.]*\.', 'time'),
            # Data sizes with context
            (r'[^.]*\d+(?:\.\d+)?\s*(?:[KMGT]B|[kmgt]b|bytes?|kilobytes?|megabytes?|gigabytes?|terabytes?)[^.]*\.', 'size'),
            # Speed/bandwidth with context
            (r'[^.]*\d+(?:\.\d+)?\s*(?:[KMG]bps|Mbps|Gbps|requests?/sec|ops/sec)[^.]*\.', 'speed'),
            # Counts/quantities with context
            (r'[^.]*\d+(?:\.\d+)?\s*(?:billion|million|thousand|users?|servers?|locations?|PoPs?|nodes?)[^.]*\.', 'count'),
            # Comparisons with context
            (r'[^.]*\d+(?:\.\d+)?\s*(?:x|times|fold)\s+(?:faster|slower|better|worse|more|less)[^.]*\.', 'comparison'),
            # Monetary with context
            (r'[^.]*\$\d+(?:\.\d+)?(?:\s*[BMK])?(?:\s*(?:billion|million|thousand))?[^.]*\.', 'monetary'),
            # Uptime/availability with context
            (r'[^.]*\d+(?:\.\d+)?\s*(?:9s|nines|%\s*uptime|%\s*availability)[^.]*\.', 'availability'),
            # Year-based statistics (e.g., "In 2024, X increased by Y%")
            (r'(?:In|By|Since)\s+20\d{2}[^.]*\d+(?:\.\d+)?(?:%|percent|million|billion)[^.]*\.', 'yearly'),
            # Growth/change statistics
            (r'[^.]*(?:increased|decreased|grew|declined|rose|fell)\s+by\s+\d+(?:\.\d+)?(?:%|percent)[^.]*\.', 'growth')
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip lines that are too short, but allow longer lines
            if len(line) < 15 or len(line) > 400:  # Increased max length
                continue
            
            # Check each pattern
            for pattern, stat_type in stat_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Get the full line as the statistic
                    stat_text = line.strip('•-* ').strip()
                    
                    # Clean up the statistic
                    stat_text = re.sub(r'^\d+\.\s+', '', stat_text)  # Remove numbering
                    stat_text = re.sub(r'\s+', ' ', stat_text)  # Normalize whitespace
                    
                    # Fix common truncation issues
                    # Check if line seems truncated (ends without proper punctuation)
                    if stat_text and len(stat_text) > 0 and stat_text[-1] not in '.!?;]':
                        # Try to find if this is part of a sentence that continues
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            # If next line doesn't start with a bullet/number, it might be continuation
                            if next_line and not re.match(r'^[•\-\*\d]+', next_line):
                                stat_text = stat_text + ' ' + next_line.strip('•-* ').strip()
                    
                    # Ensure it contains meaningful context
                    if stat_text and stat_text not in seen_stats:
                        # Check if it has enough context words
                        words = stat_text.split()
                        if len(words) >= 3:  # At least 3 words for context
                            # Truncate if still too long, but keep complete sentences
                            if len(stat_text) > 300:
                                # Try to cut at sentence boundary
                                sentences = re.split(r'(?<=[.!?])\s+', stat_text)
                                if sentences:
                                    stat_text = sentences[0]
                            
                            statistics.append(stat_text)
                            seen_stats.add(stat_text)
                            break  # Move to next line after finding a stat
        
        # Sort statistics by relevance (those with more context first)
        statistics.sort(key=lambda x: len(x.split()), reverse=True)
        
        return statistics[:20]  # Return more statistics
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points and main ideas with improved detection"""
        import re
        key_points = []
        seen_points = set()
        lines = content.split('\n')
        
        # Section headers that indicate key points
        section_markers = [
            'KEY POINT', 'IMPORTANT', 'NOTE', 'TIP', 'BEST PRACTICE',
            'RECOMMENDATION', 'CONSIDERATION', 'REQUIREMENT', 'BENEFIT',
            'ADVANTAGE', 'FEATURE', 'CAPABILITY'
        ]
        
        # Process lines
        current_section = None
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if this is a section header
            line_upper = line.upper()
            for marker in section_markers:
                if marker in line_upper:
                    current_section = marker
                    # Extract the point from the same line if present
                    if ':' in line:
                        point = line.split(':', 1)[1].strip()
                        if point and point not in seen_points and len(point) > 15:
                            key_points.append(point)
                            seen_points.add(point)
                    break
            
            # Extract numbered points
            numbered_match = re.match(r'^(\d+\.|\w\)|•|-)\s+(.+)', line)
            if numbered_match:
                point = numbered_match.group(2).strip()
                if point and point not in seen_points and len(point) > 15:
                    # Prioritize points that are complete sentences
                    if point[0].isupper() and (point.endswith('.') or len(point) > 50):
                        key_points.append(point)
                        seen_points.add(point)
            
            # Extract points from specific patterns
            patterns = [
                r'^(?:This|It|These|They)\s+(?:enables?|allows?|provides?|offers?|ensures?|helps?|supports?).+',
                r'^(?:You can|Users can|Organizations can|Companies can).+',
                r'^(?:The main|The primary|The key|A key|One of the).+(?:benefit|advantage|feature|capability).+'
            ]
            
            for pattern in patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    if line not in seen_points and len(line) > 20:
                        key_points.append(line)
                        seen_points.add(line)
                        break
        
        # Deduplicate and prioritize
        # Sort by length (assuming longer points have more detail)
        key_points.sort(key=lambda x: len(x), reverse=True)
        
        return key_points[:15]  # Return more key points
    
    def _extract_examples(self, content: str) -> List[str]:
        """Extract examples and use cases with better context"""
        import re
        examples = []
        seen_examples = set()
        lines = content.split('\n')
        
        # Example indicators
        example_indicators = [
            'for example', 'for instance', 'e.g.', 'such as', 'including',
            'like', 'consider', 'imagine', 'suppose', 'let\'s say',
            'use case', 'scenario', 'application', 'implementation'
        ]
        
        # Process lines with context
        for i, line in enumerate(lines):
            line = line.strip().strip('•-*').strip()
            line_lower = line.lower()
            
            # Check for example indicators
            for indicator in example_indicators:
                if indicator in line_lower:
                    # Extract the example with context
                    example_text = line
                    
                    # If the example continues on the next line, include it
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        # Check if next line is a continuation (not a new section)
                        if next_line and not next_line[0].isdigit() and not next_line.startswith(('•', '-', '*')):
                            if len(example_text + ' ' + next_line) < 300:
                                example_text += ' ' + next_line
                    
                    # Clean up the example
                    example_text = re.sub(r'^\d+\.\s+', '', example_text)
                    
                    if example_text not in seen_examples and len(example_text) > 25:
                        examples.append(example_text)
                        seen_examples.add(example_text)
                        break
            
            # Look for use case patterns
            use_case_patterns = [
                r'^(?:Common use cases?|Typical applications?|Real-world examples?):',
                r'^(?:Used for|Applied in|Implemented for|Deployed in):',
                r'^(?:Companies|Organizations|Businesses)\s+(?:use|implement|deploy|leverage)'
            ]
            
            for pattern in use_case_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    if line not in seen_examples and len(line) > 25:
                        examples.append(line)
                        seen_examples.add(line)
                        break
        
        return examples[:12]  # Return more examples
    
    def _extract_technical_specs(self, content: str, topic: str) -> Dict[str, Any]:
        """Extract technical specifications relevant to the topic"""
        specs = {}
        
        # Look for Gcore-specific metrics if relevant
        if any(term in topic.lower() for term in ['cdn', 'edge', 'cloud', 'gcore']):
            specs['infrastructure'] = {
                'pops': GCORE_INFO['pops'],
                'latency': GCORE_INFO['average_latency'],
                'services': list(GCORE_INFO['services'].keys())
            }
        
        # Extract any technical specifications from content
        lines = content.split('\n')
        for line in lines:
            if any(term in line.lower() for term in ['latency', 'bandwidth', 'throughput', 'capacity', 'performance']):
                # Try to extract the spec
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip().lower().replace(' ', '_')
                        value = parts[1].strip()
                        specs[key] = value
        
        return specs
    
    def _extract_sources(self, response: Dict[str, Any]) -> List[str]:
        """Extract sources from the API response"""
        sources = []
        
        # Perplexity often includes sources in the response
        if 'sources' in response:
            sources = response['sources']
        
        # Also check for citations in the content
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # Look for URLs or citations
        import re
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, content)
        sources.extend(urls)
        
        # Look for formatted citations
        citation_pattern = r'\[[\d]+\]|\([\w\s]+,\s*\d{4}\)'
        citations = re.findall(citation_pattern, content)
        sources.extend(citations)
        
        # Remove duplicates and return
        return list(set(sources))[:10]
    
    def _validate_research_quality(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of extracted research data"""
        quality_score = {
            'overall': 0,
            'facts_score': 0,
            'statistics_score': 0,
            'examples_score': 0,
            'completeness': 0,
            'recency': 0
        }
        
        # Score based on quantity and quality of extracted data
        facts = research_data.get('facts', [])
        stats = research_data.get('statistics', [])
        examples = research_data.get('examples', [])
        key_points = research_data.get('key_points', [])
        
        # Facts scoring (0-25 points)
        if len(facts) >= 10:
            quality_score['facts_score'] = 25
        elif len(facts) >= 5:
            quality_score['facts_score'] = 15
        elif len(facts) >= 3:
            quality_score['facts_score'] = 10
        else:
            quality_score['facts_score'] = 5
        
        # Statistics scoring (0-25 points)
        if len(stats) >= 8:
            quality_score['statistics_score'] = 25
        elif len(stats) >= 5:
            quality_score['statistics_score'] = 15
        elif len(stats) >= 3:
            quality_score['statistics_score'] = 10
        else:
            quality_score['statistics_score'] = 5
        
        # Examples scoring (0-20 points)
        if len(examples) >= 5:
            quality_score['examples_score'] = 20
        elif len(examples) >= 3:
            quality_score['examples_score'] = 12
        else:
            quality_score['examples_score'] = 5
        
        # Completeness (0-20 points)
        total_content = len(facts) + len(stats) + len(examples) + len(key_points)
        if total_content >= 30:
            quality_score['completeness'] = 20
        elif total_content >= 20:
            quality_score['completeness'] = 12
        elif total_content >= 10:
            quality_score['completeness'] = 8
        else:
            quality_score['completeness'] = 4
        
        # Check for recency (0-10 points)
        import re
        raw_content = research_data.get('raw_content', '')
        year_pattern = r'\b(202[3-5])\b'
        recent_years = re.findall(year_pattern, raw_content)
        if '2025' in recent_years or '2024' in recent_years:
            quality_score['recency'] = 10
        elif '2023' in recent_years:
            quality_score['recency'] = 5
        else:
            quality_score['recency'] = 2
        
        # Calculate overall score
        quality_score['overall'] = sum([
            quality_score['facts_score'],
            quality_score['statistics_score'],
            quality_score['examples_score'],
            quality_score['completeness'],
            quality_score['recency']
        ])
        
        # Add quality rating
        if quality_score['overall'] >= 80:
            quality_score['rating'] = 'Excellent'
        elif quality_score['overall'] >= 60:
            quality_score['rating'] = 'Good'
        elif quality_score['overall'] >= 40:
            quality_score['rating'] = 'Fair'
        else:
            quality_score['rating'] = 'Poor'
        
        return quality_score
    
    def _identify_coverage_gaps(self, research_data: Dict[str, Any], topic: str) -> List[str]:
        """Identify gaps in research coverage"""
        gaps = []
        
        # Check for missing data types
        if len(research_data.get('facts', [])) < 5:
            gaps.append("Limited factual information - consider additional research for definitions and concepts")
        
        if len(research_data.get('statistics', [])) < 3:
            gaps.append("Insufficient statistics - need more quantitative data and metrics")
        
        if len(research_data.get('examples', [])) < 3:
            gaps.append("Few practical examples - add more use cases and real-world applications")
        
        if not research_data.get('technical_specs'):
            gaps.append("Missing technical specifications - add performance metrics and requirements")
        
        # Check for topic-specific gaps
        topic_lower = topic.lower()
        raw_content = research_data.get('raw_content', '').lower()
        
        if 'security' in topic_lower and 'security' not in raw_content:
            gaps.append("Security aspects not covered - add security considerations")
        
        if 'performance' in topic_lower and not any(term in raw_content for term in ['latency', 'speed', 'throughput']):
            gaps.append("Performance metrics missing - add benchmarks and speed data")
        
        if 'cost' in topic_lower and not any(term in raw_content for term in ['price', 'cost', '$', 'budget']):
            gaps.append("Cost information missing - add pricing or cost considerations")
        
        if any(term in topic_lower for term in ['implement', 'setup', 'install', 'configure']):
            if 'step' not in raw_content and 'process' not in raw_content:
                gaps.append("Implementation steps missing - add detailed setup process")
        
        return gaps
    
    def get_quick_facts(self, topic: str) -> List[str]:
        """Get quick facts about a topic (simplified research)"""
        query = f"Provide 5 key facts about {topic} relevant to edge computing and CDN services. Focus on current 2024-2025 information."
        
        try:
            response = self._make_perplexity_request(query)
            content = response['choices'][0]['message']['content']
            return self._extract_facts(content)[:5]
        except:
            return []
    
    def research_competitors(self, topic: str, exclude_names: bool = True) -> Dict[str, Any]:
        """Research competitor approaches to a topic"""
        query = f"""
        Research how leading CDN and edge computing providers approach {topic}.
        Focus on:
        1. Common strategies and best practices
        2. Technical implementations
        3. Performance metrics and benchmarks
        4. Pricing models (general ranges, not specific numbers)
        
        Do not mention specific company names if possible, refer to them as "leading providers" or "major platforms".
        """
        
        try:
            response = self._make_perplexity_request(query)
            content = response['choices'][0]['message']['content']
            
            return {
                'strategies': self._extract_key_points(content),
                'benchmarks': self._extract_statistics(content),
                'best_practices': self._extract_facts(content)
            }
        except:
            return {}
    
    def validate_fact(self, fact: str) -> Dict[str, Any]:
        """Validate a specific fact or claim"""
        query = f"""
        Verify this claim: "{fact}"
        Provide:
        1. Whether this is accurate (true/false/partially true)
        2. Current accurate information if different
        3. Source or basis for verification
        """
        
        try:
            response = self._make_perplexity_request(query)
            content = response['choices'][0]['message']['content']
            
            return {
                'valid': 'true' in content.lower()[:100],
                'explanation': content,
                'verified_fact': self._extract_facts(content)[0] if self._extract_facts(content) else fact
            }
        except:
            return {'valid': None, 'explanation': 'Could not verify', 'verified_fact': fact}

# Convenience functions for use in Streamlit app
@st.cache_data(ttl=3600)  # Cache for 1 hour
def research_topic(primary_keyword: str, headings: List[Dict[str, str]]) -> Dict[str, Any]:
    """Cached research function for Streamlit"""
    engine = ResearchEngine()
    return engine.research_topic(primary_keyword, headings)

def get_quick_facts(topic: str) -> List[str]:
    """Get quick facts about a topic"""
    engine = ResearchEngine()
    return engine.get_quick_facts(topic)

def validate_fact(fact: str) -> Dict[str, Any]:
    """Validate a specific fact"""
    engine = ResearchEngine()
    return engine.validate_fact(fact)