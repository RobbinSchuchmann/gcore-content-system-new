# Gcore Content Optimization System - Complete Guide

## Overview

The Gcore Content Optimization System is a comprehensive solution for updating and improving existing articles on the Gcore website. Built on top of the existing content generation system, it adds powerful optimization capabilities specifically designed to revitalize underperforming content from Gcore's 800+ article library.

**Latest Enhancements (v2.0)**:
- 🔧 New "Optimize" action for intelligent content preservation
- 📊 Automated quality scoring with action recommendations
- 🎯 Function-based content generation from section_functions.json
- 🔬 Selective research strategy (full/light/none)
- 💎 Smart preservation of valuable content elements
- 📈 Enhanced metrics and preservation tracking

## System Architecture

### Application

**Unified Content System** (`app.py`)
   - URL: http://localhost:8501
   - Purpose: Complete content management system
   - Dual-mode interface with two tabs:
     - **📝 New Content**: Create new content from scratch (5-step workflow)
     - **🔧 Content Optimization**: Update and optimize existing content (6-step workflow)
   - Features context-aware FAQ detection for automatic function selection

### Core Modules

#### Content Scraper (`core/content_scraper.py`)
- **Purpose**: Fetch and parse existing articles from URLs
- **Key Features**:
  - Automatic HTML extraction
  - Removes unwanted sections (related articles, newsletters, footers)
  - Accurate word count calculation (actual content only)
  - Primary keyword auto-detection from URL/title
  - Gcore-specific content parsing

#### Content Optimizer (`core/content_optimizer.py`)
- **Purpose**: Intelligently merge and optimize content with preservation
- **Key Features**:
  - Enhanced HTML/Markdown content parsing
  - Automated quality assessment with thresholds
  - **NEW: "Optimize" action** with aggressive preservation
  - Valuable elements extraction (statistics, examples, specs, quotes)
  - Multiple merge strategies (preserve_valuable, smart, replace)
  - Section-by-section preservation tracking
  - Integration with content generation functions
  - Word count and improvement score calculation

#### Gap Analyzer (`core/gap_analyzer.py`)
- **Purpose**: Identify content gaps and improvement opportunities
- **Key Features**:
  - Keyword gap detection and density analysis
  - Missing section suggestions based on content type
  - Content depth analysis (word count per section)
  - Semantic SEO improvements
  - Industry-specific term recognition for Gcore

#### Enhanced Content Editor (`core/content_editor.py`)
- **Purpose**: Visual comparison and quality improvements
- **Key Features**:
  - Side-by-side content comparison
  - Diff visualization with color coding
  - Readability improvement calculations
  - AI word detection and replacement
  - Optimization summary generation

## Content Optimization Workflow (6 Steps)

### Step 1: Import & Analyze Existing Content

#### Input Methods

1. **URL Scraping (Recommended)**
   - Enter article URL (e.g., `https://gcore.com/learning/what-is-cdn`)
   - Click "🔍 Fetch" button
   - System automatically:
     - Fetches HTML content
     - Removes related articles, newsletters, footer sections
     - Extracts title and meta description
     - Auto-detects primary keyword from URL/title
     - Calculates accurate word count (content only, not navigation)

2. **Manual Input (Fallback)**
   - Paste HTML or text content directly
   - Enter primary keyword manually

#### Content Analysis
- Click "Analyze Content Structure" to:
  - Parse HTML into structured format
  - Extract all headings (H1, H2, H3)
  - Map content sections to headings
  - Count words per section
  - Identify internal/external links
  - Extract images and media

#### Output
- Word count metric
- Heading count and structure visualization
- H1 title extraction
- Section count
- Structured heading tree with emojis:
  - 🔷 H1 headings
  - 🔹 H2 headings
  - ▪️ H3 headings

### Step 2: Gap Analysis & Content Planning

#### Enhanced Gap Analysis
- **Automated Quality Assessment**: Each section receives a quality score
- **Keyword Coverage Analysis**: 
  - Missing keywords detection
  - Keyword density optimization (target: 1-3%)
  - Keywords in headings check
- **Content Depth Analysis**: Word count per section metrics
- **Semantic SEO Improvements**: LSI keyword suggestions

#### Smart Heading Optimization Interface

**Visual Structure Display**:
- 🔷 H1 headings
- 🔹 H2 headings  
- ▪️ H3 headings

**For Each Heading**:
| Column | Function | Description |
|--------|----------|-------------|
| **Level** | Visual hierarchy | Shows heading level with emoji |
| **Heading** | Editable text | Modify heading wording inline |
| **Action** | Optimization strategy | Choose how to handle section |
| **Function** | Content pattern | Auto-detected generation function |
| **Quality** | Score display | Color-coded quality indicator |
| **Delete** | Remove option | Delete unnecessary headings |

#### Action Types (NEW)
- **✅ Keep** (Score > 80%): Minor cleaning only, preserves content
- **🔧 Optimize** (Score 60-80%): Preserves valuable elements while improving quality
- **🔄 Rewrite** (Score < 60%): Complete regeneration with smart preservation
- **✨ New**: Add missing sections
- **❌ Remove**: Delete unnecessary content

#### Content Generation Functions
Automatically detected and assignable functions from `section_functions.json`:
- `generate_definition`: What is X? explanations
- `generate_listicle`: Lists and bullet points
- `generate_how`: Process explanations
- `generate_how_list`: Step-by-step instructions
- `generate_yes_no_answer`: Direct yes/no responses
- `generate_evaluation_bridge`: Criteria before CTAs
- `generate_gcore_service`: Product CTAs
- And more...

#### Intelligent Suggestions
**Gap-Based Recommendations**:
- Missing sections with pre-selected functions
- Priority ranking based on content type
- One-click addition with proper function assignment
- Automatic heading level detection

### Step 3: Targeted Research Enhancement

#### Selective Research Strategy (NEW)
**Research Scope Visualization**:
- 🔬 **Full Research**: Sections marked for rewrite or new
- 🔍 **Light Research**: Sections marked for optimization (gap-filling)
- ✅ **No Research**: Sections marked to keep (preserves existing data)

#### Research Configuration
- **Research Focus Options**:
  - Balanced approach
  - Technical details emphasis
  - Statistics & data priority
  - Use cases focus
- **Additional Context**: Custom research guidance
- **API Selection**: Toggle Perplexity API on/off

#### Smart Research Execution
**Automatic Research Planning**:
1. Identifies sections needing research
2. Differentiates between full and light research needs
3. Builds targeted research queries
4. Limits to 10 topics for efficiency
5. Shows research summary upon completion

#### Research Data Display
- **Metrics Dashboard**:
  - Facts found count
  - Statistics discovered
  - Sources collected
- **Preview Results**: Expandable view of key findings
- **Preservation of Existing Data**: Kept sections retain original research

### Step 4: Smart Content Optimization

#### Optimization Plan Summary
**Action Metrics Display**:
- Real-time count of Keep, Optimize, Rewrite, New, Remove actions
- Visual summary of optimization strategy
- Total sections and word count tracking

#### Optimization Settings
- **Preservation Strategy**:
  - Aggressive: Maximum content preservation
  - Balanced: Smart preservation (default)
  - Minimal: Limited preservation
- **Gcore Context**: Toggle product mentions and metrics

#### Enhanced Content Processing (NEW)

1. **✅ "Keep" Action** (Score > 80%):
   - AI word removal (40+ blacklisted terms)
   - Sentence length optimization
   - Promotional language cleanup
   - Minimal structural changes

2. **🔧 "Optimize" Action** (Score 60-80%) **[NEW]**:
   - Preserves ALL valuable elements:
     - Statistics and data points
     - Examples and case studies
     - Technical specifications
     - Quotes and definitions
   - Generates improved structure
   - Applies selected content function
   - Smart merge with preservation

3. **🔄 "Rewrite" Action** (Score < 60%):
   - Complete content regeneration
   - Selective preservation (top 3-5 elements)
   - Full function application
   - Research data integration

4. **✨ "New" Action**:
   - Fresh content generation
   - Function-based patterns
   - Research-driven content
   - Keyword optimization

#### Intelligent Preservation System

**Valuable Elements Extraction**:
- **Statistics**: Numbers, percentages, metrics
- **Examples**: "For example", "such as", case studies
- **Technical Specs**: APIs, protocols, specifications
- **Quotes**: Direct quotations
- **Definitions**: "X is...", "refers to..."

**Merge Strategies**:
- `preserve_valuable`: Aggressive preservation for optimize action
- `smart`: Selective preservation for rewrites
- `replace`: Complete replacement
- `append`: Add to existing

#### Optimization Results Dashboard
- **Metrics**:
  - Total sections optimized
  - Improvement score percentage
  - Total word count
  - Elements preserved count
- **Preservation Summary Table**:
  - Section-by-section preservation metrics
  - Statistics, examples, technical specs preserved
- **Content Preview**: First 5 sections with action indicators

### Step 5: Quality Comparison

#### Before/After Analysis

**Metrics Tracked**:
- Overall quality score (0-100)
- Word count change
- AI words removed
- Readability improvement
- SEO optimization score
- Gcore compliance score

#### Visual Comparison

1. **Side-by-Side View**:
   - Left panel: Original content (issues highlighted in red)
   - Right panel: Optimized content (improvements in green)

2. **Diff View**:
   - Added content (green background)
   - Removed content (red background)
   - Modified content (yellow background)

3. **Change Summary**:
   - Sections kept/rewritten/added/removed
   - Total improvements percentage
   - Quality score delta

#### Quality Checks
- **AI Word Detection**: 40+ blacklisted terms
- **SEO Validation**:
  - Keyword density (target: 1-3%)
  - Heading keyword presence
  - Meta description optimization
- **Readability**:
  - Sentence length (< 30 words)
  - Paragraph length (< 5 sentences)
  - Reading level assessment
- **Gcore Compliance**:
  - Brand terminology
  - Product mentions
  - Technical accuracy

### Step 6: Export & Tracking

#### Export Formats
1. **Markdown**: Clean markdown with proper formatting
2. **HTML**: Production-ready HTML with structure
3. **Change Report**: Detailed optimization report
4. **JSON**: Structured data for CMS integration
5. **Plain Text**: Simple text format

#### Optimization Report Contents
- **Summary Section**:
  - Original vs optimized word count
  - Quality improvement percentage
  - Keywords added/optimized
  - Sections modified

- **Detailed Changes**:
  - Section-by-section modifications
  - Change rationale for each section
  - Quality scores per section
  - Specific improvements made

- **Recommendations**:
  - Future optimization suggestions
  - Internal linking opportunities
  - Content refresh schedule
  - Performance monitoring metrics

#### Version Tracking
- Original content backup
- Optimization timestamp
- Change history log
- Performance baseline for tracking

## Enhanced Workflow Benefits (v2.0)

### SEO Specialist Control
- **Visual Heading Management**: See all headings with quality scores at a glance
- **Inline Editing**: Modify heading text without leaving the interface
- **Function Selection**: Choose specific content patterns per heading
- **Action Recommendations**: Automatic suggestions based on quality scores
- **One-Click Additions**: Add suggested sections with proper functions

### Intelligent Preservation Strategy
- **Granular Control**: Four action types instead of three
- **Smart Detection**: Automatically identifies valuable content elements
- **Preservation Metrics**: Track what's being kept vs regenerated
- **Quality Thresholds**: Automatic action assignment based on scores

### Cost-Effective Optimization
- **Selective Research**: Only research sections that need it
- **API Efficiency**: Reduced calls through smart preservation
- **Batch Processing**: Handle multiple sections efficiently
- **Demo Mode**: Test workflow without API keys

## Key Features & Capabilities

### Intelligent Content Preservation
- **What's Preserved**:
  - High-quality sections (score > 70%)
  - Accurate statistics and data
  - Specific examples and case studies
  - Technical specifications
  - Unique insights and quotes

- **What's Replaced**:
  - AI-generated fluff
  - Outdated information
  - Generic content
  - Over-promotional language
  - Poor quality sections

### Automated Improvements
- **AI Word Replacement**: 40+ terms automatically replaced
- **Sentence Splitting**: Long sentences broken at natural points
- **Promotional Removal**: Marketing language cleaned
- **Structure Enhancement**: Missing sections added
- **Keyword Optimization**: Density and placement improved

### Gcore-Specific Optimizations
- **Product Integration**: Mentions of Gcore services where relevant
- **Technical Accuracy**: CDN, Edge, Cloud terminology
- **Brand Compliance**: Consistent messaging
- **Industry Terms**: 50+ Gcore-specific terms recognized
- **Value Propositions**: Why Gcore sections for suitable content

## Technical Implementation

### Dependencies
```python
# Web scraping
beautifulsoup4
requests

# AI APIs
anthropic  # Claude API for content generation
perplexity  # Research and fact-checking

# Framework
streamlit  # Web interface

# NLP & Text Processing
difflib  # Content comparison
re  # Pattern matching
```

### Configuration Files
- `.env`: API keys (ANTHROPIC_API_KEY, PERPLEXITY_API_KEY)
- `data/ai_blacklist.txt`: AI words to remove
- `data/brand_guidelines.json`: Gcore brand requirements
- `data/section_functions.json`: Content generation functions
- `data/gcore_products.json`: Product information

### API Integration
1. **Claude API (Anthropic)**:
   - Model: Claude-3-sonnet
   - Used for content generation
   - Pattern-based prompting
   - Temperature: 0.7 for creativity

2. **Perplexity API**:
   - Used for research
   - Real-time data gathering
   - Source extraction
   - Fact verification

## Usage Guide

### Starting the System

1. **Activate Virtual Environment**:
```bash
cd gcore-content-system
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
pip install beautifulsoup4 requests
```

3. **Launch Application**:
```bash
streamlit run app.py
```

4. **Access Interface**:
Open browser to http://localhost:8501

### Workflow Example

1. **Select Content for Optimization**:
   - Use analytics to identify underperforming articles
   - Articles with < 100 monthly visits
   - Outdated content (> 1 year old)
   - Low engagement metrics

2. **Import Article**:
   - Copy URL from Gcore website
   - Paste in URL field
   - Click "Fetch" to import

3. **Add Target Keywords**:
   - Research high-value keywords
   - Add 3-5 related keywords
   - Include long-tail variations

4. **Review Gap Analysis**:
   - Check coverage score (target > 80%)
   - Review suggested sections
   - Note missing keywords

5. **Configure Optimization**:
   - Mark high-quality sections (>80%) as "keep"
   - Mark good sections (60-80%) as "optimize" for preservation
   - Mark poor sections (<60%) as "rewrite"
   - Add suggested new sections with auto-detected functions
   - Remove irrelevant or duplicate content

6. **Execute Optimization**:
   - Let system research gaps
   - Generate new content
   - Review quality metrics

7. **Export & Publish**:
   - Export optimized content
   - Review in CMS
   - Publish with tracking

### Best Practices

#### Content Selection
- **High Priority**: Articles with good potential but low performance
- **Medium Priority**: Outdated evergreen content
- **Low Priority**: News or time-sensitive content

#### Keyword Strategy
- **Primary Keyword**: Main topic, highest search volume
- **Secondary Keywords**: 3-5 related terms
- **Long-tail Keywords**: Specific variations
- **Semantic Keywords**: Related concepts

#### Quality Thresholds
- **Minimum Quality Score**: 70/100
- **Keyword Density**: 1-3%
- **Readability Level**: Grade 8-10
- **Word Count**: 1,500-3,000 words

#### Optimization Frequency
- **Monthly**: High-traffic pages
- **Quarterly**: Medium-traffic pages
- **Annually**: Low-traffic evergreen content

## Performance Metrics

### Success Indicators
- **Quality Score Improvement**: Target +20 points
- **Keyword Coverage**: Target 80%+
- **Readability Improvement**: Target +15%
- **Content Depth**: 150+ words per section

### Tracking Metrics
- **Before Optimization**:
  - Current traffic
  - Engagement rate
  - Ranking positions
  - Quality score

- **After Optimization**:
  - Traffic change %
  - Engagement improvement
  - Ranking improvements
  - Quality score delta

## Future Enhancements

### Planned Features
1. **Internal Linking Suggestions**:
   - Automatic link opportunities detection
   - Sitemap integration
   - Product page prioritization
   - Learning article cross-linking

2. **Batch Processing**:
   - Multiple article optimization
   - Queue management
   - Parallel processing
   - Bulk export

3. **Performance Tracking**:
   - Analytics integration
   - Automated reporting
   - ROI calculation
   - A/B testing support

4. **AI Improvements**:
   - Custom model fine-tuning
   - Industry-specific training
   - Competitive analysis
   - Trend prediction

## Troubleshooting

### Common Issues

1. **Fetch Button Not Working**:
   - Check URL format (needs https://)
   - Verify site is accessible
   - Check console for errors

2. **Analyze Button Not Responding**:
   - Ensure content is loaded
   - Verify primary keyword is set
   - Check for HTML parsing errors

3. **High Word Count**:
   - Related articles not removed
   - Check scraper configuration
   - Verify stop sections list

4. **Quality Score Low**:
   - Too many AI words
   - Poor readability
   - Missing keywords
   - Run quality fixes

### Debug Mode
Add to see detailed logs:
```python
import streamlit as st
st.set_option('client.showErrorDetails', True)
```

## Quick Reference: Action Types

| Action | Score Range | Icon | Description | Preservation |
|--------|------------|------|-------------|--------------|
| **Keep** | > 80% | ✅ | High quality, minor cleaning | Full content |
| **Optimize** | 60-80% | 🔧 | Good quality, needs improvement | All valuable elements |
| **Rewrite** | < 60% | 🔄 | Poor quality, regenerate | Top 3-5 elements |
| **New** | N/A | ✨ | Missing section | N/A |
| **Remove** | N/A | ❌ | Unnecessary content | None |

## Quick Reference: Content Functions

| Function | Use Case | Example Heading |
|----------|----------|-----------------|
| `generate_definition` | What is X? | What is CDN caching? |
| `generate_listicle` | Lists and benefits | Benefits of edge computing |
| `generate_how` | Process explanation | How does load balancing work? |
| `generate_how_list` | Step-by-step guide | How to configure CDN |
| `generate_yes_no_answer` | Direct answers | Is CDN necessary? |
| `generate_evaluation_bridge` | Criteria lists | How to choose a provider |
| `generate_gcore_service` | Product CTAs | Why choose Gcore |

## Conclusion

The Gcore Content Optimization System v2.0 provides a comprehensive solution for revitalizing existing content with unprecedented control and intelligence. By combining smart content preservation with function-based generation and selective research, it enables efficient optimization at scale while maintaining quality and brand consistency. 

The new "Optimize" action and preservation system ensure valuable content is never lost, while the integration with content generation functions guarantees consistent, high-quality output. The system is designed to handle the specific needs of Gcore's content library, from technical articles to product descriptions, ensuring each piece of content performs at its best while minimizing API costs and maximizing efficiency.