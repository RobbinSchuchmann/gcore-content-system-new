# Testing Instructions - Citation Fix Verification

## Quick Test via Running Streamlit App

The Streamlit server is running at: **http://localhost:8501**

### Test Steps:

1. **Open the app** in your browser: http://localhost:8501

2. **Go to "New Content" tab**

3. **Enter the following test data:**
   - **Primary Keyword:** `cloud computing`
   - **H1 Heading:** `Cloud Computing Market Analysis`
   - **Add H2 headings:**
     - `What is cloud computing?` (type: Definition)
     - `What are the current market trends?` (type: List) 

4. **Click "Continue to Research" →**

5. **Run the research step** - this should gather sources from Perplexity

6. **Continue to Generate** and generate the content

7. **Check the results:**
   - Look for market projections in the introduction (like "$X trillion by 2025")
   - Check if these projections have citations like "according to [Source] ([Year])"
   - Verify sources appear at the bottom of the exported content

## Expected Results After Our Fix:

✅ **Should Work:** Market data with proper citations  
✅ **Should Work:** Sources section at bottom with links  
✅ **Should Work:** Up to 8 citations per document  
✅ **Should Work:** Financial projections get cited when sources available  

## Alternative Test with Mock Data:

If Perplexity sources don't have proper metadata, you can:

1. **Manually add a test source** to the research data
2. **Use the debug method below**

---

## Debug Method (via Code):

Run this test to verify our citation improvements are working:

```python
# This was already tested and works:
source venv/bin/activate && python -c "
from core.source_manager import SourceManager
sm = SourceManager()

# Test market projection with quality source
gartner_source = {'title': 'Cloud Market Report 2024', 'organization': 'Gartner', 'url': 'https://gartner.com'}
fact = 'The global cloud computing market size is projected to reach \$1.25 trillion by 2025'
result = sm.format_inline_citation(fact, gartner_source, 'introduction')
print('Result:', result)
print('Has citation:', 'according to' in result)
"
```

## Key Improvements Made:

1. **Citation Limits:** Increased from 5 to 8 per document
2. **Source Recognition:** Added market research firms (Gartner, Forrester, IDC, McKinsey)
3. **Financial Data:** Prioritized market projections and financial forecasts
4. **Content Generator:** Updated prompts to use proper citations
5. **Quality Standards:** Maintained while being less restrictive

---

**Test Result Summary:**
- ✅ Citation system is working correctly with proper source metadata
- ⚠️  Issue: Perplexity sources lack organization/author/date metadata needed for recognition
- 💡 **Recommendation:** Test with the Streamlit app to see if it provides better source formatting