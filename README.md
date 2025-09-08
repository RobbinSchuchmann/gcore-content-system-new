# Gcore Content Generation System

A Streamlit-based content generation system that follows Koray Tuğberk GÜBÜR's semantic SEO methodology, specifically designed for Gcore's content needs.

## Features

- **Semantic Pattern Detection**: Automatically detects question patterns (definition, list, how-to, etc.)
- **Perplexity Research Integration**: Gather comprehensive research before content generation
- **Claude Content Generation**: Generate high-quality content following semantic SEO principles
- **Quality Checking**: Detect AI words, check Gcore compliance, SEO optimization
- **Multi-format Export**: Export to Markdown, HTML, Plain Text, JSON

## Setup

### 1. Create Virtual Environment

```bash
cd gcore-content-system
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `PERPLEXITY_API_KEY`: Your Perplexity API key

### 4. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Workflow

### Step 1: Content Brief
- Enter your primary keyword/topic
- Build heading structure (H1, H2, H3)
- System auto-detects pattern types for each heading

### Step 2: Research
- Click "Start Perplexity Research" to gather information
- Review facts, statistics, and sources
- Research is cached for the session

### Step 3: Generate Content
- Generate all sections at once or section-by-section
- Adjust creativity level with temperature slider
- Content follows semantic patterns automatically

### Step 4: Quality Check
- Automatic detection of AI-sounding words
- Gcore brand compliance scoring
- SEO optimization metrics
- One-click AI word replacement

### Step 5: Export
- Choose export format (Markdown, HTML, Text, JSON)
- Content automatically saved to library
- Download for further editing

## Content Patterns

The system recognizes and applies these semantic patterns:

- **Definition (Singular)**: "What is X?" → Direct definition + expansion
- **Definition (Plural)**: "What are X?" → List with bold terms
- **How-to**: "How to X?" → Step-by-step instructions
- **Process**: "How does X work?" → Mechanism explanation
- **Yes/No**: "Is/Can/Does X?" → Yes/No + explanation
- **Why/When/Where/Who**: Direct answer + context

## Customization

### Brand Guidelines
Edit `data/brand_guidelines.json` to customize:
- Writing style rules
- Preferred terminology
- Content guidelines

### AI Blacklist
Edit `data/ai_blacklist.txt` to add/remove AI words to detect

### Product Information
Edit `data/gcore_products.json` to update Gcore product details

## File Structure

```
gcore-content-system/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── core/
│   ├── content_generator.py  # Claude API integration
│   ├── research_engine.py    # Perplexity API integration
│   ├── quality_checker.py    # Content quality validation
│   └── semantic_patterns.py  # Pattern detection & templates
├── data/
│   ├── ai_blacklist.txt      # AI words to avoid
│   ├── brand_guidelines.json # Gcore brand guidelines
│   ├── gcore_products.json   # Product information
│   └── saved_content/        # Generated content storage
└── templates/
    └── prompts.py            # Generation prompt templates
```

## Tips

1. **Better Research**: Be specific with your primary keyword for more relevant research
2. **Heading Structure**: Follow question format for better pattern detection
3. **Quality Scores**: Aim for 80%+ on all quality metrics
4. **Regeneration**: Use section regeneration for specific improvements
5. **Export Format**: Use Markdown for easy editing, HTML for web publishing

## Troubleshooting

- **API Key Errors**: Ensure your `.env` file has valid API keys
- **Generation Fails**: Check your internet connection and API limits
- **Pattern Detection**: Use standard question formats for best results
- **Export Issues**: Ensure `data/saved_content/` directory exists

## Support

For issues or questions, please refer to the main Gcore project documentation.