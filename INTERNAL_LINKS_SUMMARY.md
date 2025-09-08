# Internal Linking System - Complete Summary

## Overview
The internal linking system automatically suggests and adds relevant Gcore product pages and learning content links to articles, following SOP requirements for natural anchor text placement.

## Current Status ✅
- **System Implemented**: Full internal linking infrastructure is built
- **Relevance Threshold**: Set to 0.35 (lowered from 0.7 for better matching)
- **Link Database**: 1,697+ links indexed (59 product pages, 1,638 learning pages)
- **SOP Compliant**: Exact anchor text matching, mid-paragraph placement

## How to Add Internal Links

### Method 1: During New Content Generation (Automatic)
1. Go to **Step 3: Generate Content** in the Streamlit app
2. Enable **"Internal Link Suggestions"** checkbox (on by default)
3. Generate content normally - links will be suggested and included automatically
4. View suggested links in the content preview under each section

### Method 2: For Existing Content (Manual)
Use the simple product links script for best results:

```bash
cd gcore-content-system
python3 add_product_links.py data/saved_content/your_article.md
```

This adds relevant product page links based on keyword matching.

## Key Product Pages Available for Linking

| URL | Trigger Keywords | Suggested Anchor Text |
|-----|-----------------|----------------------|
| `/cloud` | cloud, cloud computing, cloud platform | "cloud platform", "cloud infrastructure" |
| `/cloud/secure-cloud-computing` | cloud security, secure cloud | "secure cloud computing" |
| `/ddos-protection` | ddos, ddos protection, ddos attack | "DDoS protection" |
| `/cloud/managed-kubernetes` | kubernetes, k8s, container | "managed Kubernetes" |
| `/cloud/load-balancers` | load balancer, load balancing | "load balancers" |
| `/cdn` | cdn, content delivery | "CDN solution" |
| `/dns` | dns, domain name system | "DNS hosting" |
| `/cloud/managed-database-postgresql` | database, postgresql | "managed database" |

## Known Issues & Solutions

### Issue 1: No Links Being Added During Generation
**Cause**: The `generate_section` method wasn't passing the `include_internal_links` parameter  
**Status**: ✅ FIXED - Parameter now properly passed through

### Issue 2: Links Not Matching Content
**Cause**: Relevance threshold was too high (0.7)  
**Status**: ✅ FIXED - Lowered to 0.35 for better matching

### Issue 3: Malformed Learning URLs
**Cause**: Learning URLs in sitemap include full URLs instead of slugs  
**Status**: ⚠️ WORKAROUND - Use product links script which focuses on clean product URLs

### Issue 4: Poor Anchor Text Selection
**Cause**: System selecting single words like "in", "best", "how"  
**Status**: ✅ FIXED - Product links script uses proper multi-word anchors

## File Structure

```
gcore-content-system/
├── core/
│   ├── link_manager.py          # Link database management
│   ├── internal_linker.py       # Link suggestion & placement logic
│   └── content_generator.py     # Updated to include links during generation
├── data/
│   └── gcore/
│       └── sitemap.csv          # Product pages source
├── add_product_links.py         # Script to add links to existing content
├── add_internal_links.py        # Advanced script with learning links
└── test_internal_links.py       # Testing script
```

## SOP Compliance Features

✅ **Exact Match Anchor Text**: Links use the exact text found in content  
✅ **Mid-Paragraph Placement**: Links avoid beginning of paragraphs  
✅ **Natural Flow**: Anchor text flows naturally within sentences  
✅ **Link Density**: Maintains 100+ words between links  
✅ **Relevance**: Only suggests topically relevant links  

## Quick Commands Reference

```bash
# Add product links to existing article
python3 add_product_links.py input.md output.md

# Test the internal linking system
python3 test_internal_links.py

# Run Streamlit app with internal links enabled
streamlit run app.py
# Then check "Enable Internal Link Suggestions" in Step 3

# Debug link relevance for specific content
python3 test_link_relevance.py
```

## Best Practices

1. **For Cloud/Security Content**: Use product links script for best results
2. **Link Count**: Aim for 3-7 internal links per article
3. **Anchor Text**: Use descriptive multi-word phrases, not single words
4. **Placement**: Ensure links appear naturally within sentence flow
5. **Diversity**: Link to different product pages, not just one repeatedly

## Configuration

To adjust the system behavior, modify these settings:

```python
# In core/internal_linker.py
self.min_relevance_score = 0.35  # Lower for more suggestions
self.max_links_per_section = 3   # Maximum links per section
self.min_words_between_links = 100  # Spacing between links
```

## Testing Your Content

To test if your content will get good link suggestions:

```python
# Check what links would be suggested for your content
from core.link_manager import LinkManager
from core.internal_linker import InternalLinker

link_manager = LinkManager()
linker = InternalLinker(link_manager)

suggestions = linker.suggest_links_for_content(
    "Your content here...",
    "Your Heading",
    max_links=5
)

for link, anchor, score in suggestions:
    print(f"{anchor} -> {link.url} (score: {score:.2f})")
```

## Next Steps & Improvements

### Immediate Actions Needed:
1. ✅ Use `add_product_links.py` for existing content
2. ✅ Enable internal links checkbox when generating new content

### Future Enhancements:
1. Fix learning topic URLs to use proper slugs
2. Create UI for manually selecting links during generation
3. Add link effectiveness tracking
4. Build link suggestion API endpoint
5. Implement A/B testing for link placement strategies

## Support & Troubleshooting

If links aren't being added:
1. Check relevance threshold (should be 0.35)
2. Verify content contains product-related keywords
3. Ensure sitemap.csv exists in data/gcore/
4. Use product links script as fallback
5. Manually add links using markdown syntax: `[anchor text](/url)`

## Summary

**Current State**: The internal linking system is functional but requires the `add_product_links.py` script for best results with existing content. New content generation will include links automatically when enabled.

**Recommended Approach**: Use the product links script for reliable, SOP-compliant internal linking to Gcore product pages.