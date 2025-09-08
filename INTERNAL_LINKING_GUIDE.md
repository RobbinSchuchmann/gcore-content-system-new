# Internal Linking System Guide

## Overview
The internal linking system automatically suggests and integrates relevant Gcore product pages and learning content links into generated articles, following SOP requirements for anchor text placement and relevance.

## Components

### 1. Link Manager (`core/link_manager.py`)
- **Purpose**: Manages the database of internal links
- **Data Sources**:
  - Product pages from `data/gcore/sitemap.csv`
  - Learning content from `gcore_learning_topics.txt`
- **Features**:
  - Categorizes links (product services, solutions, features, learning)
  - Keywords and relevance scoring
  - Fast lookup by category or keyword

### 2. Internal Linker (`core/internal_linker.py`)
- **Purpose**: Intelligent link suggestion and placement
- **Features**:
  - Relevance scoring algorithm (0.0-1.0 scale)
  - Natural anchor text detection
  - SOP-compliant placement (mid-paragraph, exact match)
  - Link validation

### 3. Content Generator Integration
- **Automatic Integration**: Links are suggested during content generation
- **Configurable**: Can be enabled/disabled per generation
- **Smart Prompting**: Links are included in generation prompts for natural placement

## How It Works

### During Content Generation:
1. **Analysis**: System analyzes the heading and research data
2. **Matching**: Finds relevant product/learning pages based on keywords
3. **Scoring**: Calculates relevance scores for each potential link
4. **Selection**: Chooses top 3 most relevant links per section
5. **Integration**: Includes links in generation prompt for natural placement

### SOP Compliance:
- ✅ Exact match anchor text
- ✅ Mid-paragraph placement (not at beginning)
- ✅ Natural sentence integration
- ✅ Relevant to content topic
- ✅ Balanced distribution (not clustered)

## Configuration

### Enable/Disable in Streamlit App:
```python
# In Step 3: Generate Content
enable_internal_links = st.checkbox(
    "Enable Internal Link Suggestions", 
    value=True
)
```

### Programmatic Usage:
```python
from core.content_generator import ContentGenerator

# Enable internal links
generator = ContentGenerator(enable_internal_links=True)

# Generate with links
result = generator.generate_content(
    heading="What is a CDN?",
    pattern_type="definition",
    research_data=research,
    context=context,
    include_internal_links=True
)

# Access suggested links
if result.get('internal_links'):
    for link in result['internal_links']:
        print(f"{link['anchor_text']} -> {link['url']}")
```

## Link Categories

### Product Pages (High Priority):
- **Services**: `/cdn`, `/cloud`, `/ddos-protection`, `/dns`, `/hosting`
- **Solutions**: `/cdn/gaming`, `/cloud/financial-services`, `/edge-network`
- **Features**: `/cloud/load-balancers`, `/cloud/managed-kubernetes`

### Learning Content (Medium Priority):
- **Tutorials**: `/learning/configure-*`, `/learning/setup-*`
- **Concepts**: `/learning/what-is-*`, `/learning/*-explained`
- **Guides**: `/learning/*-guide`, `/learning/best-practices-*`

## Quality Metrics

The system tracks:
- **Total Links**: Number of links in database
- **Relevance Scores**: How well links match content
- **Link Distribution**: Links per section
- **Validation Status**: SOP compliance checking

## Testing

Run the test suite:
```bash
cd gcore-content-system
source venv/bin/activate
python test_internal_links.py
```

## Customization

### Adjust Relevance Threshold:
```python
internal_linker.min_relevance_score = 0.8  # Default: 0.7
```

### Change Link Density:
```python
internal_linker.max_links_per_section = 5  # Default: 3
internal_linker.min_words_between_links = 150  # Default: 100
```

### Add Custom Keywords:
Update `PRODUCT_KEYWORDS` in `link_manager.py` to improve matching for specific products.

## Best Practices

1. **Review Suggestions**: Always review suggested links for relevance
2. **Natural Flow**: Ensure anchor text flows naturally in sentences
3. **Avoid Over-Linking**: 3-7 links per article is optimal
4. **Update Regularly**: Keep sitemap and learning topics current
5. **Test Placement**: Use the validation function to check SOP compliance

## Troubleshooting

### No Links Suggested:
- Check if content has enough keywords matching the database
- Verify sitemap.csv and learning topics files exist
- Lower the relevance threshold if needed

### Links Not Natural:
- Review anchor text suggestions
- Adjust the content to naturally include product mentions
- Use manual placement for complex cases

### Performance Issues:
- Database loads once on initialization
- ~1700 links indexed for fast lookup
- Keyword index enables O(1) lookups