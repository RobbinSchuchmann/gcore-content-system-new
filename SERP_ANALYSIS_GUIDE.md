# Competitor Analysis Guide

## Overview

The Competitor Analysis feature is designed to make SEO content creation accessible to **Virtual Assistants (VAs) and non-SEO professionals**. Instead of manually researching competitors and planning heading structures, you can now:

1. Enter a primary keyword
2. Search Google and copy competitor URLs
3. Paste URLs into the system (3-7 competitors)
4. Get AI-powered heading suggestions based on what's ranking

This eliminates the need for SEO expertise while ensuring your content is optimized for search engines.

---

## Table of Contents

- [What is Competitor Analysis?](#what-is-competitor-analysis)
- [How to Use Competitor Analysis](#how-to-use-competitor-analysis)
- [Understanding the Results](#understanding-the-results)
- [How It Works (Technical)](#how-it-works-technical)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## What is Competitor Analysis?

**Competitor Analysis** for SEO means:
- Looking at what content is currently ranking on Google for your keyword
- Analyzing how competitors structure their content (headings, topics covered)
- Using that data to create a better, more comprehensive content structure

**Why this matters for SEO:**
- Google ranks content that comprehensively covers topics
- Analyzing top-ranking pages reveals what Google considers important
- By covering the same topics (and more), you increase your chances of ranking

---

## How to Use Competitor Analysis

### Step-by-Step Workflow

#### 1. **Start with Your Primary Keyword**

Enter the main topic you want to write about:
- ✅ Good examples: "cloud computing", "CDN security", "edge computing benefits"
- ❌ Too vague: "technology", "cloud"
- ❌ Too specific: "how to configure CloudFront cache headers in AWS"

**Tip:** Use 2-4 word phrases that describe your main topic.

---

#### 2. **Search Google Manually**

1. Open Google in a new tab
2. Search for your keyword (e.g., "what is cloud computing")
3. Look at the top 10 results

**What to look for:**
- Direct competitors (AWS, Google Cloud, Azure, etc.)
- Authority sites (Wikipedia, major tech blogs)
- Comprehensive guides and tutorials

---

#### 3. **Copy Competitor URLs**

For each relevant result in Google:
1. Right-click the title → Copy link address
2. Or click the result and copy the URL from your browser

**Recommended:** Copy 3-7 URLs total

---

#### 4. **Add URLs to the System**

Back in the Gcore Content System:
1. Paste each URL into the "Competitor URL" field
2. Click "➕ Add URL"
3. Repeat for all competitors

**The system will:**
- Validate each URL
- Display added URLs with domains
- Allow you to remove URLs if needed

---

#### 5. **Analyze Competitors**

Once you have 2+ URLs added:

Click **"🤖 Analyze X Competitors"**

**How to choose competitors:**

✅ **DO Select:**
- Direct competitors (AWS, Google Cloud, Cloudflare, etc.)
- Authority sites with comprehensive content
- Pages with clear heading structures
- Mix of different perspectives (3-5 pages is ideal)

❌ **DON'T Select:**
- Your own Gcore pages
- Low-quality content farms
- Forums or Q&A sites (like Quora) unless they're exceptionally detailed
- Pages that are clearly outdated

**Recommended:** Select **3-7 competitors** for best results. Too few gives limited insights, too many creates noise.

---

#### 4. **Analyze Selected Competitors**

Click **"🤖 Analyze X Selected Competitors"**.

The system will:
1. **Extract headings** from each competitor page (H1, H2, H3)
2. **Analyze patterns** to find common topics across competitors
3. **Identify gaps** where you can add unique value
4. **Generate AI suggestions** for your optimal heading structure

**This process takes 30-60 seconds** depending on how many competitors you selected.

---

#### 5. **Review AI Suggestions**

Once complete, you'll see:

**📌 Suggested H1:** The main title for your article

**💡 Strategic Insights:** Explanation of why this structure will outperform competitors

**📋 Suggested H2/H3 Structure:**
- Each H2 section with explanation
- Suggested H3 subheadings under each H2
- FAQ section with common questions

**What the AI considers:**
- Topics all competitors cover (must-haves)
- Topics some competitors miss (opportunities)
- Logical flow and hierarchy
- Search intent (what users want to know)
- SEO best practices

---

#### 6. **Use or Edit Suggestions**

You have two options:

**Option A: "✅ Use These Suggestions"**
- Automatically applies the full heading structure to your content brief
- Proceeds to Step 1 (Content Brief) with everything pre-populated
- You can still edit manually in Step 1

**Option B: "📝 Edit Manually in Brief"**
- Moves to Step 1 with your keyword filled in
- You can reference the suggestions while building your own structure
- Good if you want to customize before proceeding

---

#### 7. **Skip SERP Analysis (Optional)**

If you already know your content structure, click **"Skip to Manual Brief →"** at any time.

This takes you directly to Step 1 where you can build your brief manually.

---

## Understanding the Results

### What Makes a Good Heading Structure?

The AI suggestions aim to create content that:

1. **Covers Core Topics**
   - All essential concepts competitors cover
   - Ensures you don't miss important information

2. **Fills Content Gaps**
   - Identifies topics competitors missed
   - Gives you opportunities to rank for additional keywords

3. **Follows Logical Flow**
   - Introduction → Core concepts → Advanced topics → FAQ
   - Mirrors how users naturally search for information

4. **Optimizes for SEO**
   - Uses natural language (not keyword-stuffed)
   - Follows proper heading hierarchy (H2 → H3)
   - Includes FAQ section (great for featured snippets)

### Reading the Strategic Insights

The **Strategic Insights** section explains:
- **Why this structure works** for SEO
- **What gaps** you're filling vs competitors
- **How comprehensive** the coverage is

**Example:**
> "This structure combines the technical depth of competitor A with the practical examples from competitor B, while adding a security considerations section that none of the top 10 results cover. The FAQ section addresses 5 common questions that appear in 'People Also Ask' boxes."

---

## How It Works (Technical)

For those interested in the technical details:

### Architecture

```
1. SERP Fetching
   └→ Uses Perplexity AI to query Google
   └→ Returns top 10 URLs with titles

2. Competitor Scraping
   └→ Fetches each competitor page
   └→ Extracts H1, H2, H3 headings
   └→ Handles failures gracefully

3. Pattern Analysis
   └→ Identifies common H2 topics (appear in 2+ competitors)
   └→ Identifies common H3 topics
   └→ Detects FAQ sections
   └→ Calculates average heading counts

4. AI Suggestion Generation
   └→ Claude AI analyzes all data
   └→ Generates optimal structure
   └→ Provides explanations for each section
   └→ Suggests FAQ questions
```

### APIs Used

- **Perplexity AI**: For fetching Google SERP results (bypasses scraping blocks)
- **BeautifulSoup**: For extracting headings from competitor pages
- **Claude Sonnet 4**: For analyzing patterns and generating suggestions

### Data Processing

The system:
- Processes pages **concurrently** (5 at a time) for speed
- **Caches** results during your session
- **Handles errors** gracefully (skips failed URLs)
- **Preserves** your selections if you refresh

---

## Best Practices

### Keyword Selection

✅ **Good Keywords:**
- "cloud storage solutions" (specific + commercial intent)
- "how CDN works" (informational + clear intent)
- "edge computing vs cloud computing" (comparison)

❌ **Poor Keywords:**
- "cloud" (too broad)
- "best cdn provider 2024 gcore" (too specific + branded)

### Competitor Selection

**Mix your competitors:**
- 1-2 direct competitors (AWS, Google Cloud, Azure)
- 1-2 authority sites (Wikipedia, tech blogs)
- 1-2 niche experts (specialized blogs, documentation)

**Avoid:**
- Selecting only Gcore competitors (you'll just copy their structure)
- Selecting more than 8 pages (diminishing returns)

### Editing Suggestions

**The AI suggestions are a starting point**, not gospel. Feel free to:
- Remove sections that don't fit Gcore's focus
- Add sections about Gcore-specific features
- Reorder sections for better flow
- Simplify overly complex structures

### When to Skip SERP Analysis

Skip if:
- You're an SEO expert and know exactly what you want
- You're updating existing content (use Content Optimization tab instead)
- Your topic is very niche (top 10 results may not be relevant)
- You're in a hurry and have a template ready

---

## Troubleshooting

### "Failed to fetch SERP results"

**Possible causes:**
- Perplexity API is down or rate-limited
- API key is invalid or expired
- Network connectivity issues

**Solutions:**
1. Wait 1-2 minutes and try again
2. Check your `.env` file has `PERPLEXITY_API_KEY` set
3. Try a different keyword (some keywords may be blocked)

### "Failed to scrape X URLs"

**This is normal!** Some websites block scraping.

**Common failures:**
- Cloudflare-protected sites
- Sites with aggressive bot detection
- Paywalled content

**What to do:**
- Don't worry if 1-3 URLs fail out of 10
- The AI will work with whatever data succeeded
- If ALL fail, try selecting different competitors

### "AI suggestion failed"

**Possible causes:**
- Claude API is down or rate-limited
- API key is invalid
- The extracted competitor data was insufficient

**Solutions:**
1. Check your `.env` file has `ANTHROPIC_API_KEY` set
2. Try selecting more competitors (need at least 2-3 successful scrapes)
3. Use manual brief as fallback

### Suggestions seem generic or off-topic

**Causes:**
- Keyword was too broad
- Competitors selected weren't relevant
- Not enough successful scrapes

**Solutions:**
- Try a more specific keyword
- Reselect competitors (choose more relevant ones)
- Use suggestions as inspiration, edit heavily in Step 1

### "No results found for my keyword"

**Possible causes:**
- Very niche keyword with few results
- Typo in keyword
- Perplexity couldn't find relevant results

**Solutions:**
- Try a broader keyword
- Check spelling
- Skip to manual brief

---

## Tips for VAs

### Your Workflow

1. **Get the keyword from your client**
   - Ask: "What's the main topic for this article?"

2. **Run SERP Analysis**
   - Takes 2-3 minutes total
   - No SEO knowledge needed

3. **Review AI suggestions**
   - Look for anything obviously wrong
   - Check that it makes sense for Gcore

4. **Use suggestions**
   - Click "Use These Suggestions"
   - Proceed to next steps

5. **If you see issues:**
   - Use "Edit Manually" instead
   - Remove/modify problematic sections in Step 1

### What to Look For

✅ **Good suggestions include:**
- Clear, readable headings (not keyword-stuffed)
- Logical flow (intro → details → advanced → FAQ)
- 5-8 main H2 sections
- 2-4 H3s under each H2
- FAQ section with 5-7 questions

❌ **Bad suggestions to fix:**
- Competitor mentions (AWS, Azure, etc.) - replace with "major providers"
- Off-topic sections
- Duplicate sections
- Overly technical jargon

---

## Advanced Usage

### For SEO Professionals

**The SERP Analysis tool doesn't replace SEO expertise**, but it speeds up research:

- **Keyword clustering**: Run analysis on multiple related keywords, combine insights
- **Content gap analysis**: Compare suggestions across different keywords
- **SERP feature analysis**: Note which competitors have FAQ sections (featured snippets)
- **Intent mapping**: Identify if top results are informational, commercial, or comparison

**Tip:** The raw competitor heading data is stored in session state if you need to inspect it manually.

### API Rate Limits

- **Perplexity**: 20 requests/minute on free tier, 60/minute on paid
- **Claude**: 50 requests/minute on most tiers

If hitting rate limits:
- Add delays between analyses
- Reduce number of competitors selected
- Upgrade API tier if needed

---

## FAQ

**Q: Does this guarantee my content will rank?**
A: No. SERP Analysis creates an SEO-optimized structure, but ranking depends on content quality, links, domain authority, and many other factors. This tool gives you a competitive starting point.

**Q: Can I analyze Gcore's own pages?**
A: Yes, but it's not recommended. You'd just be copying your existing structure. Better to analyze external competitors.

**Q: How often should I run SERP Analysis?**
A: Every time you create new content on a topic you're not familiar with. For topics you know well, you can skip it.

**Q: Will this show my competitors what I'm doing?**
A: No. The analysis is read-only. You're just viewing public competitor pages, not sending them any data.

**Q: Can I save SERP Analysis results?**
A: Results are stored in your session while you work. Once you apply them to Step 1, they're part of your content brief. The raw data isn't exported separately (yet).

**Q: What if I want to analyze more than 10 results?**
A: Currently limited to top 10. This covers 99% of use cases (most clicks go to top 5). If you need more, contact support.

**Q: Can I use this for languages other than English?**
A: The tool works with any language that Google and Perplexity support. However, AI suggestions are optimized for English SEO patterns.

---

## Support

If you encounter issues not covered in this guide:

1. Check the error message carefully
2. Try the troubleshooting steps above
3. Contact your team lead or Gcore support
4. Report bugs with:
   - Keyword used
   - Error message
   - Screenshot if possible

---

## Version History

**v1.0 (2025-09-30)**
- Initial release
- SERP fetching via Perplexity
- Competitor heading extraction
- AI-powered heading suggestions
- FAQ detection and generation

---

**Happy content creating! 🚀**