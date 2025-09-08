#!/usr/bin/env python3
"""Debug Perplexity response"""

from core.research_engine import ResearchEngine
import json

engine = ResearchEngine()

# Simple test query
topic = "cloud storage"
headings = [{"text": "What is cloud storage?", "level": "H2"}]

print("Sending request to Perplexity...")
print("-" * 50)

result = engine.research_topic(
    primary_keyword=topic,
    headings=headings,
    context="Test query for debugging"
)

if result['status'] == 'success':
    data = result['data']
    
    # Print raw content first
    print("RAW CONTENT (first 1000 chars):")
    print("-" * 50)
    print(data.get('raw_content', '')[:1000])
    print("\n" + "=" * 50)
    
    # Check extraction results
    print(f"Facts extracted: {len(data.get('facts', []))}")
    print(f"Statistics extracted: {len(data.get('statistics', []))}")
    print(f"Key points extracted: {len(data.get('key_points', []))}")
    print(f"Examples extracted: {len(data.get('examples', []))}")
    
    # Save full response for analysis
    with open('debug_perplexity_response.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\nFull response saved to debug_perplexity_response.json")
else:
    print(f"Error: {result.get('message', 'Unknown error')}")