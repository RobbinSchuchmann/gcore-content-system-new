"""
Source Management for Research Citations
Handles proper citation formatting and source tracking
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import json
from pathlib import Path

class CitationTracker:
    """Track citations globally to prevent duplicates and manage fact distribution"""
    
    def __init__(self):
        self.cited_stats: Set[str] = set()  # Track which statistics have been cited
        self.citation_count: int = 0        # Total citations in document
        self.max_citations_per_doc: int = 8 # Global maximum citations (increased from 5)
        self.stats_by_section: Dict[str, int] = {}  # Track citations per section
        self.fact_to_source: Dict[str, str] = {}  # Map facts to their sources
        self.used_facts_content: Set[str] = set()  # Track actual fact content to prevent repetition
        self.section_fact_count: Dict[str, int] = {}  # Track how many facts per section
        
    def extract_stat_key(self, text: str) -> str:
        """Extract a normalized key from a statistic for deduplication"""
        # Extract key numbers/percentages from the text
        
        # Look for key patterns
        patterns = [
            r'(\d+(?:\.\d+)?%)',  # Percentages
            r'(\d+\.?\d*)\s*(?:billion|million|thousand)',  # Large numbers
            r'99\.9+%',  # High availability percentages
            r'\$\d+(?:\.\d+)?',  # Money amounts
            r'\d+(?:\.\d+)?\s*(?:ms|milliseconds|seconds)',  # Time measurements
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1) if match.groups() else match.group(0)
        
        # Fallback: use first 30 chars of text as key
        return text[:30].lower()
    
    def should_cite(self, stat_text: str, section: str = "general") -> bool:
        """Determine if a statistic should be cited"""
        # Check global limit
        if self.citation_count >= self.max_citations_per_doc:
            return False
        
        # Check section limit (max 2 per section, 3 for introduction)
        section_limit = 3 if section.lower() in ["introduction", "intro", "general"] else 2
        if self.stats_by_section.get(section, 0) >= section_limit:
            return False
        
        # Check if this specific stat was already cited
        stat_key = self.extract_stat_key(stat_text)
        if stat_key in self.cited_stats:
            return False
        
        # Enhanced fact content deduplication
        fact_fingerprint = self._create_fact_fingerprint(stat_text)
        if fact_fingerprint in self.used_facts_content:
            return False
        
        # Check if it's significant enough to cite
        if not self._is_significant_stat(stat_text):
            return False
        
        return True
    
    def _create_fact_fingerprint(self, text: str) -> str:
        """Create a normalized fingerprint of fact content to detect duplicates"""
        import re
        
        # Extract key numbers and concepts
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        
        # Extract key concepts (market, growth, billion, etc.)
        key_terms = re.findall(r'\b(?:market|growth|billion|million|trillion|CAGR|projected|forecast|expected|reach|grow)\b', 
                              text.lower())
        
        # Create fingerprint from numbers + key terms
        fingerprint = ''.join(numbers) + '_' + '_'.join(sorted(set(key_terms)))
        return fingerprint
    
    def check_fact_duplication(self, fact_text: str) -> bool:
        """Check if a fact (not just statistic) has already been used"""
        fact_fingerprint = self._create_fact_fingerprint(fact_text)
        return fact_fingerprint in self.used_facts_content
    
    def record_fact_usage(self, fact_text: str, section: str = "general", source: str = ""):
        """Record that a fact has been used to prevent repetition"""
        fact_fingerprint = self._create_fact_fingerprint(fact_text)
        self.used_facts_content.add(fact_fingerprint)
        self.section_fact_count[section] = self.section_fact_count.get(section, 0) + 1
        
        if source:
            self.fact_to_source[fact_fingerprint] = source
    
    def _is_significant_stat(self, text: str) -> bool:
        """Check if a statistic is significant enough to warrant citation"""
        
        # More flexible patterns to catch important statistics
        significant_patterns = [
            r'[23456789]\d%',  # 20%+ percentages  
            r'99\.9+%',  # High availability
            r'\d+\s*(?:billion|million)',  # Large scale numbers
            r'\$\d+',  # Any monetary values (will be filtered by needs_citation)
            r'(?:reduce|increase|improve|grow|CAGR).*?\d+',  # Growth/improvement metrics
            r'\d+.*?(?:ms|milliseconds|seconds)',  # Time metrics
            r'(?:research|study|according)',  # Research mentions
        ]
        
        text_lower = text.lower()
        for pattern in significant_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def record_citation(self, stat_text: str, section: str = "general"):
        """Record that a statistic has been cited"""
        stat_key = self.extract_stat_key(stat_text)
        self.cited_stats.add(stat_key)
        self.citation_count += 1
        self.stats_by_section[section] = self.stats_by_section.get(section, 0) + 1
    
    def reset(self):
        """Reset tracker for new document"""
        self.cited_stats.clear()
        self.citation_count = 0
        self.stats_by_section.clear()
        self.fact_to_source.clear()
        self.used_facts_content.clear()
        self.section_fact_count.clear()

class SourceManager:
    """Manage research sources and citations"""
    
    def __init__(self):
        self.sources = []
        self.citation_map = {}
        self.source_counter = 0
        self.citation_tracker = CitationTracker()  # Add global citation tracker
        
    def needs_citation(self, statement: str, section: str = "general") -> bool:
        """
        Determine if a statement needs a citation based on its content.
        
        Citations are needed for:
        - Specific statistics and percentages
        - Research findings and study results
        - Technical specifications and standards
        - Industry benchmarks and metrics
        - Claims that need verification
        
        Citations are NOT needed for:
        - General definitions
        - Basic explanations
        - Common knowledge
        - Simple descriptions
        
        Args:
            statement: The statement to evaluate
            
        Returns:
            True if citation is needed, False otherwise
        """
        # First check with citation tracker - if we've hit limits, no more citations
        if not self.citation_tracker.should_cite(statement, section):
            return False
        
        statement_lower = statement.lower()
        
        # Updated patterns to include market and financial projections
        exceptional_patterns = [
            # High percentages or high precision
            r'[789]\d%',  # 70-99%
            r'[234]\d%.*?(?:reduce|increase|improve|grow|CAGR)',  # 20%+ with growth/improvement context
            r'99\.9+%',  # 99.9%+ availability/durability
            
            # Financial projections and market data (ALWAYS cite these)
            r'\$\d+(?:\.\d+)?\s*(?:trillion|billion|million)\b',  # Any market size projections
            r'(?:market|revenue|spending).*?\$\d+',  # Market revenue/spending
            r'(?:projected|forecast|expected).*?\$\d+',  # Financial forecasts
            r'(?:reach|grow|increase).*?\$\d+(?:\.\d+)?\s*(?:trillion|billion)',  # Growth to X trillion/billion
            
            # Large scale numbers with significance
            r'\d+\s*(?:billion|million)\s+(?:users|customers|enterprises)',
            r'\$\d+(?:\.\d+)?.*?per\s+',  # Specific pricing (more flexible)
            
            # Performance metrics - more flexible
            r'(?:reduce|increase|improve|reduced).*?\d+%',  # Any % improvements
            r'\d+(?:-\d+)?\s*(?:ms|milliseconds|seconds)',  # Time measurements
            r'(?:average|latency|response).*?\d+',  # Performance metrics
            
            # Research/study results with specific numbers
            r'(?:study|research|survey|report|according).*?(?:shows|found|reveals)?.*?\d+',
            r'(?:CAGR|growth).*?\d+%',  # Growth rates
            
            # Market projections and forecasts (high priority)
            r'(?:by\s+20\d{2}).*?\$\d+(?:\.\d+)?\s*(?:trillion|billion)',  # "by 2025, $1.25 trillion"
            r'(?:projected|forecast|expected|anticipated).*?(?:trillion|billion)',  # Market forecasts
        ]
        
        # Check if it's exceptional enough
        is_exceptional = False
        for pattern in exceptional_patterns:
            if re.search(pattern, statement_lower, re.IGNORECASE):
                is_exceptional = True
                break
        
        if not is_exceptional:
            return False
        
        # Patterns that indicate NO citation is needed
        no_citation_patterns = [
            # Basic definitions
            r'^[\w\s]+\s+(?:is|are|refers to|means)\s+(?:a|an|the)?\s+',
            r'^(?:a|an|the)?\s*[\w\s]+\s+(?:is|are)\s+(?:used|designed|built)\s+(?:for|to)',
            
            # General descriptions
            r'^(?:this|these|it)\s+(?:allows|enables|provides|offers|includes)',
            r'^users?\s+can\s+',
            r'^you\s+can\s+',
            
            # Common knowledge
            r'commonly\s+(?:used|known|understood)',
            r'typically\s+(?:includes|involves|requires)',
            r'generally\s+(?:refers|means|includes)',
        ]
        
        # Check if it's a general statement that doesn't need citation
        for pattern in no_citation_patterns:
            if re.match(pattern, statement_lower):
                # Even if it matches a no-citation pattern, override if it has specific numbers
                if not re.search(r'\d+(?:\.\d+)?(?:%|ms|GB|TB|Mbps|Gbps)', statement):
                    return False
        
        # Default: only cite if statement contains specific data
        # More flexible pattern to catch various numeric formats
        has_specific_data = bool(re.search(
            r'(?:\d+(?:-\d+)?(?:\.\d+)?)\s*(?:%|ms|milliseconds?|seconds?|minutes?|hours?|GB|TB|MB|Mbps|Gbps|users?|servers?|billion|million)|' +
            r'\$\d+(?:\.\d+)?',  # Dollar amounts (separate pattern for better matching)
            statement
        ))
        
        return has_specific_data
        
    def extract_sources_from_perplexity(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and format sources from Perplexity API response
        
        Args:
            response: Perplexity API response
            
        Returns:
            List of formatted source dictionaries
        """
        extracted_sources = []
        
        # Primary: Check for citations field (current Perplexity format - contains URLs)
        # Citations correspond to [1], [2], etc. in the content
        if 'citations' in response:
            for i, url in enumerate(response['citations']):
                if isinstance(url, str) and url.startswith('http'):
                    extracted_sources.append({
                        'title': self._extract_domain_name(url),
                        'url': url,
                        'snippet': '',
                        'author': '',
                        'date': '',
                        'type': 'web',
                        'citation_index': i + 1  # Store index for matching with [1], [2], etc.
                    })
        
        # Fallback to old sources field if present
        elif 'sources' in response:
            for source in response['sources']:
                if isinstance(source, dict):
                    extracted_sources.append({
                        'title': source.get('title', 'Unknown Source'),
                        'url': source.get('url', ''),
                        'snippet': source.get('snippet', ''),
                        'author': source.get('author', ''),
                        'date': source.get('date', ''),
                        'type': 'web'
                    })
                elif isinstance(source, str):
                    # Try to parse string sources
                    extracted_sources.append(self._parse_string_source(source))
        
        # Extract from content
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '') if 'choices' in response else ''
        
        # Extract URLs from content with enhanced pattern matching
        url_patterns = [
            r'https?://[^\s\])\n]+',  # Standard URLs
            r'Source:\s*(https?://[^\s\])\n]+)',  # "Source: URL" format
            r'(?:from|via|at):\s*(https?://[^\s\])\n]+)',  # "from: URL" format
        ]
        
        for pattern in url_patterns:
            urls = re.findall(pattern, content, re.IGNORECASE)
            for url in urls:
                if isinstance(url, tuple):
                    url = url[0]  # Extract from capture group
                if not any(s['url'] == url for s in extracted_sources):
                    extracted_sources.append({
                        'title': self._extract_domain_name(url),
                        'url': url,
                        'snippet': self._extract_url_context(content, url),
                        'author': '',
                        'date': '',
                        'type': 'web'
                    })
        
        # Extract organization names that might be sources
        org_patterns = [
            r'(?:according to|per|from|by)\s+([A-Z][a-zA-Z\s&]+(?:Research|Institute|University|Company|Corporation|Inc|LLC))',
            r'([A-Z][a-zA-Z\s&]+(?:Research|Institute|University))\s+(?:reports?|study|survey|data|analysis)',
            r'([A-Z][a-zA-Z\s&]+Research)\s+(?:\(\d{4}\))?',  # "Market Research Future (2024)" pattern
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                org_name = match.strip()
                if len(org_name) > 3 and not any(org_name.lower() in s.get('title', '').lower() for s in extracted_sources):
                    extracted_sources.append({
                        'title': org_name,
                        'url': '',
                        'snippet': self._extract_organization_context(content, org_name),
                        'author': '',
                        'date': self._extract_year_from_context(content, org_name),
                        'type': 'research_organization'
                    })
        
        # Extract academic citations (Author, Year) format
        academic_pattern = r'\(([A-Z][a-z]+(?:\s+(?:et\s+al\.|&\s+[A-Z][a-z]+))?),\s*(\d{4})\)'
        academic_citations = re.findall(academic_pattern, content)
        for author, year in academic_citations:
            extracted_sources.append({
                'title': f"{author} ({year})",
                'url': '',
                'snippet': '',
                'author': author,
                'date': year,
                'type': 'academic'
            })
        
        # Extract numbered references [1], [2], etc.
        numbered_pattern = r'\[(\d+)\]\s*([^[\n]+)'
        numbered_refs = re.findall(numbered_pattern, content)
        for num, text in numbered_refs:
            # Try to extract title or description
            extracted_sources.append({
                'title': text.strip()[:100],
                'url': '',
                'snippet': text.strip(),
                'author': '',
                'date': '',
                'type': 'reference',
                'ref_number': num
            })
        
        # Deduplicate sources
        unique_sources = []
        seen = set()
        for source in extracted_sources:
            identifier = source.get('url') or source.get('title')
            if identifier and identifier not in seen:
                unique_sources.append(source)
                seen.add(identifier)
        
        return unique_sources
    
    def _parse_string_source(self, source_str: str) -> Dict[str, Any]:
        """Parse a string source into structured format"""
        source_dict = {
            'title': '',
            'url': '',
            'snippet': '',
            'author': '',
            'date': '',
            'type': 'unknown'
        }
        
        # Check if it's a URL
        if source_str.startswith('http'):
            source_dict['url'] = source_str
            source_dict['title'] = self._extract_domain_name(source_str)
            source_dict['type'] = 'web'
        else:
            # Assume it's a title or description
            source_dict['title'] = source_str
            source_dict['type'] = 'reference'
        
        return source_dict
    
    def _extract_domain_name(self, url: str) -> str:
        """Extract a readable domain name from URL"""
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Make it more readable
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            return domain_parts[0].capitalize()
        return domain
    
    def _extract_url_context(self, content: str, url: str) -> str:
        """Extract context around a URL mention"""
        lines = content.split('\n')
        for line in lines:
            if url in line:
                # Return the line containing the URL, cleaned up
                return line.strip().replace(url, '').strip('- []()').strip()[:200]
        return ''
    
    def _extract_organization_context(self, content: str, org_name: str) -> str:
        """Extract context around an organization mention"""
        lines = content.split('\n')
        for line in lines:
            if org_name.lower() in line.lower():
                # Return the line containing the organization
                return line.strip('- []()').strip()[:200]
        return ''
    
    def _extract_year_from_context(self, content: str, org_name: str) -> str:
        """Extract year from context around organization mention"""
        lines = content.split('\n')
        for line in lines:
            if org_name.lower() in line.lower():
                # Look for year patterns in the line
                year_match = re.search(r'\b(20[12]\d)\b', line)
                if year_match:
                    return year_match.group(1)
        return ''
    
    def format_inline_citation(self, fact: str, source: Dict[str, Any], section: str = "general") -> str:
        """
        Format a fact with proper inline citation using Svalbardi method
        
        Prioritizes credible sources: academic papers, research institutions,
        government data, expert opinions. Avoids generic company blogs.
        
        Args:
            fact: The fact or statement to cite
            source: Source dictionary
            
        Returns:
            Formatted string with proper citation or fact alone if source not credible
        """
        # First check if this fact even needs a citation (with section context)
        if not self.needs_citation(fact, section):
            return f"{fact}." if not fact.endswith('.') else fact
        
        # Check for fact duplication FIRST
        if self.citation_tracker.check_fact_duplication(fact):
            return f"{fact}." if not fact.endswith('.') else fact
        
        # Double-check with citation tracker (redundant but ensures consistency)
        if not self.citation_tracker.should_cite(fact, section):
            return f"{fact}." if not fact.endswith('.') else fact
        
        # STRICT SOURCE VALIDATION - Only cite if we have a verified source
        if not source or not isinstance(source, dict):
            return f"{fact}." if not fact.endswith('.') else fact
        
        # Reject sources without proper attribution
        source_url = source.get('url', '')
        source_title = source.get('title', '')
        if not source_url and not source_title:
            return f"{fact}." if not fact.endswith('.') else fact
        # Extract all available source information
        author = source.get('author', '')
        organization = source.get('organization', '')
        date = source.get('date', '')
        title = source.get('title', '')
        url = source.get('url', '')
        
        # Assess source credibility
        credibility_indicators = {
            'academic': any(term in str(source).lower() for term in 
                           ['university', 'professor', 'dr.', 'phd', 'academic', 
                            'journal', 'scholar', 'institute', '.edu']),
            'research': any(term in str(source).lower() for term in 
                           ['research', 'study', 'survey', 'report', 'analysis', 
                            'findings', 'data', 'statistics']),
            'government': any(term in str(source).lower() for term in 
                            ['.gov', 'government', 'federal', 'national', 
                             'bureau', 'department', 'agency']),
            'expert': any(term in str(source).lower() for term in 
                         ['expert', 'specialist', 'analyst', 'consultant']),
            'industry': any(term in str(source).lower() for term in 
                          ['gartner', 'forrester', 'idc', 'mckinsey', 'deloitte', 
                           'accenture', 'pwc', 'kpmg', 'ey', 'bain']),
            'market_research': any(term in str(source).lower() for term in
                                  ['market research', 'market size', 'market forecast', 
                                   'industry report', 'market analysis', 'cagr', 
                                   'projected', 'forecast', 'trillion', 'billion']),
            'major_vendor': any(term in str(source).lower() for term in
                              ['aws.amazon', 'cloud.google', 'azure.microsoft', 'ibm.com',
                               'oracle.com', 'vmware.com', 'redhat.com'])
        }
        
        # Check if it's a low-quality source (company blog, tech media, etc.)
        low_quality_indicators = [
            'blog', 'marketing', 'promo', 'sale', 'product page',
            'learn more', 'get started', 'sign up',
            'techtarget', 'techrepublic', 'zdnet', 'cnet', 'venturebeat',
            'techcrunch', 'theverge', 'engadget', 'arstechnica', 'wired',
            'informationweek', 'computerworld', 'infoworld', 'pcmag', 'pcworld'
        ]
        is_low_quality = any(term in str(source).lower() for term in low_quality_indicators)
        
        # Don't cite if source is low quality OR if it's just a tech media site
        # Even if it has "research" in it, tech media sites shouldn't be cited
        if is_low_quality:
            # Return fact without weak citation
            return f"{fact}."
        
        # Also require at least one strong credibility indicator
        if not any([credibility_indicators['academic'], 
                    credibility_indicators['government'],
                    credibility_indicators['industry'],
                    credibility_indicators['market_research'],
                    credibility_indicators['major_vendor']]):
            # Not credible enough to cite
            return f"{fact}."
        
        # Try to extract better information from title/URL if needed
        if not author and title:
            # Look for credible author patterns
            author_patterns = [
                r'(?:Dr\.|Professor|Prof\.) ([A-Z][a-z]+ [A-Z][a-z]+)',
                r'([A-Z][a-z]+ [A-Z][a-z]+), (?:PhD|MD|M\.D\.|researcher)',
                r'by ([A-Z][a-z]+ [A-Z][a-z]+) (?:at|from)',
            ]
            for pattern in author_patterns:
                match = re.search(pattern, title)
                if match:
                    author = match.group(1)
                    break
        
        if not organization and url:
            # Extract credible organizations from URL
            if '.edu' in url:
                # Extract university name
                match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)\.edu', url)
                if match:
                    org_name = match.group(1).replace('-', ' ').title()
                    organization = f"{org_name} University"
            elif '.gov' in url:
                match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)\.gov', url)
                if match:
                    organization = match.group(1).upper()
        
        # Build citation using Svalbardi patterns
        citation = ""
        
        # Pattern 1: Academic with author and institution
        if author and organization and credibility_indicators['academic']:
            if any(title in author for title in ['Dr.', 'Professor', 'Prof.']):
                citation = f"according to {author} at {organization}"
            else:
                citation = f"according to {author} of {organization}"
            if date:
                citation += f" ({date})"
        
        # Pattern 2: Research by institution
        elif organization and credibility_indicators['research']:
            if date:
                citation = f"according to {organization}'s {date} research"
            else:
                citation = f"according to research by {organization}"
        
        # Pattern 3: Government source
        elif credibility_indicators['government']:
            if organization:
                citation = f"according to {organization}"
            elif author:
                citation = f"according to {author}"
            if date and citation:
                citation += f" ({date})"
        
        # Pattern 4: Industry research
        elif credibility_indicators['industry'] and organization:
            if date:
                citation = f"according to {organization} ({date})"
            else:
                citation = f"according to {organization}"
        
        # Pattern 4a: Market research (new pattern for market projections)
        elif credibility_indicators['market_research'] and organization:
            if date:
                citation = f"according to {organization} ({date})"
            else:
                citation = f"according to {organization}"
        
        # Pattern 5: Expert opinion
        elif author and credibility_indicators['expert']:
            citation = f"according to {author}"
            if organization:
                citation += f" of {organization}"
            if date:
                citation += f" ({date})"
        
        # If no credible citation can be formed, return fact alone
        if not citation:
            return f"{fact}."
        
        # Clean up fact ending
        if fact.endswith('.'):
            fact = fact[:-1]
        
        # Record that we're adding this citation
        self.citation_tracker.record_citation(fact, section)
        
        # Record fact usage to prevent repetition
        source_id = source_url or source_title or 'unknown'
        self.citation_tracker.record_fact_usage(fact, section, source_id)
        
        # Format with citation
        return f"{fact}, {citation}."
    
    def format_statistic_with_source(self, statistic: str, source: Dict[str, Any], section: str = "general") -> str:
        """
        Format a statistic with proper source attribution using Svalbardi method
        
        Example: "60% in adult men, according to Dr. Jeffrey Utz of Allegheny University (2023)"
        """
        # Check for fact duplication FIRST
        if self.citation_tracker.check_fact_duplication(statistic):
            return f"{statistic}." if not statistic.endswith('.') else statistic
        
        # Check with citation tracker 
        if not self.citation_tracker.should_cite(statistic, section):
            return f"{statistic}." if not statistic.endswith('.') else statistic
        
        # STRICT SOURCE VALIDATION - Must have verified source
        if not source or not isinstance(source, dict):
            return f"{statistic}." if not statistic.endswith('.') else statistic
        
        # Statistics usually need citations, but check if it's a truly significant stat
        # Skip citation for trivial or obvious statistics
        trivial_patterns = [
            r'100%\s+of',  # Obviously true statements
            r'0%\s+of',     # Obviously false statements
            r'all\s+\d+',   # "All 3 types" doesn't need citation
            r'both\s+',     # "Both options" doesn't need citation
        ]
        
        for pattern in trivial_patterns:
            if re.search(pattern, statistic.lower()):
                return f"{statistic}." if not statistic.endswith('.') else statistic
        # Extract specific attribution details
        author = source.get('author', '')
        organization = source.get('organization', '')
        date = source.get('date', '')
        title = source.get('title', '')
        url = source.get('url', '')
        
        # Try to extract from title if not explicitly provided
        if not author and source.get('title'):
            # Look for patterns like "Dr. X" or "Professor Y"
            title_patterns = [
                r'(?:Dr\.|Professor|Prof\.) ([A-Z][a-z]+ [A-Z][a-z]+)',
                r'([A-Z][a-z]+ [A-Z][a-z]+), (?:PhD|MD|researcher)',
            ]
            for pattern in title_patterns:
                match = re.search(pattern, source['title'])
                if match:
                    author = match.group(1)
                    break
        
        # Extract organization from URL or title
        if not organization:
            if source.get('url'):
                # Extract from domain
                domain = self._extract_domain_name(source['url'])
                if 'university' in source['url'].lower() or 'edu' in source['url']:
                    organization = f"{domain} University"
                elif 'institute' in source['url'].lower():
                    organization = f"{domain} Institute"
                else:
                    organization = domain
        
        # Assess source credibility (same as in format_inline_citation)
        is_academic = any(term in str(source).lower() for term in 
                          ['university', 'professor', 'dr.', 'phd', 'academic', 
                           'journal', 'scholar', 'institute', '.edu'])
        is_government = any(term in str(source).lower() for term in 
                           ['.gov', 'government', 'federal', 'national', 
                            'bureau', 'department', 'agency'])
        is_research = any(term in str(source).lower() for term in 
                         ['research', 'study', 'survey', 'report', 'analysis',
                          'gartner', 'forrester', 'idc', 'mckinsey', 'deloitte'])
        is_market_research = any(term in str(source).lower() for term in
                                ['market research', 'market size', 'market forecast', 
                                 'industry report', 'market analysis', 'cagr', 
                                 'projected', 'forecast', 'trillion', 'billion'])
        
        # Only cite statistics from credible sources
        if not (is_academic or is_government or is_research or is_market_research):
            # Return statistic without weak source
            return f"{statistic}."
        
        # Format the attribution using Svalbardi patterns
        attribution = ""
        
        if author and organization:
            if any(title in author for title in ['Dr.', 'Professor', 'Prof.']):
                attribution = f"according to {author} at {organization}"
            else:
                attribution = f"according to {author} of {organization}"
        elif organization and is_research:
            attribution = f"according to {organization}"
        elif author and is_academic:
            attribution = f"according to {author}"
        elif organization:
            attribution = f"according to {organization}"
        elif date and is_research:
            attribution = f"according to {date} research"
        
        # If no credible attribution, return statistic alone
        if not attribution:
            return f"{statistic}."
        
        # Add date if available
        if date and '(' not in attribution:
            attribution += f" ({date})"
        
        # Combine statistic with attribution
        if statistic.endswith('.'):
            statistic = statistic[:-1]
        
        # Record that we're adding this citation
        self.citation_tracker.record_citation(statistic, section)
        
        # Record fact usage to prevent repetition
        source_url = source.get('url', '')
        source_title = source.get('title', '')
        source_id = source_url or source_title or 'unknown'
        self.citation_tracker.record_fact_usage(statistic, section, source_id)
        
        return f"{statistic}, {attribution}."
    
    def generate_source_reference_section(self, sources: List[Dict[str, Any]]) -> str:
        """
        Generate a formatted source reference section for export
        
        Returns:
            Formatted HTML/Markdown source section
        """
        if not sources:
            return ""
        
        reference_lines = ["## Sources and References\n"]
        
        # Group sources by type - prioritize those with URLs
        web_sources = [s for s in sources if s.get('url')]
        academic_sources = [s for s in sources if s.get('type') == 'academic' and not s.get('url')]
        other_sources = [s for s in sources if not s.get('url') and s.get('type') != 'academic']
        
        if web_sources:
            reference_lines.append("### Web Sources\n")
            for i, source in enumerate(web_sources, 1):
                title = source.get('title', 'Unknown Source')
                url = source.get('url', '')
                date = source.get('date', '')
                
                # Always show URL if available
                if url:
                    # Make title more descriptive if it's just a domain name
                    if '.' in title and len(title.split()) == 1:
                        # It's likely just a domain, make it more descriptive
                        title = f"Source from {title}"
                    reference_lines.append(f"{i}. [{title}]({url})")
                else:
                    reference_lines.append(f"{i}. {title}")
                
                if date and date not in title:
                    reference_lines[-1] += f" ({date})"
                reference_lines[-1] += "\n"
        
        if academic_sources:
            reference_lines.append("\n### Academic References\n")
            for source in academic_sources:
                author = source.get('author', 'Unknown')
                date = source.get('date', '')
                title = source.get('title', '')
                
                reference_lines.append(f"- {author} ({date}). {title}\n")
        
        if other_sources:
            reference_lines.append("\n### Additional References\n")
            for source in other_sources:
                title = source.get('title', 'Unknown Source')
                reference_lines.append(f"- {title}\n")
        
        return ''.join(reference_lines)
    
    def store_sources(self, sources: List[Dict[str, Any]], filepath: Optional[str] = None):
        """Store sources to a JSON file for later reference"""
        if filepath is None:
            filepath = f"data/sources/sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Store sources with metadata
        source_data = {
            'timestamp': datetime.now().isoformat(),
            'total_sources': len(sources),
            'sources': sources
        }
        
        with open(filepath, 'w') as f:
            json.dump(source_data, f, indent=2)
        
        return filepath
    
    def load_sources(self, filepath: str) -> List[Dict[str, Any]]:
        """Load sources from a JSON file"""
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get('sources', [])
        return []