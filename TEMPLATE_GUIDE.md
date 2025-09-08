# Content Template System Guide

## Quick Start

The template system allows you to quickly set up and test content generation with predefined structures.

## Using the Cloud Storage Template

1. **Start the app**: `streamlit run app.py`
2. **In Step 1 (Content Brief)**:
   - Look for "Select Content Template" dropdown
   - Choose "Cloud Storage (Standard Test Template)"
   - Click "Load Template"
   - The entire structure will be loaded automatically

3. **The Cloud Storage Template includes**:
   - Primary keyword: "cloud storage"
   - 9 optimized headings with appropriate functions:
     - What is cloud storage? (Definition)
     - How does cloud storage work? (How Process)
     - What are the main types of cloud storage? (Listicle)
     - What are the different cloud storage deployment models? (Listicle)
     - What are the key benefits of cloud storage? (Listicle)
     - What are common cloud storage use cases? (Listicle)
     - How secure is cloud storage? (How with Statistics)
     - How to choose the right cloud storage solution? (How-to Steps)
     - Gcore cloud storage solutions (Gcore Service Section)

4. **Continue through the workflow**:
   - Step 2: Research (will gather comprehensive data)
   - Step 3: Generate (creates content for each section)
   - Step 4: Quality Check (reviews and improves content)
   - Step 5: Export (includes sources and references)

## Features Added

### 1. Template System
- Load predefined content structures instantly
- Save your own templates for reuse
- Templates include heading structure, functions, and settings

### 2. Improved Research
- **Topic-specific queries**: Different research approaches for technical vs how-to content
- **Better extraction**: Full statistics without truncation
- **Quality scoring**: 0-100 score with rating (Excellent/Good/Fair/Poor)
- **Coverage gap detection**: Identifies missing research areas
- **More data used**: 6-8 facts, 5-6 statistics per section (vs 3-5 before)

### 3. Source References
All exported content now includes:
- Research quality score
- Key facts referenced (top 10)
- Statistics and metrics used (top 10)
- Source URLs when available

## Available Templates

1. **Cloud Storage (Standard Test Template)** - Complete 9-section structure for cloud storage content
2. **CDN Comprehensive Guide** - Full CDN content structure
3. **Edge Computing Guide** - Edge computing educational content
4. **Simple Test** - Quick 3-heading test structure

## Creating Your Own Templates

1. Build your content structure in Step 1
2. In the right column, find "Save Template"
3. Enter a template name and description
4. Click "Save as Template"
5. Your template will be available for future use

## Testing Consistency

Use the cloud storage template to test content generation consistency:

```bash
# Run the test script
python test_cloud_storage_template.py

# Results saved to:
# - data/template_tests/cloud_storage_test_[timestamp].json
# - data/template_tests/cloud_storage_test_[timestamp].html
```

## What's Improved

1. **No more truncated statistics** - Full sentences preserved
2. **Better research prompts** - Structured output with 7 sections
3. **Pattern-specific research** - Different data for different content types
4. **Source attribution** - All research data tracked and referenced
5. **Quality validation** - Know if research is comprehensive enough

## Workflow Summary

```
Load Template → Research (Enhanced) → Generate (More Data) → Quality Check → Export (With Sources)
```

The system now provides:
- More comprehensive research
- Better data integration
- Full source attribution
- Consistent testing baseline

Use the cloud storage template as your standard test to ensure output quality remains consistent across updates.