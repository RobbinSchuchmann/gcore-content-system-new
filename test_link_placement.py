#!/usr/bin/env python3
"""Test link placement in cloud security content"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.link_manager import LinkManager
from core.internal_linker import InternalLinker, InternalLink

# Sample paragraph from cloud security article
test_content = """
Cloud security is the collection of policies, technologies, applications, and controls designed to protect cloud-based systems, data, and infrastructure from cyber threats. Organizations spend an average of $1.75 million annually on cloud security solutions, with this investment growing 33% year-over-year as cloud adoption accelerates.
"""

# Initialize
link_manager = LinkManager()
internal_linker = InternalLinker(link_manager)

print("Testing link placement in cloud security content")
print("=" * 60)

# Manually create a suggestion for testing
cloud_link = None
for link in link_manager.links:
    if link.url == "/cloud":
        cloud_link = link
        break

if cloud_link:
    print(f"Using link: {cloud_link.url}")
    print(f"Keywords: {cloud_link.keywords[:5]}")
    
    # Test finding natural anchor text
    anchor = internal_linker._find_natural_anchor_text(cloud_link, test_content)
    print(f"Natural anchor found: '{anchor}'")
    
    if not anchor:
        # Try manual anchor
        anchor = "cloud security solutions"
        print(f"Using manual anchor: '{anchor}'")
    
    # Create suggestion
    suggestions = [(cloud_link, anchor, 0.5)]
    
    # Try to place the link
    print("\nAttempting to place link...")
    result = internal_linker.place_links_in_content(test_content, suggestions)
    
    print("\nOriginal content:")
    print(test_content[:200] + "...")
    
    print("\nContent with links:")
    print(result[:300] + "...")
    
    # Check if link was actually placed
    if "[" in result and "](" in result:
        print("\n✅ Link was successfully placed!")
    else:
        print("\n❌ Link was NOT placed")
        print("\nDebug: Checking why...")
        print(f"  - Anchor text '{anchor}' in content: {anchor.lower() in test_content.lower()}")
        print(f"  - Content has paragraphs: {len(test_content.split('\\n\\n'))}")
        print(f"  - Content word count: {len(test_content.split())}")
else:
    print("Could not find /cloud link in database")