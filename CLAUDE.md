# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit-based content generation and optimization system specifically designed for Gcore's content needs. The system implements semantic SEO methodology and provides two main workflows:

- **New Content Creation**: 5-step workflow for generating content from scratch
- **Content Optimization**: 6-step workflow for improving existing content

⚠️ **IMPORTANT**: Use ONLY `app.py` as the main application file. This unified app contains both content creation and optimization tabs. Do not create separate app files.

## Commands

### Python/Streamlit Development
```bash
cd gcore-content-system
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py       # Start application on http://localhost:8501
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
- `ANTHROPIC_API_KEY` - Claude API for content generation
- `PERPLEXITY_API_KEY` - Research and information gathering

## Architecture

### Core Application Structure
- **`app.py`** - Main Streamlit application with tab-based interface
  - Tab 1: New Content (5-step workflow)
  - Tab 2: Content Optimization (6-step workflow)
- **`config.py`** - Central configuration with API keys, model settings, and Gcore-specific data
- **`core/`** - Core functionality modules:
  - `content_generator.py` - Claude API integration for content generation
  - `content_optimizer.py` - Content optimization and preservation logic
  - `content_scraper.py` - Web scraping for existing content analysis
  - `research_engine.py` - Perplexity API integration for research
  - `quality_checker.py` - Content quality validation and AI word detection
  - `semantic_patterns.py` - Pattern detection and content templates
  - `gap_analyzer.py` - Content gap analysis for optimization
  - `content_editor.py` - Content editing and refinement
- **`templates/prompts.py`** - Prompt templates for different content patterns
- **`data/`** - Configuration and reference data:
  - `brand_guidelines.json` - Gcore writing style and terminology rules
  - `ai_blacklist.txt` - AI words to detect and avoid
  - `gcore_products.json` - Product information for context
  - `section_functions.json` - Content section type definitions
  - `saved_content/` - Generated content storage

### Key Dependencies
- **Streamlit**: 1.40.2 for web interface
- **Anthropic**: 0.40.0 for Claude API integration
- **Python-dotenv**: Environment variable management
- **Requests**: HTTP requests for API calls
- **Pandas**: Data manipulation
- **Plotly**: Visualization and charts
- **Python-docx**: Document export capabilities

## Content Workflows

### New Content Tab (5-step process):
1. **Content Brief**: Define topic structure with H1/H2/H3 headings
2. **Research**: Gather facts and data via Perplexity API
3. **Generate**: Create content using Claude with semantic patterns
4. **Quality Check**: Validate against AI words, SEO, and Gcore compliance
5. **Export**: Multiple formats (Markdown, HTML, JSON, DOCX)

### Content Optimization Tab (6-step process):
1. **Import & Analyze**: Fetch existing content from URL or HTML input
2. **Gap Analysis**: Identify missing sections, keywords, and improvements
3. **Research Enhancement**: Targeted research for identified gaps
4. **Smart Optimization**: Preserve valuable content while improving quality
5. **Quality Comparison**: Before/after analysis with metrics
6. **Export & Tracking**: Export optimized content with change tracking

## Semantic Pattern System

The system automatically detects content patterns and applies appropriate templates:

- **Definition (Singular)**: "What is X?" → Direct definition format
- **Definition (Plural)**: "What are X?" → List with bold terms
- **How-to**: "How to X?" → Step-by-step instructions
- **Process**: "How does X work?" → Mechanism explanation
- **Yes/No**: "Is/Can/Does X?" → Yes/No + detailed explanation
- **FAQ Detection**: Auto-detects FAQ sections and applies Q&A format

## Model Configuration

- **Claude Model**: `claude-sonnet-4-20250514` (latest Sonnet 4)
- **Default Temperature**: 0.4 (balanced for factual yet natural content)
- **Max Tokens**: 4000
- **Perplexity Model**: `sonar` for research queries

## Gcore-Specific Context

The system includes comprehensive Gcore information:
- **Global Reach**: 180+ Points of Presence
- **Performance**: 30ms average latency
- **Services**: CDN, Edge Cloud, AI Infrastructure
- **Brand Guidelines**: Formal but approachable tone, specific terminology preferences
- **Quality Standards**: 80%+ Gcore compliance, max 3 AI words, 75%+ SEO score

## Quality Validation

Content is validated against multiple criteria:
- **AI Word Detection**: Identifies and flags AI-sounding language
- **Gcore Compliance**: Checks adherence to brand guidelines
- **SEO Optimization**: Validates keyword density and structure
- **Readability**: Ensures appropriate sentence/paragraph length
- **Technical Accuracy**: Validates technical claims and metrics

## Export Capabilities

Multiple export formats supported:
- **Markdown**: `.md` for easy editing
- **HTML**: `.html` for web publishing
- **Plain Text**: `.txt` for basic use
- **JSON**: `.json` for structured data
- **Word Document**: `.docx` for collaborative editing

## Development Guidelines

- All content generation uses semantic SEO principles
- Maintain Gcore brand voice and terminology
- Validate API keys before content operations
- Cache research data during sessions for efficiency
- Use pattern-specific prompts for consistent output
- Implement quality checks before content export
- Save generated content with metadata for tracking

## File Storage Structure

Generated content is automatically saved to `data/saved_content/` with:
- Content files in various formats
- Metadata files with generation parameters
- Quality metrics and compliance scores
- Research data and sources used
- remember to always push changes to the gcore-content-system-new git