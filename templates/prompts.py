"""
Prompt Templates for Content Generation
Based on semantic SEO patterns and Gcore brand guidelines
"""

from typing import Dict, Any

# Base system prompt for all content generation
SYSTEM_PROMPT = """
You are a content writer for Gcore, a global edge computing and content delivery company with 180+ Points of Presence worldwide and 30ms average latency.

Your writing must:
1. Follow semantic SEO principles by directly answering questions
2. Use formal but approachable language
3. Include contractions naturally (it's, don't, etc.)
4. Avoid AI-sounding words and phrases
5. Incorporate specific metrics and data
6. Keep sentences under 30 words
7. Keep paragraphs under 150 words
8. Use sentence case for headings
9. Never use em dashes (—) in content - use regular hyphens (-) or commas for breaks instead
"""

# Pattern-specific prompt templates
PATTERN_PROMPTS = {
    'definition_singular': """
Write a definition for: {heading}

Requirements (per Holistic SEO SOP):
- MUST start with "A {subject} is..." or "{Subject} is..." as grammatically appropriate
- First sentence: Clear, comprehensive definition using semantic triple
- Follow with 2-3 sentences of expansion that elaborate
- Keep in paragraph form (no lists)
- Use formal but approachable language
- NO uncertainty words (maybe, perhaps, probably)
- NO brand mentions or sales language
- NO competitor mentions (AWS, Azure, GCP, etc.)
- Include specific facts and data points from research only
- Target {min_words}-{max_words} words

Semantic Triple Structure:
- Subject: What/who is being defined
- Predicate: The relationship/action
- Object: The definition/explanation

Research context:
{research_context}

Write the definition now:
""",
    
    'definition_plural': """
Create a list for: {heading}

Requirements (per Holistic SEO SOP):
- MUST start with "The {subject} are listed below."
- Follow immediately with a bulleted list
- Format: • **Term**: Clear explanation starting with what it is
- Include 3-7 relevant items based on research
- Each explanation: 1-2 complete sentences
- Use colons after bold terms (not dashes or other punctuation)
- Definitions must be substantive and specific
- NO vague or generic descriptions
- Target {min_words}-{max_words} words total

List Structure:
- Each item must be self-contained and complete
- Order by importance or logical progression
- Ensure each definition could stand alone

Research context:
{research_context}

Write the list now:
""",
    
    'how_to': """
Write instructions for: {heading}

Requirements (per Holistic SEO SOP):
- MUST start: "To {action}, [first step]..."
- Provide clear step-by-step instructions
- Use transition words: First, Then, Next, After that, Finally
- Each step must be specific and actionable
- Can use numbered list OR paragraph form with transitions
- Include concrete examples or specific tools/methods
- NO vague instructions like "configure properly"
- Target {min_words}-{max_words} words

Structure Options:
1. Paragraph form: "To [action], first [step]. Then [step]. Finally [step]."
2. Numbered list after opening sentence

Research context:
{research_context}

Write the instructions now:
""",
    
    'how_process': """
Explain the process for: {heading}

Requirements:
- Start with "{subject} works by..."
- Explain the mechanism or process clearly
- Break down into logical components
- Include technical details appropriate for the audience
- Reference Gcore infrastructure where relevant
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the explanation now:
""",
    
    'yes_no': """
Answer this yes/no question: {heading}

Requirements (per Holistic SEO SOP):
- MUST start with "Yes," or "No," (with comma)
- Immediately follow with the main answer/explanation
- Provide 2-3 sentences of supporting evidence
- Include specific facts, statistics, or examples
- Keep direct and authoritative
- NO hedging or uncertainty
- If conditional, still start with Yes/No then explain conditions
- Include specific evidence or examples
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the answer now:
""",
    
    'why': """
Answer this why question: {heading}

Requirements (per Holistic SEO SOP):
- MUST start: "{Subject} {predicate} because [main reason]..."
- Provide clear causal explanation
- Follow with 2-3 supporting points or elaboration
- Use specific examples or evidence
- Keep logical flow from cause to effect
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the explanation now:
""",
    
    'when': """
Answer this when question: {heading}

Requirements (per Holistic SEO SOP):
- MUST start: "{Subject} should be {action} when [condition]..." or "{Subject} occurs when..."
- Provide specific timing, conditions, or circumstances
- Include multiple scenarios if applicable
- Be precise with timeframes or triggers
- Avoid vague terms like "sometimes" or "occasionally"
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the answer now:
""",
    
    'where': """
Answer this where question: {heading}

Requirements (per Holistic SEO SOP):
- MUST start: "{Subject} is located/found/occurs in [location]..." or "{Subject} are typically stored in..."
- Provide specific locations, contexts, or environments
- Include geographical, digital, or conceptual locations as appropriate
- Add relevant details about distribution or availability
- Be precise and comprehensive
- NO specific brand or competitor mentions (use generic terms like "major cloud providers")
- Focus on general availability patterns rather than promoting specific services
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the answer now:
""",
    
    'who': """
Answer this who question: {heading}

Requirements (per Holistic SEO SOP):
- MUST start: "{Subject} is/are [identification]..." or "The person/organization responsible is..."
- Clearly identify the person(s), organization(s), or entity
- Provide relevant credentials, roles, or characteristics
- Include why they are significant to the topic
- Be specific with names, titles, or descriptions
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the answer now:
""",
    
    'which': """
Answer this which question: {heading}

Requirements (per Holistic SEO SOP):
- MUST start with direct identification of the selection/choice
- Format: "{Subject} that [criteria] include..." or "The [options] are..."
- Clearly state which option(s) are being discussed
- Provide comparison or differentiation if multiple options
- Include criteria for selection if applicable
- Be definitive in the answer
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the answer now:
""",
    
    'general': """
Write content for: {heading}

Requirements:
- Provide comprehensive coverage of the topic
- Structure information logically
- Include relevant examples and data
- Maintain Gcore brand voice
- Target {min_words}-{max_words} words

Research context:
{research_context}

Write the content now:
"""
}

# Regeneration prompt template
REGENERATION_PROMPT = """
Original heading: {heading}
Pattern type: {pattern_type}

Original content:
{original_content}

User feedback: {feedback}

Please regenerate the content addressing the feedback while:
1. Maintaining the {pattern_type} pattern structure
2. Directly answering the question
3. Following Gcore brand guidelines
4. Avoiding AI-sounding words
5. Keeping the same target length

Regenerated content:
"""

# Quality improvement prompt
QUALITY_IMPROVEMENT_PROMPT = """
Improve this content for: {heading}

Current content:
{content}

Quality issues found:
{issues}

Please rewrite to:
1. Address all quality issues
2. Maintain the same pattern structure
3. Keep similar length
4. Improve clarity and directness

Improved content:
"""

# SEO optimization prompt
SEO_OPTIMIZATION_PROMPT = """
Optimize this content for SEO: {heading}

Primary keyword: {keyword}
Current content:
{content}

SEO requirements:
1. Include primary keyword 2-3 times naturally
2. Add semantic keywords: {semantic_keywords}
3. Ensure keyword appears in opening
4. Maintain natural flow
5. Keep the same pattern structure

Optimized content:
"""

def get_prompt(pattern_type: str, **kwargs) -> str:
    """Get the appropriate prompt template for a pattern type"""
    template = PATTERN_PROMPTS.get(pattern_type, PATTERN_PROMPTS['general'])
    return template.format(**kwargs)

def get_system_prompt() -> str:
    """Get the system prompt for content generation"""
    return SYSTEM_PROMPT

def get_regeneration_prompt(**kwargs) -> str:
    """Get the regeneration prompt template"""
    return REGENERATION_PROMPT.format(**kwargs)

def get_quality_prompt(**kwargs) -> str:
    """Get the quality improvement prompt"""
    return QUALITY_IMPROVEMENT_PROMPT.format(**kwargs)

def get_seo_prompt(**kwargs) -> str:
    """Get the SEO optimization prompt"""
    return SEO_OPTIMIZATION_PROMPT.format(**kwargs)