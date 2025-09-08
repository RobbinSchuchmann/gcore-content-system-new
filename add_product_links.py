#!/usr/bin/env python3
"""
Add Product Internal Links to Content
Focuses on adding relevant Gcore product page links
"""

import re
from pathlib import Path

# Key product pages and their trigger keywords
PRODUCT_LINKS = {
    '/cloud': {
        'keywords': ['cloud', 'cloud computing', 'cloud infrastructure', 'cloud services', 'cloud platform'],
        'anchor_variants': ['cloud platform', 'cloud infrastructure', 'cloud services']
    },
    '/cloud/secure-cloud-computing': {
        'keywords': ['secure cloud', 'cloud security', 'secure computing'],
        'anchor_variants': ['secure cloud computing', 'secure cloud solutions']
    },
    '/ddos-protection': {
        'keywords': ['ddos', 'ddos protection', 'ddos attack', 'denial of service'],
        'anchor_variants': ['DDoS protection', 'DDoS protection services']
    },
    '/cloud/managed-kubernetes': {
        'keywords': ['kubernetes', 'k8s', 'container orchestration', 'managed kubernetes'],
        'anchor_variants': ['managed Kubernetes', 'Kubernetes services']
    },
    '/cloud/load-balancers': {
        'keywords': ['load balancer', 'load balancing', 'traffic distribution'],
        'anchor_variants': ['load balancers', 'load balancing solutions']
    },
    '/cloud/managed-database-postgresql': {
        'keywords': ['database', 'postgresql', 'managed database'],
        'anchor_variants': ['managed database', 'database services']
    },
    '/dns': {
        'keywords': ['dns', 'domain name system', 'nameserver'],
        'anchor_variants': ['DNS hosting', 'DNS services']
    },
    '/cdn': {
        'keywords': ['cdn', 'content delivery', 'content distribution'],
        'anchor_variants': ['CDN solution', 'content delivery network']
    }
}

def find_best_anchor(content, link_data):
    """Find the best anchor text in the content"""
    content_lower = content.lower()
    
    # Try to find exact matches from anchor variants
    for anchor in link_data['anchor_variants']:
        if anchor.lower() in content_lower:
            # Find the exact case version
            pattern = re.escape(anchor)
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
    
    # Try keywords
    for keyword in link_data['keywords']:
        if keyword in content_lower:
            # Find exact case
            pattern = r'\b' + re.escape(keyword) + r'\b'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
    
    return None

def add_product_links(markdown_file, output_file=None):
    """Add product links to markdown content"""
    
    # Read file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Adding product links to: {markdown_file}")
    print("=" * 60)
    
    # Track which links we've already added
    links_added = set()
    links_count = 0
    
    # Process each product link
    for url, link_data in PRODUCT_LINKS.items():
        # Skip if we already have this link
        if url in content:
            print(f"✓ Link {url} already exists")
            continue
        
        # Find best anchor text
        anchor = find_best_anchor(content, link_data)
        
        if anchor and anchor.lower() not in links_added:
            # Create markdown link
            link = f"[{anchor}]({url})"
            
            # Replace first occurrence only
            pattern = re.escape(anchor)
            new_content, count = re.subn(pattern, link, content, count=1)
            
            if count > 0:
                content = new_content
                links_added.add(anchor.lower())
                links_count += 1
                print(f"✅ Added link: {anchor} -> {url}")
            else:
                print(f"⚠️ Could not place link for {url}")
        else:
            if not anchor:
                print(f"✗ No suitable anchor found for {url}")
    
    # Save result
    output_path = output_file or markdown_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n📊 Summary:")
    print(f"  Total links added: {links_count}")
    print(f"  File saved to: {output_path}")
    
    return links_count

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python add_product_links.py <markdown_file> [output_file]")
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(markdown_file).exists():
        print(f"Error: File '{markdown_file}' not found")
        sys.exit(1)
    
    links_added = add_product_links(markdown_file, output_file)
    
    if links_added > 0:
        print(f"\n🎉 Successfully added {links_added} product links!")
    else:
        print(f"\n✓ No new links needed - content may already have links or no matches found")

if __name__ == "__main__":
    main()