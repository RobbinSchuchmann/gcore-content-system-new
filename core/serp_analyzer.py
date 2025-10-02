"""
SERP Analyzer Module
Fetches Google search results and analyzes competitor content for heading structure optimization
"""

import requests
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import concurrent.futures
from urllib.parse import urlparse
import anthropic
from config import ANTHROPIC_API_KEY, PERPLEXITY_API_KEY, PERPLEXITY_API_URL, CLAUDE_MODEL
from core.content_scraper import ContentScraper


class SERPAnalyzer:
    """Analyze Google SERP results and extract competitor heading structures"""

    def __init__(self, perplexity_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.perplexity_api_key = perplexity_api_key or PERPLEXITY_API_KEY
        self.anthropic_api_key = anthropic_api_key or ANTHROPIC_API_KEY
        self.perplexity_url = PERPLEXITY_API_URL
        self.scraper = ContentScraper()
        self.client = anthropic.Anthropic(api_key=self.anthropic_api_key) if self.anthropic_api_key else None
        self.model = CLAUDE_MODEL

    def fetch_serp_results(self, keyword: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Fetch top Google search results for a keyword using Perplexity API

        Args:
            keyword: Primary keyword to search for
            num_results: Number of results to fetch (default 10)

        Returns:
            Dictionary with SERP results and metadata
        """
        if not self.perplexity_api_key:
            return {
                'success': False,
                'error': 'Perplexity API key not configured',
                'results': []
            }

        try:
            # Build query to get SERP results
            query = f"What are the top {num_results} Google search results for '{keyword}'? Provide the exact URLs and page titles in a structured format. Focus on authoritative sources and competitors in the CDN, cloud computing, and edge computing space."

            # Make Perplexity API request
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a search engine result parser. Return ONLY a JSON array of objects with 'title' and 'url' fields. No additional text."
                    },
                    {
                        "role": "user",
                        "content": f"Find the top {num_results} Google search results for: {keyword}\n\nReturn as JSON array: [{{'title': 'Page Title', 'url': 'https://...'}}]"
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2000,
                "return_citations": True,
                "search_recency_filter": "month"  # Focus on recent results
            }

            response = requests.post(
                self.perplexity_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Perplexity API error: {response.status_code}',
                    'results': []
                }

            response_data = response.json()

            # Extract results from response
            results = self._parse_serp_response(response_data, num_results)

            return {
                'success': True,
                'keyword': keyword,
                'results': results,
                'timestamp': datetime.now().isoformat(),
                'total_results': len(results)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to fetch SERP results: {str(e)}',
                'results': []
            }

    def _parse_serp_response(self, response_data: Dict[str, Any], num_results: int) -> List[Dict[str, str]]:
        """Parse Perplexity API response to extract URLs and titles"""
        results = []

        try:
            # Get content from response
            content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

            # Try to parse as JSON
            try:
                parsed_data = json.loads(content)
                if isinstance(parsed_data, list):
                    results = parsed_data[:num_results]
            except json.JSONDecodeError:
                # Fallback: extract from citations
                citations = response_data.get('citations', [])
                for i, citation in enumerate(citations[:num_results]):
                    if isinstance(citation, str):
                        results.append({
                            'title': f'Result {i+1}',
                            'url': citation,
                            'rank': i + 1
                        })

            # Add ranking if not present
            for i, result in enumerate(results):
                if 'rank' not in result:
                    result['rank'] = i + 1
                # Extract domain for display
                if 'url' in result:
                    result['domain'] = urlparse(result['url']).netloc

            return results

        except Exception as e:
            print(f"Error parsing SERP response: {e}")
            return []

    def extract_competitor_headings(self, urls: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """
        Extract heading structures from multiple competitor URLs concurrently

        Args:
            urls: List of competitor URLs to analyze
            max_workers: Maximum concurrent requests

        Returns:
            Dictionary with heading data for each URL
        """
        results = {
            'success': True,
            'competitors': {},
            'failed_urls': [],
            'timestamp': datetime.now().isoformat()
        }

        def scrape_single_url(url: str) -> Tuple[str, Dict]:
            """Helper function to scrape a single URL"""
            try:
                data = self.scraper.fetch_from_url(url)
                if data['success']:
                    return url, {
                        'title': data['title'],
                        'headings': data['headings'],
                        'success': True
                    }
                else:
                    return url, {
                        'error': data.get('error', 'Unknown error'),
                        'success': False
                    }
            except Exception as e:
                return url, {
                    'error': str(e),
                    'success': False
                }

        # Use ThreadPoolExecutor for concurrent scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(scrape_single_url, url): url for url in urls}

            for future in concurrent.futures.as_completed(future_to_url):
                url, data = future.result()

                if data['success']:
                    results['competitors'][url] = data
                else:
                    results['failed_urls'].append({
                        'url': url,
                        'error': data.get('error', 'Unknown error')
                    })

        return results

    def analyze_heading_patterns(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze heading patterns across competitors to identify common structures and gaps

        Args:
            competitor_data: Dictionary with heading data from competitors

        Returns:
            Analysis results with patterns, gaps, and insights
        """
        analysis = {
            'total_competitors': len(competitor_data.get('competitors', {})),
            'common_h2_topics': [],
            'common_h3_topics': [],
            'unique_topics': [],
            'faq_sections': [],
            'average_h2_count': 0,
            'average_h3_count': 0,
            'heading_hierarchy': []
        }

        if not competitor_data.get('competitors'):
            return analysis

        # Collect all headings
        all_h2 = []
        all_h3 = []
        total_h2_count = 0
        total_h3_count = 0

        for url, data in competitor_data['competitors'].items():
            headings = data.get('headings', [])

            h2_for_url = []
            h3_for_url = []

            for heading in headings:
                level = heading.get('level', '').upper()
                text = heading.get('text', '').lower()

                if level == 'H2':
                    all_h2.append(text)
                    h2_for_url.append(text)
                    total_h2_count += 1

                    # Check for FAQ sections
                    if any(faq_term in text for faq_term in ['faq', 'frequently asked', 'common questions']):
                        analysis['faq_sections'].append(url)

                elif level == 'H3':
                    all_h3.append(text)
                    h3_for_url.append(text)
                    total_h3_count += 1

        # Find common topics (appearing in 2+ competitors)
        from collections import Counter

        h2_counts = Counter(all_h2)
        h3_counts = Counter(all_h3)

        analysis['common_h2_topics'] = [
            {'topic': topic, 'frequency': count}
            for topic, count in h2_counts.most_common(10)
            if count >= 2
        ]

        analysis['common_h3_topics'] = [
            {'topic': topic, 'frequency': count}
            for topic, count in h3_counts.most_common(15)
            if count >= 2
        ]

        # Calculate averages
        num_competitors = len(competitor_data['competitors'])
        analysis['average_h2_count'] = round(total_h2_count / num_competitors, 1) if num_competitors > 0 else 0
        analysis['average_h3_count'] = round(total_h3_count / num_competitors, 1) if num_competitors > 0 else 0

        return analysis

    def suggest_heading_structure(self,
                                  keyword: str,
                                  competitor_headings: Dict[str, Any],
                                  analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude AI to suggest optimal heading structure based on competitor analysis

        Args:
            keyword: Primary keyword
            competitor_headings: Extracted competitor heading data
            analysis: Analyzed patterns and insights

        Returns:
            AI-generated heading suggestions with explanations
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Anthropic API key not configured'
            }

        try:
            # Build prompt for Claude
            prompt = self._build_heading_suggestion_prompt(keyword, competitor_headings, analysis)

            # Call Claude API
            message = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse response
            response_text = message.content[0].text

            # Try to extract structured data from response
            suggestions = self._parse_ai_suggestions(response_text)

            return {
                'success': True,
                'suggestions': suggestions,
                'raw_response': response_text,
                'keyword': keyword,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate suggestions: {str(e)}'
            }

    def _build_heading_suggestion_prompt(self,
                                        keyword: str,
                                        competitor_headings: Dict[str, Any],
                                        analysis: Dict[str, Any]) -> str:
        """Build comprehensive prompt for Claude to suggest heading structure"""

        # Extract competitor heading structures
        competitor_structures = []
        for url, data in competitor_headings.get('competitors', {}).items():
            domain = urlparse(url).netloc
            headings = data.get('headings', [])
            competitor_structures.append(f"\n**{domain}**:")
            for h in headings[:15]:  # Limit to first 15 headings per competitor
                level = h.get('level', '')
                text = h.get('text', '')
                indent = "  " if level == "H3" else ""
                competitor_structures.append(f"{indent}- {level}: {text}")

        competitor_text = "\n".join(competitor_structures)

        # Build analysis summary
        common_h2 = "\n".join([f"- {t['topic']} (appears {t['frequency']}x)"
                               for t in analysis.get('common_h2_topics', [])[:8]])

        prompt = f"""You are an expert SEO content strategist for Gcore. Analyze the following competitor heading structures and suggest an optimal heading structure for a new article targeting the keyword: "{keyword}".

**COMPETITOR HEADING STRUCTURES:**
{competitor_text}

**ANALYSIS INSIGHTS:**
- Average H2 count across competitors: {analysis.get('average_h2_count', 0)}
- Average H3 count across competitors: {analysis.get('average_h3_count', 0)}
- Competitors with FAQ sections: {len(analysis.get('faq_sections', []))}

**COMMON H2 TOPICS:**
{common_h2}

**GCORE HEADING STYLE REQUIREMENTS:**
All headings MUST follow these formats:

**H2 Headings** - Use question format:
- "What is [topic]?"
- "How does [topic] work?"
- "What are the [plural noun]?" (e.g., "What are the main challenges?")
- "How to [verb phrase]?" (e.g., "How to implement best practices?")
- Exception: "Frequently asked questions" (for FAQ section)

**H3 Headings** - Use question format:
- Under FAQ H2: Always questions (e.g., "What's the difference between X and Y?")
- Under regular H2: Can be questions or specific topics

**YOUR TASK:**
Create a comprehensive heading structure that:
1. Covers all essential topics from competitors
2. Converts all H2 headings to question format
3. Identifies and fills content gaps
4. Includes a FAQ section with 5-7 question-format H3s
5. Uses natural, user-focused language

**OUTPUT FORMAT:**
Provide your suggestions in this exact format:

# Suggested H1:
[Topic-focused title without question]

## H2 Headings:

### H2: What is [keyword]?
**Why:** Foundational definition section
**H3 subheadings:**
- [Optional H3 if needed]

### H2: How does [keyword] work?
**Why:** Explains the mechanism/process
**H3 subheadings:**
- [Optional H3 if needed]

### H2: What are the main [keyword] [challenges/benefits/features]?
**Why:** Lists key points
**H3 subheadings:**
- [Optional H3 if needed]

### H2: How to [implement/use] [keyword] best practices?
**Why:** Actionable guidance
**H3 subheadings:**
- [Optional H3 if needed]

## FAQ Section:

### H2: Frequently asked questions
**H3 Questions:**
- What's the difference between [X] and [Y]?
- How much does [keyword] cost?
- Is [keyword] secure?
- What are the requirements for [keyword]?
- How does [concept] apply to [keyword]?

## Strategic Insights:
[2-3 sentences explaining your overall strategy and why this structure will outperform competitors]

**CRITICAL RULES:**
- ALL H2 headings (except "Frequently asked questions") MUST be questions
- Use "What", "How", "Why", "When", "Where" to start H2s
- Use sentence case (capitalize first word + proper nouns only)
- Focus on user search intent
- Make questions natural and conversational
- DO NOT include formatting markers like "H3:", "###", or markdown headers in the actual heading text
- Strategic Insights should be plain text, no headers or special formatting"""

        return prompt

    def _parse_ai_suggestions(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response into structured heading suggestions"""
        import re

        suggestions = {
            'h1': '',
            'h2_sections': [],
            'faq_section': {
                'h2': '',
                'questions': []
            },
            'strategic_insights': ''
        }

        # Extract H1
        h1_match = re.search(r'# Suggested H1:\s*\n(.+)', response_text)
        if h1_match:
            suggestions['h1'] = h1_match.group(1).strip()

        # Extract H2 sections with H3s and explanations
        h2_sections = re.findall(
            r'### H2: (.+?)\n\*\*Why:\*\* (.+?)(?:\n\*\*H3 subheadings:\*\*\n((?:- .+\n?)+))?',
            response_text,
            re.MULTILINE | re.DOTALL
        )

        for h2_text, why, h3_text in h2_sections:
            h3_items = []
            if h3_text:
                h3_items = [h3.strip('- ').strip() for h3 in h3_text.strip().split('\n') if h3.strip()]

            suggestions['h2_sections'].append({
                'h2': h2_text.strip(),
                'why': why.strip(),
                'h3_subheadings': h3_items
            })

        # Extract FAQ section
        faq_section = re.search(
            r'## FAQ Section:\s*\n### H2: (.+?)\n\*\*H3 Questions:\*\*\n((?:- .+\n?)+)',
            response_text,
            re.MULTILINE | re.DOTALL
        )

        if faq_section:
            suggestions['faq_section']['h2'] = faq_section.group(1).strip()
            faq_questions = [q.strip('- ').strip() for q in faq_section.group(2).strip().split('\n') if q.strip()]
            suggestions['faq_section']['questions'] = faq_questions

        # Extract strategic insights
        insights_match = re.search(
            r'## Strategic Insights:\s*\n(.+?)(?:\n\n|\Z)',
            response_text,
            re.MULTILINE | re.DOTALL
        )

        if insights_match:
            suggestions['strategic_insights'] = insights_match.group(1).strip()

        return suggestions

    def run_full_analysis(self, keyword: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Run complete SERP analysis workflow: fetch results, extract headings, analyze, and suggest

        Args:
            keyword: Primary keyword to analyze
            num_results: Number of SERP results to fetch

        Returns:
            Complete analysis with all results
        """
        result = {
            'keyword': keyword,
            'timestamp': datetime.now().isoformat(),
            'serp_results': {},
            'competitor_headings': {},
            'analysis': {},
            'suggestions': {},
            'errors': []
        }

        # Step 1: Fetch SERP results
        serp_data = self.fetch_serp_results(keyword, num_results)
        result['serp_results'] = serp_data

        if not serp_data['success']:
            result['errors'].append(f"SERP fetch failed: {serp_data.get('error')}")
            return result

        # Step 2: Extract competitor headings
        urls = [r['url'] for r in serp_data['results'] if 'url' in r]
        heading_data = self.extract_competitor_headings(urls)
        result['competitor_headings'] = heading_data

        if heading_data['failed_urls']:
            result['errors'].append(f"Failed to scrape {len(heading_data['failed_urls'])} URLs")

        # Step 3: Analyze patterns
        analysis = self.analyze_heading_patterns(heading_data)
        result['analysis'] = analysis

        # Step 4: Get AI suggestions
        suggestions = self.suggest_heading_structure(keyword, heading_data, analysis)
        result['suggestions'] = suggestions

        if not suggestions['success']:
            result['errors'].append(f"AI suggestions failed: {suggestions.get('error')}")

        return result

    def analyze_for_optimization(self, existing_url: str, competitor_urls: List[str], keyword: str = "") -> Dict[str, Any]:
        """
        Analyze existing article against competitors for optimization recommendations

        Args:
            existing_url: URL of the article to optimize
            competitor_urls: List of competitor URLs to analyze against
            keyword: Primary keyword (optional, for context)

        Returns:
            Dictionary with:
            - existing_structure: Current article structure
            - competitor_structures: Competitor heading structures
            - recommendations: AI-powered Keep/Improve/Add/Remove suggestions
            - optimal_structure: Suggested heading order
            - strategic_insights: Explanation of recommendations
        """
        result = {
            'success': False,
            'existing_structure': {},
            'competitor_structures': {},
            'recommendations': [],
            'optimal_structure': [],
            'strategic_insights': '',
            'errors': []
        }

        try:
            # Step 1: Extract existing article structure
            print(f"Fetching existing article from {existing_url}...")
            all_urls = [existing_url] + competitor_urls
            heading_response = self.extract_competitor_headings(all_urls)

            # Extract competitors dict from response
            heading_data = heading_response.get('competitors', {})

            if existing_url not in heading_data or not heading_data[existing_url]['success']:
                result['errors'].append(f"Failed to fetch existing article: {existing_url}")
                if heading_response.get('failed_urls'):
                    for failed in heading_response['failed_urls']:
                        if failed['url'] == existing_url:
                            result['errors'].append(f"Error: {failed.get('error', 'Unknown')}")
                return result

            result['existing_structure'] = heading_data[existing_url]

            # Step 2: Get competitor structures (exclude existing article)
            result['competitor_structures'] = {
                url: data for url, data in heading_data.items()
                if url != existing_url and data['success']
            }

            if len(result['competitor_structures']) < 2:
                result['errors'].append("Need at least 2 successful competitor fetches")
                return result

            # Step 3: Build comparison for AI
            existing_headings = result['existing_structure']['headings']
            competitor_headings_list = [data['headings'] for data in result['competitor_structures'].values()]

            # Step 4: Get AI recommendations
            recommendations = self._suggest_optimization_actions(
                existing_headings,
                competitor_headings_list,
                keyword
            )

            if recommendations['success']:
                result['success'] = True
                result['recommendations'] = recommendations['recommendations']
                result['optimal_structure'] = recommendations['optimal_structure']
                result['strategic_insights'] = recommendations['strategic_insights']
            else:
                result['errors'].append(f"AI analysis failed: {recommendations.get('error')}")

        except Exception as e:
            result['errors'].append(f"Analysis error: {str(e)}")

        return result

    def _suggest_optimization_actions(self, existing_headings: List[Dict], competitor_headings_list: List[List[Dict]], keyword: str) -> Dict[str, Any]:
        """
        Use Claude AI to suggest optimization actions for each section

        Returns recommendations with actions: keep, improve, add, remove
        """
        result = {
            'success': False,
            'recommendations': [],
            'optimal_structure': [],
            'strategic_insights': '',
            'error': None
        }

        try:
            # Format existing structure
            existing_structure_text = "## Current Article Structure:\n\n"
            for heading in existing_headings:
                existing_structure_text += f"- {heading['level']}: {heading['text']}\n"

            # Format competitor structures
            competitor_text = "## Competitor Structures:\n\n"
            for i, comp_headings in enumerate(competitor_headings_list, 1):
                competitor_text += f"### Competitor {i}:\n"
                for heading in comp_headings:
                    competitor_text += f"- {heading['level']}: {heading['text']}\n"
                competitor_text += "\n"

            # Build AI prompt
            prompt = f"""You are an expert SEO content strategist analyzing an existing article for optimization.

**Primary Keyword:** {keyword if keyword else "Not specified"}

{existing_structure_text}

{competitor_text}

**Your Task:**
Analyze the current article structure against competitors and provide optimization recommendations.

For each existing section, decide:
- **KEEP**: Section is competitive and should be preserved exactly as-is
- **IMPROVE**: Section exists but needs enhancement (better examples, more depth, clearer structure)
- **REMOVE**: Section is redundant, low-value, or off-topic

Also identify:
- **ADD**: Missing sections that competitors cover and we should add

**IMPORTANT RULES:**
1. Be balanced - preserve unique valuable content
2. **KEEP** means keeping the heading AND content as-is - don't suggest KEEP if you want to change the heading
3. **IMPROVE** means enhancing existing content - keep the same topic but make it better
4. **DO NOT suggest transforming or restructuring headings** - if a heading needs a different title, use IMPROVE and explain the better title in the reason
5. All NEW headings (ADD) should be in question format (What is...? How does...? etc.)
6. **CRITICAL: NEVER recommend the same heading for both REMOVE and ADD** - If you want to completely rewrite a section, use IMPROVE instead
7. **H3 Subheadings**: Only suggest H3s for complex technical sections. For lists (benefits, challenges, features), do NOT suggest H3s.

**Output Format:**

# Strategic Insights:
[2-3 sentences explaining the overall optimization strategy and why these changes will improve SEO]

## Recommendations:

### KEEP (Preserve as-is):
- H2: [heading text] | Reason: [why this is valuable and should be kept]

### IMPROVE (Enhance content):
- H2: [heading text] | Reason: [what's weak and how to improve]

### REMOVE (Delete section):
- H2: [heading text] | Reason: [why this should be removed]

### ADD (New sections needed):
- H2: [new heading text] | Reason: [what gap this fills]
  - H3: [subheading] (ONLY if genuinely needed for complex content - skip for listicles)

## Optimal Structure:
[List all headings in recommended order, including existing KEEP/IMPROVE sections and new ADD sections]
1. H2: [heading text] - [KEEP/IMPROVE/ADD]
2. H2: [heading text] - [KEEP/IMPROVE/ADD]
...
"""

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                system="You are an expert SEO content strategist specializing in content optimization and competitive analysis.",
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = response.content[0].text

            # DEBUG: Save response to file for inspection
            import os
            from datetime import datetime
            debug_dir = 'debug_responses'
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_file = f'{debug_dir}/optimization_response_{timestamp}.txt'
            with open(debug_file, 'w') as f:
                f.write(response_text)
            print(f"DEBUG: Saved AI response to {debug_file}")

            # Parse AI response
            parsed = self._parse_optimization_recommendations(response_text)
            result.update(parsed)
            result['success'] = True

            # DEBUG: Print parsing results
            print(f"DEBUG: Parsed {len(parsed['recommendations'])} recommendations")
            for rec in parsed['recommendations']:
                print(f"  - {rec['action'].upper()}: {rec['heading']}")

        except Exception as e:
            result['error'] = str(e)

        return result

    def _to_sentence_case(self, text: str) -> str:
        """Convert heading to sentence case (only first letter capitalized)"""
        # Preserve question words and common acronyms
        preserve_words = ['CDN', 'API', 'DNS', 'SSL', 'HTTP', 'HTTPS', 'VPN', 'SLA', 'FAQ', 'SEO', 'AI', 'ML', 'GPU', 'CPU', 'RAM', 'SSD', 'HDD']

        words = text.split()
        result = []

        for i, word in enumerate(words):
            # Keep acronyms uppercase
            if word.upper() in preserve_words or word.isupper() and len(word) <= 4:
                result.append(word.upper())
            # Capitalize first word
            elif i == 0:
                result.append(word.capitalize())
            # Lowercase everything else
            else:
                result.append(word.lower())

        return ' '.join(result)

    def _parse_optimization_recommendations(self, response_text: str) -> Dict[str, Any]:
        """Parse AI optimization recommendations into structured format"""
        parsed = {
            'recommendations': [],
            'optimal_structure': [],
            'strategic_insights': ''
        }

        # Extract strategic insights
        insights_match = re.search(r'# Strategic Insights:\s*\n(.+?)(?=\n##|\Z)', response_text, re.DOTALL)
        if insights_match:
            parsed['strategic_insights'] = insights_match.group(1).strip()

        # Extract KEEP recommendations
        keep_match = re.search(r'### KEEP.*?:\s*\n((?:- \*?\*?H2:.+\n?)+)', response_text, re.DOTALL | re.IGNORECASE)
        keep_text = keep_match.group(1) if keep_match else ''
        keep_sections = re.findall(
            r'-\s*\*?\*?H2:\s*(.+?)\*?\*?\s*\|\s*Reason:\s*(.+?)(?=\n-|\n\n|\Z)',
            keep_text,
            re.DOTALL
        )
        for heading, reason in keep_sections:
            parsed['recommendations'].append({
                'action': 'keep',
                'heading': self._to_sentence_case(heading.strip()),
                'level': 'H2',
                'reason': reason.strip(),
                'h3_subheadings': []
            })

        # Extract IMPROVE recommendations
        improve_match = re.search(r'### IMPROVE.*?:\s*\n((?:- \*?\*?H2:.+\n?)+)', response_text, re.DOTALL | re.IGNORECASE)
        improve_text = improve_match.group(1) if improve_match else ''
        improve_sections = re.findall(
            r'-\s*\*?\*?H2:\s*(.+?)\*?\*?\s*\|\s*Reason:\s*(.+?)(?=\n-|\n\n|\Z)',
            improve_text,
            re.DOTALL
        )
        for heading, reason in improve_sections:
            parsed['recommendations'].append({
                'action': 'improve',
                'heading': self._to_sentence_case(heading.strip()),
                'level': 'H2',
                'reason': reason.strip(),
                'h3_subheadings': []
            })

        # Extract REMOVE recommendations
        remove_match = re.search(r'### REMOVE.*?:\s*\n((?:- \*?\*?H2:.+\n?)+)', response_text, re.DOTALL | re.IGNORECASE)
        remove_text = remove_match.group(1) if remove_match else ''
        remove_sections = re.findall(
            r'-\s*\*?\*?H2:\s*(.+?)\*?\*?\s*\|\s*Reason:\s*(.+?)(?=\n-|\n\n|\Z)',
            remove_text,
            re.DOTALL
        )
        for heading, reason in remove_sections:
            parsed['recommendations'].append({
                'action': 'remove',
                'heading': self._to_sentence_case(heading.strip()),
                'level': 'H2',
                'reason': reason.strip(),
                'h3_subheadings': []
            })

        # Extract ADD recommendations with H3s
        add_section = re.search(r'### ADD.*?:\s*\n((?:- \*?\*?H2:.+(?:\n\s+- H3:.+)*\n?)+)', response_text, re.DOTALL | re.IGNORECASE)
        if add_section:
            add_text = add_section.group(1)
            # Parse each ADD section
            add_items = re.findall(r'- \*?\*?H2:\s*(.+?)\*?\*?\s*\|\s*Reason:\s*(.+?)(?=\n-|\Z)', add_text, re.DOTALL)
            for heading, reason in add_items:
                # Find H3s for this H2
                h3_pattern = rf'{re.escape(heading.strip())}.*?Reason:.*?\n((?:\s+- H3:.+\n?)*)'
                h3_match = re.search(h3_pattern, add_text, re.DOTALL)
                h3_items = []
                if h3_match:
                    h3_text = h3_match.group(1)
                    h3_items = [h3.strip('- H3:').strip() for h3 in re.findall(r'- H3:\s*(.+)', h3_text)]

                parsed['recommendations'].append({
                    'action': 'add',
                    'heading': self._to_sentence_case(heading.strip()),
                    'level': 'H2',
                    'reason': reason.strip(),
                    'h3_subheadings': [self._to_sentence_case(h3) for h3 in h3_items]
                })

        # Extract optimal structure order
        structure_match = re.search(r'## Optimal Structure:\s*\n((?:\d+\..+\n?)+)', response_text, re.DOTALL)
        if structure_match:
            structure_lines = structure_match.group(1).strip().split('\n')
            for line in structure_lines:
                # Parse: "1. **H2: heading text** - ACTION" or "1. H2: heading text - ACTION"
                match = re.match(r'\d+\.\s*\*?\*?H2:\s*(.+?)\*?\*?\s*-\s*(KEEP|IMPROVE|ADD|REMOVE)', line, re.IGNORECASE)
                if match:
                    parsed['optimal_structure'].append({
                        'heading': self._to_sentence_case(match.group(1).strip()),
                        'action': match.group(2).lower()
                    })

        return parsed


# Convenience function for Streamlit
def analyze_serp(keyword: str, num_results: int = 10) -> Dict[str, Any]:
    """Run SERP analysis for a keyword"""
    analyzer = SERPAnalyzer()
    return analyzer.run_full_analysis(keyword, num_results)