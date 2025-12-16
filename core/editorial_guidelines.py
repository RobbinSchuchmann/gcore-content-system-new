"""
Gcore Editorial Guidelines
Contains reusable constants for Gcore's editorial voice and writing principles
Based on: Chicago Manual of Style, Google Developer Style Guide, Microsoft Writing Style Guide
"""

# American English Rules
AMERICAN_ENGLISH_RULES = """
AMERICAN ENGLISH (MANDATORY):
• Use American spellings consistently throughout:
  - "-ize" not "-ise" (optimize, customize, organize)
  - "-or" not "-our" (color, behavior, favor)
  - "-er" not "-re" (center, meter, fiber)
  - "-og" not "-ogue" (catalog, dialog, analog)
  - "-ment" not "-ement" (judgment, acknowledgment)
  - "-ense" not "-ence" (defense, offense, license)
• Common technical terms (American spelling):
  - analyze, authorize, synchronize, initialize
  - virtualization, containerization, optimization
  - canceled (one 'l'), labeled, traveled
"""

# Number Formatting Rules (Chicago Manual of Style)
NUMBER_FORMATTING_RULES = """
NUMBER FORMATTING (CHICAGO MANUAL OF STYLE):
• Spell out zero through nine in running text
• Use numerals for 10 and above
• EXCEPTIONS - always use numerals for:
  - Technical values: 5 GB, 3 ms, 2 vCPUs, version 3
  - Percentages: 5%, 99.9% uptime
  - Measurements: 4 TB storage, 8 GB RAM
  - When mixed with larger numbers: "between 3 and 15 servers"
• NUMBER RANGES - use words, not dashes:
  - "five to ten" not "5-10" or "5–10"
  - "from 100 to 500 requests" not "100-500 requests"
  - EXCEPTION: Technical specifications may use hyphens (e.g., "100-500ms response time")
• Spell out ordinals: first, second, third (not 1st, 2nd, 3rd)
• Use commas in numbers 1,000 and above
• Avoid quoting exact monetary amounts when possible; use ranges or qualitative descriptions
"""

# Pronoun Rules
PRONOUN_RULES = """
PRONOUN USAGE:
• AVOID first-person pronouns (I, we, our, us) in most content
• Use second person ("you", "your") to address the reader directly
• EXCEPTION: When Gcore is explicitly the subject, "Gcore offers..." is preferred over "We offer..."
• Acceptable patterns:
  - "You can configure..." (preferred)
  - "Gcore provides..." (when company is subject)
  - "This feature allows..." (neutral)
• Avoid patterns:
  - "We recommend..." → "The recommended approach is..."
  - "Our platform..." → "The Gcore platform..." or "This platform..."
  - "We'll show you..." → "This guide shows..."
"""

# Punctuation and Chicago Style Rules
CHICAGO_STYLE_RULES = """
PUNCTUATION (CHICAGO MANUAL OF STYLE):
• Use the serial (Oxford) comma: "CDN, edge computing, and cloud services"
• Em dashes (—): Use sparingly for sentence breaks, no spaces around them
  - Prefer commas or parentheses when possible
  - NEVER use en dashes (–) for sentence breaks
• Hyphens: Use for compound modifiers before nouns ("high-performance computing")
• Quotation marks: Use double quotes for direct quotations, single for quotes within quotes
• Periods and commas: Always inside quotation marks (American style)
• Colons: Capitalize the first word after a colon only if it begins a complete sentence
"""

# Technical Writing Style (aligned with GCP, DigitalOcean, AWS conventions)
TECHNICAL_WRITING_STYLE = """
TECHNICAL WRITING STYLE:
• Follow terminology conventions from: Google Cloud (GCP), DigitalOcean, AWS (in preference order)
• Use present tense for documentation: "This command creates..." not "This command will create..."
• Active voice preferred: "The API returns data" not "Data is returned by the API"
• Be direct: "Click Submit" not "You should click the Submit button"
• Minimize repetition - repeat keywords only as needed for SEO, not for emphasis
• Context-dependent specificity:
  - Technical sections: Use exact Gcore metrics (30ms latency, 210+ PoPs, 99.9% uptime)
  - General content: May use qualitative descriptions ("ultra-low latency", "global presence")
"""

# Gcore Editorial Principles (from Gcore Editorial Guidelines)
GCORE_PRINCIPLES = """
GCORE EDITORIAL PRINCIPLES:
• Be simple: Use simple structures, short sentences are good (mix 5-10 word with 20-30 word sentences)
• Be concise: Use as few words as possible to convey your message
• Be friendly: Write like you talk - relaxed, warm, natural tone with active voice
• Be helpful: Focus on what the reader needs, not just corporate messaging
• Be specific: Use exact numbers and facts (30ms, 210+ PoPs), not vague terms (very fast, many)
"""

# Gcore Editorial Voice Description
GCORE_VOICE = """
GCORE EDITORIAL VOICE:
You are a knowledgeable expert writing for technical professionals. Your voice should be:
- Professional but approachable (like a helpful colleague explaining concepts)
- Clear and direct, not corporate or stuffy
- Warm and natural, not casual or sloppy
- Authoritative but friendly
"""

# Writing Style Guidelines
WRITING_STYLE = """
WRITING STYLE (GCORE STANDARDS):
- Vary sentence length naturally: Mix short punchy sentences (5-10 words) with detailed ones (20-30 words)
- Use contractions naturally where they sound professional (it's, don't, can't, you'll)
- Active voice preferred: "Cloud GPUs process data" not "Data is processed by cloud GPUs"
- Direct language: "use" not "utilize", "help" not "facilitate", "work" not "operate"
- Remove filler phrases: "It's worth noting that" → just state the fact directly
- Front-load important information: Put key points at the start of sentences
"""

# Humanization Instructions
HUMANIZATION_INSTRUCTIONS = """
GCORE HUMANIZATION GUIDELINES:

IMPROVEMENTS TO MAKE:
1. Replace overly formal vocabulary with clearer professional alternatives:
   - "encompasses" → "includes"
   - "whilst" → "while"
   - "thus" → "therefore"
   - "leverage" → "use"
   - "utilize" → "use"
   - "facilitate" → "help" or "enable"

2. Improve sentence rhythm and flow:
   - Mix short clear sentences (5-10 words) with detailed explanatory ones (20-30 words)
   - Vary sentence starters naturally
   - Remove choppy or overly uniform patterns

3. Use contractions where natural in professional writing:
   - "it's" instead of "it is"
   - "don't" instead of "do not"
   - "you'll" instead of "you will"
   - BUT: Keep formal in technical definitions and specifications

4. Remove AI-sounding patterns:
   - "It's worth noting that" → "Note that" or remove entirely
   - "In today's digital landscape" → "Currently" or "Today"
   - "Let's dive into" → "Let's explore"
   - "It's important to understand" → just explain it directly

5. CRITICAL: Replace ALL em-dashes (—) with commas, periods, or parentheses:
   - "botnets—networks of devices" → "botnets (networks of devices)" or "botnets, which are networks of devices,"
   - "400 Gbps—enough to" → "400 Gbps, enough to" or "400 Gbps. This is enough to"
   - Search specifically for the — character and replace EVERY instance
   - Exception: Keep en-dashes (–) for number ranges like "20-30%"

6. Use active voice and direct language where possible

7. AMERICAN ENGLISH - Convert any British spellings:
   - "optimise" → "optimize", "colour" → "color", "centre" → "center"
   - "behaviour" → "behavior", "favour" → "favor"
   - "licence" (noun) → "license", "defence" → "defense"
   - "cancelled" → "canceled", "labelled" → "labeled"

8. FIRST-PERSON PRONOUN REPLACEMENT:
   - "We recommend" → "The recommended approach is" or "Consider"
   - "We offer" → "Gcore offers" or "This service provides"
   - "Our platform" → "The Gcore platform" or "This platform"
   - "We'll show you" → "This guide shows" or "This section explains"
   - "our servers" → "Gcore servers" or "the servers"
   - Keep "you" and "your" for addressing the reader

9. NUMBER RANGE FORMATTING:
   - Replace dashes in ranges with "to": "5-10" → "five to ten" (for small numbers)
   - "100-500 requests" → "100 to 500 requests"
   - Keep technical specs as-is: "100-500ms" is acceptable

CRITICAL PROTECTIONS (DO NOT CHANGE):
- MAINTAIN professional, authoritative tone throughout
- NO casual slang, conversational filler, or informal language
- NO sentence fragments or incomplete sentences
- KEEP educational expert voice and technical precision
- PRESERVE semantic SEO patterns exactly (direct answers, structure)
- MAINTAIN all technical terminology and accuracy
- KEEP formal tone for definitions and technical specifications
- DO NOT change headings, lists, or structural elements
- DO NOT add or remove information or statistics
- PRESERVE exact Gcore metrics (30ms, 210+ PoPs) in technical content
"""

# =============================================================================
# GOOGLE DEVELOPER STYLE GUIDE ADDITIONS
# =============================================================================

# Timeless Documentation Rules
TIMELESS_DOCUMENTATION_RULES = """
TIMELESS DOCUMENTATION (GOOGLE STYLE GUIDE):
Write content that doesn't become outdated. Avoid time-anchored language.

WORDS/PHRASES TO AVOID (replace or remove):
• "currently" → remove, or specify version/date
• "now" → remove, or be specific about what changed
• "new/newer" → use version reference instead
• "latest" → specify the version number
• "soon/eventually" → remove, or give specific timeframe
• "as of this writing" → use specific date if needed
• "does not yet" → "does not" or specify version when feature arrives
• "old/older" → use version reference instead
• "presently/at present" → remove
• "existing" → remove if not necessary for clarity
• "in the future" → remove or specify timeline

ACCEPTABLE EXCEPTIONS:
• Release notes and changelogs (time context is appropriate)
• Version-specific documentation clearly labeled
• Blog posts with publication dates
"""

# Inclusive Language Rules
INCLUSIVE_LANGUAGE_RULES = """
INCLUSIVE LANGUAGE (GOOGLE STYLE GUIDE):
Use inclusive, bias-free terminology throughout.

REQUIRED REPLACEMENTS:
• "blacklist" → "denylist" or "blocklist"
• "whitelist" → "allowlist"
• "master/slave" → "primary/replica", "main/secondary", or "leader/follower"
• "master branch" → "main branch"
• "man-hours" → "person-hours" or "work hours"
• "sanity check" → "quick check", "validation", or "smoke test"
• "dummy value" → "placeholder value" or "sample value"
• "native" (for features) → "built-in"
• "grandfathered" → "legacy" or "exempted"

ABLEIST TERMS TO AVOID:
• "crazy/insane" → "unexpected", "unusual", or "surprising"
• "blind to" → "unaware of", "ignores", or "overlooks"
• "cripple/cripples" → "disable", "impair", or "limit"
• "dumb" → "silent", "mute", or "basic"
• "lame" → "inadequate" or "ineffective"

GENDERED LANGUAGE:
• Use gender-neutral pronouns: "they/their" for singular unknown person
• "mankind" → "humanity" or "people"
• "man-made" → "artificial" or "synthetic"
"""

# Sentence Structure Rules (Context-First)
GOOGLE_SENTENCE_STRUCTURE = """
SENTENCE STRUCTURE - CONTEXT FIRST (GOOGLE STYLE GUIDE):
For procedural/instructional content, lead with context before the action.

PATTERN: State the goal, condition, or context BEFORE the instruction.

✅ RECOMMENDED:
• "To delete the document, click Delete"
• "For more information, see the API reference"
• "If your app uses caching, configure TTL values first"
• "To improve performance, enable compression"

❌ AVOID:
• "Click Delete to delete the document"
• "See the API reference for more information"
• "Configure TTL values first if your app uses caching"
• "Enable compression to improve performance"

IMPORTANT EXCEPTION:
This rule does NOT apply to semantic SEO content patterns.
For H2/H3 question headings, the DIRECT ANSWER must come first.
Example: "What is a CDN?" → Answer starts with "A CDN is..."
The context-first rule applies only to procedural steps and instructions.
"""

# Heading Guidelines
HEADING_GUIDELINES = """
HEADING GUIDELINES (GOOGLE STYLE GUIDE):
Use clear, scannable headings that help readers find information.

TASK-BASED HEADINGS - Use infinitives (base verb), not gerunds (-ing):
✅ "Create an instance"     ❌ "Creating an instance"
✅ "Configure the API"      ❌ "Configuring the API"
✅ "Set up authentication"  ❌ "Setting up authentication"
✅ "Deploy to production"   ❌ "Deploying to production"

CONCEPTUAL HEADINGS - Use noun phrases without -ing verbs:
✅ "Authentication methods"  ❌ "Understanding authentication"
✅ "Cache configuration"     ❌ "Configuring caches"
✅ "API rate limits"         ❌ "Working with rate limits"

ADDITIONAL RULES:
• Use sentence case (already implemented)
• No punctuation at end of headings
• Avoid starting with articles (a, an, the) when possible
• Don't use questions as headings for procedural content
• Keep headings under 10 words when possible
• Don't use code font in headings unless necessary
"""

# Procedure/Instruction Writing Rules
PROCEDURE_WRITING_RULES = """
PROCEDURE WRITING (GOOGLE STYLE GUIDE):
Write clear, actionable instructions using imperative mood.

IMPERATIVE VERBS - Start steps with action verbs:
✅ "Click Submit"           ❌ "You should click Submit"
✅ "Enter your API key"     ❌ "The API key should be entered"
✅ "Run the command"        ❌ "You can run the command"
✅ "Select the option"      ❌ "The option needs to be selected"

STATE GOAL BEFORE ACTION:
✅ "To save your changes, click Save"
✅ "To view logs, open the Console"
❌ "Click Save to save your changes"

AVOID IN INSTRUCTIONS:
• "please" - unnecessary in technical instructions
• Directional terms: "above", "below", "right-hand side"
• "simply" or "just" - implies task is easy
• "Note that" at start of sentences - just state the information

OPTIONAL STEPS:
✅ "Optional: Enable debug mode"
❌ "(Optional) Enable debug mode"
❌ "You can optionally enable debug mode"

SINGLE-STEP PROCEDURES:
• Use a bullet point, not a numbered list
• A procedure with one step doesn't need numbering
"""

# Abbreviation Handling Rules
ABBREVIATION_RULES = """
ABBREVIATION HANDLING (GOOGLE STYLE GUIDE):
Spell out abbreviations on first reference, then use the short form.

FIRST REFERENCE FORMAT:
✅ "Content Delivery Network (CDN)"
✅ "Application Programming Interface (API)"
✅ "Transport Layer Security (TLS)"

SUBSEQUENT REFERENCES:
• Use only the abbreviation: "The CDN caches content..."

COMMON ABBREVIATIONS - No need to spell out:
API, URL, HTML, CSS, PDF, USB, AI, ML, CPU, GPU, RAM, SSD, IP, HTTP, HTTPS, DNS, SSL, TLS, SSH, FTP, SQL, JSON, XML, SDK, CLI, GUI, OS

RULES:
• Don't use periods in acronyms: "API" not "A.P.I."
• Don't use abbreviations as verbs: "Use SSH to connect" not "SSH into"
• Treat abbreviations as regular words for plurals: "APIs" not "API's"
• Article choice based on pronunciation: "an API" (sounds like "ay"), "a URL" (sounds like "you")
"""

# Link Text Guidelines
LINK_TEXT_RULES = """
LINK TEXT GUIDELINES (GOOGLE STYLE GUIDE):
Use descriptive, front-loaded link text that makes sense out of context.

DESCRIPTIVE LINK TEXT:
✅ "For details, see the authentication guide"
✅ "Learn more about rate limiting"
✅ "View the complete API reference"

AVOID VAGUE LINK TEXT:
❌ "click here"
❌ "this document"
❌ "this article"
❌ "here"
❌ "this page"
❌ "read more"

FRONT-LOAD IMPORTANT WORDS:
✅ "Authentication methods for APIs"
❌ "Methods for authenticating APIs"

CROSS-REFERENCE INTRODUCTIONS:
✅ "For more information, see..."
✅ "For details about X, see..."
✅ "To learn more, see..."

DON'T USE:
• Raw URLs as link text
• Full URLs in running text (use descriptive text)
• Redundant link text on same page to same destination
"""

# Date and Time Formatting Rules
DATE_TIME_RULES = """
DATE AND TIME FORMATTING (GOOGLE STYLE GUIDE):
Use consistent, unambiguous date and time formats.

DATE FORMATS:
✅ "January 19, 2025" (spell out month, four-digit year)
✅ "2025-01-19" (ISO format for technical/API contexts)
❌ "1/19/25" (ambiguous)
❌ "19/1/2025" (ambiguous)
❌ "Jan 19, 2025" (abbreviations only when space-constrained)

MONTH REFERENCES:
• Spell out month names in running text
• Four-digit years only
• Avoid seasons (spring, summer) - use months or quarters

TIME FORMATS:
✅ "3:45 PM" (space before AM/PM)
✅ "3 PM" (omit :00 for round hours)
✅ "9 AM to 5 PM" (ranges)
❌ "3:45PM" (no space)
❌ "3:00 PM" (unnecessary :00)
❌ "15:45" (use 12-hour unless technical context requires 24-hour)

TIME ZONES:
• Specify time zone when relevant: "3 PM EST"
• Use UTC for international technical contexts
"""

# Units of Measurement Rules
UNITS_RULES = """
UNITS OF MEASUREMENT (GOOGLE STYLE GUIDE):
Use consistent spacing and formatting for measurements.

SPACING RULES:
✅ "64 GB" (space between number and unit)
✅ "100 ms" (space before milliseconds)
✅ "30 Mbps" (space before rate units)
❌ "64GB" (no space)
❌ "100ms" (no space)

NO SPACE FOR:
• Currency: $10, €50
• Percentages: 65%, 99.9%
• Degrees: 90°, 45°

RANGES - Repeat the unit:
✅ "10 GB to 20 GB"
✅ "100 ms to 500 ms"
❌ "10-20 GB"
❌ "100-500 ms"

RATES - Use "per" over slashes in running text:
✅ "requests per second"
✅ "gigabytes per month"
❌ "requests/second" (acceptable in tables/UI)
❌ "GB/month" (acceptable in technical specs)

THOUSANDS:
• Use lowercase "k" for thousands: "55k operations"
• Use commas for 4+ digit numbers: "1,000" "10,000"

BINARY VS DECIMAL:
• GB, TB, MB = decimal (1000-based)
• GiB, TiB, MiB = binary (1024-based)
• Use what matches the technology being documented
"""

# Google Word List Additions
GOOGLE_WORD_LIST = """
WORD CHOICE (GOOGLE STYLE GUIDE):
Use clear, direct words. Avoid unnecessarily complex alternatives.

REQUIRED REPLACEMENTS:
• "allows you to" → "lets you"
• "in order to" → "to"
• "make sure" → "ensure" or "verify"
• "a number of" → specific number, "several", or "some"
• "etc." → complete the list, or use "and more"
• "impact" (as verb) → "affect"
• "utilize" → "use"
• "via" → "through" or "using"
• "i.e." → "that is" or rephrase
• "e.g." → "for example" or "such as"
• "enables" → "lets" or "allows"
• "provides the ability to" → "lets you"
• "has the capability to" → "can"
• "is able to" → "can"
• "in the event that" → "if"
• "at this point in time" → "now" or remove
• "due to the fact that" → "because"
• "for the purpose of" → "to" or "for"

DATA IS SINGULAR:
✅ "The data is stored"
❌ "The data are stored"
"""

# Tone Examples
TONE_EXAMPLES = """
GCORE TONE EXAMPLES:

❌ TOO STIFF (Avoid):
"Cloud-based GPU infrastructure facilitates the execution of computationally intensive workloads. Organizations leverage this technology to optimize performance whilst minimizing infrastructure costs."

✅ GCORE STYLE (Target):
"Cloud GPUs handle compute-intensive workloads like AI training and rendering. They're faster than traditional CPUs and don't require upfront hardware investment."

❌ TOO CASUAL (Avoid):
"Hey! Cloud GPUs are super cool for AI stuff. You're gonna love how fast they crunch numbers!"

ANALYSIS OF CORRECT EXAMPLE:
✓ Professional and accurate
✓ Simple, concise language
✓ Contraction used naturally ("They're")
✓ Active voice ("handle", not "are utilized for")
✓ Specific benefits stated clearly
✓ No casual slang, maintains authority
"""

def get_humanization_prompt_section() -> str:
    """
    Get the complete humanization prompt section for content generation

    Returns:
        Formatted string with Gcore editorial guidelines for humanization
    """
    return f"""
{GCORE_VOICE}

{GCORE_PRINCIPLES}

{WRITING_STYLE}

{AMERICAN_ENGLISH_RULES}

{NUMBER_FORMATTING_RULES}

{PRONOUN_RULES}

{HUMANIZATION_INSTRUCTIONS}

{INCLUSIVE_LANGUAGE_RULES}

{TIMELESS_DOCUMENTATION_RULES}

{GOOGLE_WORD_LIST}
"""

def get_generation_prompt_section() -> str:
    """
    Get the editorial guidelines section for initial content generation

    Returns:
        Formatted string with Gcore editorial principles for content generation
    """
    return f"""
{GCORE_VOICE}

{GCORE_PRINCIPLES}

{WRITING_STYLE}

{AMERICAN_ENGLISH_RULES}

{NUMBER_FORMATTING_RULES}

{PRONOUN_RULES}

{CHICAGO_STYLE_RULES}

{TECHNICAL_WRITING_STYLE}

{TIMELESS_DOCUMENTATION_RULES}

{INCLUSIVE_LANGUAGE_RULES}

{GOOGLE_SENTENCE_STRUCTURE}

{HEADING_GUIDELINES}

{PROCEDURE_WRITING_RULES}

{ABBREVIATION_RULES}

{LINK_TEXT_RULES}

{DATE_TIME_RULES}

{UNITS_RULES}

{GOOGLE_WORD_LIST}
"""
