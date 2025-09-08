#!/usr/bin/env python3
"""Debug extraction issues"""

from core.research_engine import ResearchEngine

# Test with a sample text
test_content = """
CDN caching is the process of storing copies of website content on geographically distributed servers.

Key Facts:
• CDN reduces latency by serving content from edge locations
• Modern CDNs support dynamic content caching
• Edge servers are located in data centers worldwide
• CDN caching improves website performance significantly

Statistics:
• CDNs can reduce load times by 50-70%
• Over 70% of internet traffic uses CDNs
• Average latency is 30ms globally
• 99.9% uptime is standard for CDN services

Cloud storage costs have decreased by 50% over the past 5 years.
The global CDN market is worth $15 billion in 2024.
"""

engine = ResearchEngine()

# Test fact extraction
print("Testing Fact Extraction:")
print("-" * 50)
facts = engine._extract_facts(test_content)
print(f"Facts found: {len(facts)}")
for i, fact in enumerate(facts[:5], 1):
    print(f"{i}. {fact}")

print("\n" + "=" * 50)
print("Testing Statistics Extraction:")
print("-" * 50)
stats = engine._extract_statistics(test_content)
print(f"Statistics found: {len(stats)}")
for i, stat in enumerate(stats[:5], 1):
    print(f"{i}. {stat}")