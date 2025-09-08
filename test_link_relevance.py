#!/usr/bin/env python3
"""Test why links aren't being suggested for cloud security content"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.link_manager import LinkManager
from core.internal_linker import InternalLinker

# Sample cloud security content
test_content = """
Cloud security is the collection of policies, technologies, applications, and controls designed to protect cloud-based systems, data, and infrastructure from cyber threats. Organizations spend an average of $1.75 million annually on cloud security solutions, with this investment growing 33% year-over-year as cloud adoption accelerates.

Cloud security operates through a shared responsibility model between cloud service providers and their customers. Cloud providers secure the underlying infrastructure including physical servers, networks, and hypervisors, while customers remain responsible for securing their data, applications, and user access controls.
"""

# Initialize
link_manager = LinkManager()
internal_linker = InternalLinker(link_manager)

print("Testing link suggestions for cloud security content...")
print("=" * 60)

# Lower the threshold for testing
internal_linker.min_relevance_score = 0.3
print(f"Relevance threshold: {internal_linker.min_relevance_score}")

# Get suggestions
suggestions = internal_linker.suggest_links_for_content(
    test_content,
    "Cloud Security",
    max_links=10
)

print(f"\nFound {len(suggestions)} links:")
for link, anchor, score in suggestions:
    print(f"  Score {score:.3f}: {link.url}")
    print(f"    Anchor: '{anchor}'")
    print(f"    Keywords: {link.keywords[:5] if len(link.keywords) > 5 else link.keywords}")
    print()

# Check specific keywords
print("\nChecking specific keywords in database:")
keywords_to_check = ['cloud', 'security', 'infrastructure', 'data', 'protection']
for kw in keywords_to_check:
    links = link_manager.get_links_by_keyword(kw)
    print(f"  '{kw}': {len(links)} links")

# Check cloud-specific URLs
print("\nCloud-related URLs in database:")
cloud_links = [link for link in link_manager.links if 'cloud' in link.url.lower()]
print(f"Found {len(cloud_links)} cloud-related links")

# Show product pages specifically
product_cloud_links = [link for link in cloud_links if link.category.startswith('product')]
print(f"\nProduct cloud links ({len(product_cloud_links)}):")
for link in product_cloud_links[:15]:
    print(f"  - {link.url} ({link.category}) - Keywords: {link.keywords[:3] if link.keywords else 'none'}")