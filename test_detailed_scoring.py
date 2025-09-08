#!/usr/bin/env python3
"""Test detailed scoring for cloud security content"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.link_manager import LinkManager
from core.internal_linker import InternalLinker

# Sample cloud security content - from the actual article
test_content = """
Cloud security is the collection of policies, technologies, applications, and controls designed to protect cloud-based systems, data, and infrastructure from cyber threats. Cloud security operates through identity and access management (IAM), which authenticates users and controls permissions. Network security controls traffic flow through virtual firewalls and security groups.
"""

# Initialize
link_manager = LinkManager()
internal_linker = InternalLinker(link_manager)

print("Detailed scoring analysis for cloud security content")
print("=" * 60)

# Get specific cloud product pages
test_links = [
    "/cloud",
    "/cloud/secure-cloud-computing", 
    "/ddos-protection",
    "/cloud/managed-kubernetes",
    "/cloud/load-balancers"
]

print("\nManual scoring for key product pages:")
for url in test_links:
    # Find the link
    matching_links = [l for l in link_manager.links if l.url == url]
    if matching_links:
        link = matching_links[0]
        score = internal_linker._calculate_relevance_score(link, test_content, "Cloud Security")
        print(f"\n{url}:")
        print(f"  Category: {link.category}")
        print(f"  Keywords: {link.keywords[:5] if len(link.keywords) > 5 else link.keywords}")
        print(f"  Relevance keywords: {link.relevance_keywords[:5] if len(link.relevance_keywords) > 5 else link.relevance_keywords}")
        print(f"  Score: {score:.3f}")
        
        # Check keyword matches
        content_lower = test_content.lower()
        matches = []
        for kw in link.relevance_keywords:
            if kw.lower() in content_lower:
                matches.append(kw)
        print(f"  Matched keywords: {matches}")

# Try with even lower threshold
print("\n" + "=" * 60)
print("Testing with very low threshold (0.1):")
internal_linker.min_relevance_score = 0.1

suggestions = internal_linker.suggest_links_for_content(
    test_content,
    "Cloud Security", 
    max_links=10
)

print(f"\nFound {len(suggestions)} links with threshold 0.1:")
for link, anchor, score in suggestions[:5]:
    print(f"  {score:.3f}: {link.url} ('{anchor}')")