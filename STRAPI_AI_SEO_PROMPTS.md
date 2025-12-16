# Strapi AI SEO Optimization Prompts

**Version:** 1.0
**Date:** 2025-11-20
**Purpose:** AI prompts for optimizing Strapi-generated landing pages for SEO and conversion

---

## Table of Contents

1. [Overview](#overview)
2. [Strategic Plan](#strategic-plan)
3. [Prompt 1: Content SEO Optimization](#prompt-1-content-seo-optimization)
4. [Prompt 2: SEO Title Generation](#prompt-2-seo-title-generation)
5. [Prompt 3: Meta Description Generation](#prompt-3-meta-description-generation)
6. [Implementation Guide](#implementation-guide)

---

## Overview

**Status:** Draft for Discussion
**Purpose:** Brainstorm document for team meeting

This document contains three specialized prompts designed to integrate with Strapi's AI Page Builder for landing page optimization:

1. **Content SEO Optimization Prompt** - Post-generation page optimization
2. **SEO Title Generation Prompt** - Primary keyword-focused, 60 char max
3. **Meta Description Prompt** - Click-through optimized, 155 char max

> **Note:** This is a working document for discussion. Prompts can be adapted for either Claude 4.5 or OpenAI models based on team preference and testing results.

### Key Differences from Blog Content

- Landing pages are **conversion-focused** (not purely educational)
- Need to balance **SEO best practices** with **copywriting effectiveness**
- Allow for more **persuasive language** while maintaining quality
- Focus on **structure optimization** (H1, paragraphs) rather than semantic patterns
- Looser restrictions on promotional language (it's expected on landing pages)

---

## Strategic Plan

### Workflow Integration

```
Landing Page AI Generation (Strapi)
    ↓
Content SEO Optimization (Prompt #1)
    ↓
SEO Title Generation (Prompt #2)
    ↓
Meta Description Generation (Prompt #3)
    ↓
Save to Strapi CMS
```

### Model Configuration

**Recommended Models:**
- **Primary:** `claude-sonnet-4-5-20250929` (Claude 4.5 Sonnet - latest)
- **Alternative:** OpenAI `gpt-4o` or `gpt-4-turbo` (if preferred)

**Temperature & Token Settings:**
- **Content Optimization:** Temperature 0.7, Max tokens 4000 *(matches current system)*
- **SEO Title:** Temperature 0.7, Max tokens 50 *(creative but consistent)*
- **Meta Description:** Temperature 0.7, Max tokens 100 *(compelling CTR optimization)*

> **Note:** Temperature 0.7 is proven in the current Gcore content system for natural, human-like writing while maintaining accuracy. These prompts are model-agnostic and work with both Claude and OpenAI models.

---

## Prompt 1: Content SEO Optimization

**Purpose:** Optimize AI-generated landing page content for both SEO and conversion

**Input Variables:**
- `{GENERATED_PAGE_CONTENT}` - The HTML/text from Strapi AI Page Builder
- `{PRIMARY_KEYWORD}` - Target keyword for the page

### Full Prompt

```
You are an SEO optimization expert specializing in landing page content. Your task is to optimize the provided AI-generated landing page content for search engines while maintaining conversion-focused copy.

CONTENT TO OPTIMIZE:
{GENERATED_PAGE_CONTENT}

PRIMARY KEYWORD: {PRIMARY_KEYWORD}

OPTIMIZATION OBJECTIVES:
1. SEO structure and readability
2. Conversion-focused copy effectiveness
3. Brand voice consistency (Gcore: professional yet approachable)

=============================================================
CRITICAL SEO STRUCTURE REQUIREMENTS
=============================================================

H1 OPTIMIZATION:
• Exactly ONE H1 tag per page (must exist)
• H1 must include the primary keyword naturally
• Keep H1 between 30-70 characters
• Use sentence case, not title case
• Make it compelling and benefit-focused
• Examples:
  ✅ "Enterprise CDN solutions for global content delivery"
  ✅ "Cloud GPU hosting that scales with your needs"
  ❌ "The Best CDN Solution For All Your Needs" (too salesy)
  ❌ "CDN" (too short, not descriptive)

HEADING HIERARCHY:
• Maintain logical structure: H1 → H2 → H3 (no skipping levels)
• Each H2 should relate to main topic
• H2s should include semantic keywords (not exact match)
• Use 2-5 H2 sections maximum for landing pages
• Keep headings concise: 3-8 words optimal

PARAGRAPH OPTIMIZATION:
• First paragraph must include primary keyword within first 100 words
• Break long paragraphs: Maximum 3-4 sentences (150 words)
• Break long sentences: Maximum 25 words per sentence
• Use short sentences for impact (vary length: 8-25 words)
• Add white space for scanability

KEYWORD INTEGRATION:
• Primary keyword density: 0.5-1.5% (natural, not forced)
• Include primary keyword in:
  - H1 (required)
  - First paragraph (required)
  - At least one H2 (natural variation)
  - Final paragraph/CTA section
• Use semantic variations and related terms
• NEVER keyword stuff - readability first

=============================================================
LANDING PAGE COPYWRITING PRINCIPLES
=============================================================

CONVERSION FOCUS:
• Keep benefit-driven language (landing pages need this)
• Allow value propositions and unique selling points
• Persuasive language is ACCEPTABLE for landing pages
• CTAs can be direct and action-oriented
• Address pain points and solutions

TONE & VOICE (Gcore Brand):
• Professional but approachable
• Confident without being arrogant
• Technical accuracy with clear explanations
• Use "you/your" to address readers
• Contractions are acceptable (it's, you're, don't)
• Active voice preferred

READABILITY:
• Use bullet points for features/benefits
• Bold important phrases (maximum 2-3 per section)
• Short paragraphs with clear topic sentences
• Transition words for flow
• Scannable content structure

=============================================================
QUALITY STANDARDS
=============================================================

PROHIBITED AI PATTERNS (avoid but not critical for landing pages):
• Minimize: leverage, utilize, delve, moreover, furthermore
• Avoid overly formal language: "aforementioned", "wherein", "henceforth"
• Limit uncertainty words: perhaps, maybe, possibly, arguably
• Remove academic phrases: "it is important to note", "as previously mentioned"

COMPETITOR MENTIONS:
• NEVER mention competitors by name:
  ❌ AWS, Azure, Google Cloud, Cloudflare, Akamai, Fastly
• Use generic terms:
  ✅ "leading cloud providers"
  ✅ "major CDN platforms"
  ✅ "enterprise hosting solutions"

TECHNICAL ACCURACY:
• Verify technical claims are accurate
• Use specific metrics when possible (30ms latency, 185+ PoPs)
• Avoid superlatives without backing: "best", "fastest", "#1"
• Replace with specific claims: "30ms average latency", "99.9% uptime SLA"

FORMATTING CLEANUP:
• Remove any HTML/Markdown mixing issues
• Ensure consistent formatting throughout
• Clean up double spaces and awkward line breaks
• Proper punctuation and grammar

=============================================================
OUTPUT REQUIREMENTS
=============================================================

Return ONLY the optimized content in clean HTML format with:
- Properly structured H1, H2, H3 tags
- Paragraph tags (<p>) for all body text
- Bullet lists (<ul><li>) where appropriate
- Bold tags (<strong>) for emphasis (use sparingly)
- No inline styles or unnecessary markup
- No meta-commentary or explanations

VALIDATION CHECKLIST:
✓ ONE H1 tag with primary keyword
✓ Logical heading hierarchy (H1→H2→H3)
✓ Primary keyword in first 100 words
✓ Paragraphs under 150 words
✓ Sentences under 25 words (with variety)
✓ No competitor mentions
✓ Conversion-focused tone maintained
✓ Clean HTML structure

Generate the optimized content now:
```

---

## Prompt 2: SEO Title Generation

**Purpose:** Generate optimized SEO titles with primary keyword integration

**Input Variables:**
- `{PAGE_TOPIC}` - Brief description of the page (e.g., "Enterprise CDN Services")
- `{PRIMARY_KEYWORD}` - Target keyword (e.g., "enterprise CDN")
- `{BRIEF_CONTENT_SUMMARY}` - Optional 1-2 sentence summary

### Full Prompt

```
You are an SEO title specialist. Generate an optimized SEO title tag for the following page.

PAGE TOPIC: {PAGE_TOPIC}
PRIMARY KEYWORD: {PRIMARY_KEYWORD}
PAGE CONTENT SUMMARY: {BRIEF_CONTENT_SUMMARY}

=============================================================
SEO TITLE REQUIREMENTS (CRITICAL)
=============================================================

LENGTH:
• Minimum: 30 characters
• Maximum: 60 characters (STRICT LIMIT - longer titles get truncated)
• Optimal: 50-60 characters for maximum display
• Count includes spaces and punctuation

KEYWORD PLACEMENT:
• Primary keyword MUST appear in title
• Place keyword as close to the beginning as natural
• If brand name included, put keyword first: "Keyword | Gcore"
• Examples:
  ✅ "Enterprise CDN Solutions | Gcore" (32 chars)
  ✅ "Cloud GPU Hosting for AI Workloads" (35 chars)
  ✅ "Edge Computing Platform - Fast & Secure" (42 chars)
  ❌ "Gcore's Amazing Revolutionary Cloud GPU Hosting Solutions" (59 chars, keyword too far back)

STRUCTURE PATTERNS:
Choose the most appropriate pattern:
1. Primary Keyword + Benefit: "CDN Solutions for Global Performance"
2. Primary Keyword + Modifier: "Enterprise CDN Platform"
3. Primary Keyword | Brand: "Cloud GPU Hosting | Gcore"
4. Primary Keyword - Differentiator: "Edge CDN - 180+ Global PoPs"
5. Primary Keyword + Use Case: "CDN for Streaming & Gaming"

WRITING GUIDELINES:
• Use sentence case or title case (not all caps)
• Include numbers when relevant: "CDN with 180+ PoPs"
• Power words for clicks: Fast, Secure, Enterprise, Global, Managed
• Action-oriented when appropriate: "Deploy", "Scale", "Accelerate"
• Avoid: Very, Best, Ultimate (unless backing data exists)
• Be specific over generic: "30ms Latency CDN" > "Fast CDN"

CHARACTER COUNTING:
• Remember: spaces count as characters
• Special characters (-, |, &) count as 1 character each
• Preview: "{example}" = XX characters

=============================================================
QUALITY CHECKS
=============================================================

REQUIRED ELEMENTS:
✓ Primary keyword included
✓ 50-60 characters (ideal range)
✓ NEVER exceeds 60 characters
✓ Compelling and click-worthy
✓ Matches page content accurately
✓ No keyword stuffing
✓ Grammatically correct

AVOID:
❌ Clickbait or misleading titles
❌ All caps words (unless acronyms)
❌ Excessive punctuation (!!!, ???)
❌ Competitor brand names
❌ Generic phrases: "Welcome to", "Home Page", "Best Ever"
❌ Year dates (unless current and relevant)

=============================================================
OUTPUT FORMAT
=============================================================

Provide ONLY the SEO title text with character count:

[TITLE TEXT] (XX characters)

Example outputs:
"Enterprise CDN Solutions | Gcore" (32 characters)
"Cloud GPU for AI & Machine Learning" (37 characters)
"Global Edge Network - 180+ PoPs Worldwide" (43 characters)

Generate the SEO title now:
```

---

## Prompt 3: Meta Description Generation

**Purpose:** Generate click-through optimized meta descriptions

**Input Variables:**
- `{PAGE_TOPIC}` - Brief description of the page
- `{PRIMARY_KEYWORD}` - Target keyword
- `{BRIEF_CONTENT_SUMMARY}` - Optional 1-2 sentence summary
- `{TARGET_AUDIENCE}` - Optional (e.g., "enterprises", "developers", "startups")

### Full Prompt

```
You are a meta description specialist focused on maximizing click-through rates while optimizing for search.

PAGE TOPIC: {PAGE_TOPIC}
PRIMARY KEYWORD: {PRIMARY_KEYWORD}
PAGE CONTENT SUMMARY: {BRIEF_CONTENT_SUMMARY}
TARGET AUDIENCE: {TARGET_AUDIENCE} (optional)

=============================================================
META DESCRIPTION REQUIREMENTS (CRITICAL)
=============================================================

LENGTH:
• Minimum: 120 characters (too short looks incomplete)
• Maximum: 155 characters (STRICT LIMIT - text gets cut off after this)
• Optimal: 145-155 characters (use full space available)
• Count includes spaces, punctuation, and special characters

KEYWORD INTEGRATION:
• Primary keyword MUST appear naturally (Google bolds matching terms)
• Place keyword in first half when possible (more visible)
• Use keyword once, with variations/related terms for context
• Examples:
  ✅ "Deploy enterprise CDN solutions with 180+ global PoPs. Experience 30ms latency, DDoS protection, and 99.9% uptime. Start your free trial today." (155 chars)
  ✅ "Cloud GPU hosting optimized for AI workloads. Scale instantly with NVIDIA GPUs, pay-per-use pricing, and 24/7 support." (121 chars)

CLICK-THROUGH OPTIMIZATION:
• Start with benefit or unique value proposition
• Include specific differentiators (numbers, features, guarantees)
• Add clear call-to-action at the end
• Create urgency or highlight competitive advantage
• Answer user intent directly

CTAs THAT WORK:
• "Get started free"
• "Start your trial"
• "Request demo"
• "Compare plans"
• "Learn more"
• "See pricing"
• "Talk to expert"

PERSUASIVE ELEMENTS:
• Specific metrics: "30ms latency", "180+ PoPs", "99.9% uptime"
• Social proof: "Trusted by 1000+ enterprises"
• Free offers: "Free trial", "No credit card"
• Guarantees: "Money-back guarantee", "SLA-backed"
• Speed indicators: "Deploy in minutes", "5-minute setup"

=============================================================
STRUCTURE PATTERNS
=============================================================

Choose the most effective pattern for your use case:

Pattern 1 - Problem/Solution:
"[Problem]? [Solution with keyword]. [Key benefits]. [CTA]."
Example: "Struggling with slow content delivery? Deploy Gcore's enterprise CDN with 180+ global PoPs. 30ms latency, DDoS protection. Start free trial." (155)

Pattern 2 - Value Proposition:
"[Main benefit with keyword]. [Supporting benefits]. [Differentiator]. [CTA]."
Example: "Enterprise CDN solutions with unmatched performance. 180+ PoPs, advanced security, real-time analytics. 99.9% uptime SLA. Get started today." (155)

Pattern 3 - Feature-Benefit:
"[Keyword + core feature]. [Benefit 1]. [Benefit 2]. [CTA]."
Example: "Cloud GPU hosting for AI and machine learning. Scale instantly with NVIDIA A100s. Pay-per-use pricing, 24/7 support. Deploy in minutes." (145)

Pattern 4 - Audience-Specific:
"[Solution] for [audience] with [keyword]. [Key benefits]. [Trust element]. [CTA]."
Example: "CDN platform built for enterprises. Global edge network, advanced DDoS protection, dedicated support. Trusted by Fortune 500s. Talk to expert." (155)

=============================================================
WRITING GUIDELINES
=============================================================

TONE & STYLE:
• Professional but compelling
• Direct and benefit-focused
• Active voice (not passive)
• Use numbers and specifics (avoid vague claims)
• Clear and concise (no fluff)

PUNCTUATION:
• Use periods for complete sentences
• Commas for lists of benefits
• Avoid: exclamation points (looks spammy), question marks (unless rhetorical)

POWER WORDS FOR CTR:
• Technical: Enterprise, Advanced, Secure, Scalable, Managed
• Performance: Fast, Instant, Optimized, Efficient
• Value: Free, Affordable, Flexible, Custom
• Trust: Certified, Compliant, Reliable, Proven
• Action: Deploy, Scale, Accelerate, Optimize

=============================================================
QUALITY CHECKS
=============================================================

REQUIRED ELEMENTS:
✓ Primary keyword included naturally
✓ 145-155 characters (optimal range)
✓ NEVER exceeds 155 characters
✓ Includes call-to-action
✓ Specific benefits/differentiators
✓ Grammatically correct
✓ Matches page content accurately

AVOID:
❌ Generic descriptions: "Learn more about [keyword] on our website"
❌ Keyword stuffing: "CDN CDN solutions CDN services CDN platform"
❌ Misleading claims or clickbait
❌ Duplicate content from title tag
❌ Cutting off mid-sentence (stay under 155 chars)
❌ Competitor mentions
❌ Special characters that waste space (©, ™, ®)

=============================================================
CHARACTER COUNTING TIPS
=============================================================

• Every character counts: spaces, commas, periods
• Short words save space: "Get" vs "Obtain", "24/7" vs "round-the-clock"
• Ampersands save characters: "& " (2) vs "and " (4)
• Numbers are efficient: "180+" vs "over one hundred eighty"
• Abbreviations when clear: "PoPs" vs "Points of Presence"

=============================================================
OUTPUT FORMAT
=============================================================

Provide ONLY the meta description text with character count:

[META DESCRIPTION TEXT] (XXX characters)

Example outputs:
"Deploy enterprise CDN solutions with 180+ global PoPs. Experience 30ms latency, DDoS protection, and 99.9% uptime. Start your free trial today." (155 characters)

"Cloud GPU hosting optimized for AI workloads. Scale instantly with NVIDIA GPUs, pay-per-use pricing, and 24/7 support. Deploy in minutes." (142 characters)

Generate the meta description now:
```

---

## Implementation Guide

### API Integration Points

#### 1. Content Optimization Endpoint

**Option A: Claude 4.5 Sonnet**
```javascript
{
  "model": "claude-sonnet-4-5-20250929",
  "temperature": 0.7,
  "max_tokens": 4000,
  "messages": [
    {
      "role": "user",
      "content": "[Full Prompt 1 with variables replaced]"
    }
  ]
}
```

**Option B: OpenAI GPT-4o**
```javascript
{
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 4000,
  "messages": [
    {
      "role": "user",
      "content": "[Full Prompt 1 with variables replaced]"
    }
  ]
}
```

**Input:**
- Generated page HTML from Strapi
- Primary keyword

**Output:**
- Optimized HTML content

---

#### 2. SEO Title Endpoint

**Option A: Claude 4.5 Sonnet**
```javascript
{
  "model": "claude-sonnet-4-5-20250929",
  "temperature": 0.7,
  "max_tokens": 50,
  "messages": [
    {
      "role": "user",
      "content": "[Full Prompt 2 with variables replaced]"
    }
  ]
}
```

**Option B: OpenAI GPT-4o**
```javascript
{
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 50,
  "messages": [
    {
      "role": "user",
      "content": "[Full Prompt 2 with variables replaced]"
    }
  ]
}
```

**Input:**
- Page topic
- Primary keyword
- Brief content summary

**Output:**
- SEO title (with character count)

---

#### 3. Meta Description Endpoint

**Option A: Claude 4.5 Sonnet**
```javascript
{
  "model": "claude-sonnet-4-5-20250929",
  "temperature": 0.7,
  "max_tokens": 100,
  "messages": [
    {
      "role": "user",
      "content": "[Full Prompt 3 with variables replaced]"
    }
  ]
}
```

**Option B: OpenAI GPT-4o**
```javascript
{
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 100,
  "messages": [
    {
      "role": "user",
      "content": "[Full Prompt 3 with variables replaced]"
    }
  ]
}
```

**Input:**
- Page topic
- Primary keyword
- Brief content summary
- Target audience (optional)

**Output:**
- Meta description (with character count)

---

### Strapi Button Configuration

#### Button 1: "Optimize Page for SEO"
- Triggers: Content Optimization Prompt
- Shows: Before/after preview with changes highlighted
- Validates: H1 exists, keyword present, structure correct

#### Button 2: "Generate SEO Title"
- Triggers: SEO Title Generation Prompt
- Shows: Character count + Google SERP preview
- Validates: 30-60 character limit

#### Button 3: "Generate Meta Description"
- Triggers: Meta Description Generation Prompt
- Shows: Character count + Google SERP preview
- Validates: 120-155 character limit

---

### Validation & Preview

Add these UI elements to Strapi:

1. **Character Counter**
   - Real-time count for title (60 max) and meta description (155 max)
   - Visual indicator: green (optimal), yellow (acceptable), red (too long)

2. **Google SERP Preview**
   - Mock-up showing how title + description appear in search results
   - Shows truncation if over limit

3. **Keyword Density Check**
   - Highlight primary keyword occurrences in optimized content
   - Show density percentage (target: 0.5-1.5%)

4. **Structure Validation**
   - Check for H1 presence and uniqueness
   - Verify heading hierarchy (H1→H2→H3)
   - Flag any structure issues

---

### Best Practices

1. **Always provide primary keyword** - Required for all three prompts
2. **Use brief content summaries** - 1-2 sentences max for context
3. **Run prompts in sequence** - Optimize content first, then generate title/meta
4. **Review AI output** - Always validate before publishing
5. **Test character counts** - Use validation before saving to Strapi
6. **A/B test variations** - Generate 2-3 options and test performance

### Model Selection Discussion Points

**Claude 4.5 Sonnet Advantages:**
- Superior instruction following for complex SEO requirements
- Better at maintaining exact character limits
- Excellent at preserving brand voice consistency
- More reliable with structured output formats

**OpenAI GPT-4o Advantages:**
- Potentially lower latency
- May have different pricing structure
- Strong performance on creative copywriting
- Good alternative for redundancy/failover

**Recommendation:** Test both models with sample landing pages and compare:
- Output quality and SEO compliance
- Character count accuracy (title/meta limits)
- Brand voice consistency
- Cost per optimization
- Response time

---

### Troubleshooting

**Issue:** Title or meta description too long
- **Solution:** Reduce content summary input or regenerate with "make it shorter" instruction

**Issue:** Keyword not appearing naturally
- **Solution:** Provide better context in content summary about keyword usage

**Issue:** Too promotional/salesy
- **Solution:** Remind prompt about professional tone in additional instructions

**Issue:** HTML formatting errors
- **Solution:** Validate HTML output before saving to Strapi database

---

## Discussion Topics for Meeting

### 1. Model Selection
- [ ] Test Claude 4.5 vs OpenAI GPT-4o
- [ ] Compare costs and performance
- [ ] Decide on primary model or hybrid approach

### 2. Integration Workflow
- [ ] Confirm Strapi button placement
- [ ] Discuss user interface for prompt inputs
- [ ] Review approval process before publishing

### 3. Customization Needs
- [ ] Additional input fields needed?
- [ ] Custom validation rules for Gcore pages?
- [ ] Integration with existing Strapi workflows

### 4. Testing & Validation
- [ ] QA process for AI-generated content
- [ ] Character limit enforcement (title/meta)
- [ ] SEO compliance checks

### 5. Edge Cases
- [ ] How to handle very technical products?
- [ ] Multi-language support needed?
- [ ] Product-specific customizations?

---

## Version History

- **v0.1** (2025-11-20): Draft for team discussion
  - Content SEO Optimization prompt
  - SEO Title Generation prompt
  - Meta Description Generation prompt
  - Added model flexibility (Claude 4.5 / OpenAI)

---

## Next Steps

1. Review prompts in team meeting
2. Test with sample landing pages
3. Compare model outputs (Claude vs OpenAI)
4. Refine prompts based on feedback
5. Finalize integration approach

**Document Status:** Draft - Ready for Discussion
**Last Updated:** 2025-11-20
