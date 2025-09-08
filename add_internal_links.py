#!/usr/bin/env python3
"""
Add Internal Links to Existing Content
This script adds internal links to content that was generated without them
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.link_manager import LinkManager
from core.internal_linker import InternalLinker

def add_links_to_markdown(markdown_file: str, output_file: str = None):
    """
    Add internal links to an existing markdown file
    
    Args:
        markdown_file: Path to the markdown file
        output_file: Optional output path (if not specified, overwrites original)
    """
    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize link system
    print("Initializing internal link system...")
    link_manager = LinkManager()
    internal_linker = InternalLinker(link_manager)
    
    print(f"Loaded {link_manager.get_statistics()['total_links']} internal links")
    
    # Find all headings and their positions
    headings = []
    for match in re.finditer(r'^(#{1,3}\s+.+)$', content, re.MULTILINE):
        headings.append({
            'text': match.group(1),
            'start': match.start(),
            'end': match.end()
        })
    
    # Process sections
    processed_content = ""
    total_links_added = 0
    
    # Process introduction (before first heading)
    if headings:
        intro_content = content[:headings[0]['start']]
        if intro_content.strip():
            print(f"\nProcessing introduction...")
            suggestions = internal_linker.suggest_links_for_content(
                intro_content, 
                "Cloud Security",
                max_links=2
            )
            
            if suggestions:
                print(f"  Found {len(suggestions)} relevant links:")
                for link, anchor, score in suggestions:
                    print(f"    - {anchor} -> {link.url} (score: {score:.2f})")
                
                # Place links in content
                intro_with_links = internal_linker.place_links_in_content(
                    intro_content, suggestions
                )
                processed_content += intro_with_links
                total_links_added += len([s for s in suggestions if s[0].url in intro_with_links])
            else:
                print("  No relevant links found")
                processed_content += intro_content
    
    # Process each section
    for i, heading in enumerate(headings):
        # Add the heading
        processed_content += heading['text'] + '\n'
        
        # Get section content (between this heading and next, or end of file)
        section_start = heading['end'] + 1  # +1 for newline
        section_end = headings[i+1]['start'] if i+1 < len(headings) else len(content)
        section_content = content[section_start:section_end]
        
        if section_content.strip():
            print(f"\nProcessing section: {heading['text'].strip()}")
            
            # Get link suggestions for this section
            suggestions = internal_linker.suggest_links_for_content(
                section_content,
                heading['text'].replace('#', '').strip(),
                max_links=2
            )
            
            if suggestions:
                print(f"  Found {len(suggestions)} relevant links:")
                for link, anchor, score in suggestions:
                    print(f"    - {anchor} -> {link.url} (score: {score:.2f})")
                
                # Place links in content
                section_with_links = internal_linker.place_links_in_content(
                    section_content, suggestions
                )
                processed_content += section_with_links
                total_links_added += len([s for s in suggestions if s[0].url in section_with_links])
            else:
                print("  No relevant links found for this section")
                processed_content += section_content
        else:
            processed_content += section_content
    
    # Use the processed content
    final_content = processed_content
    
    # Validate link placement
    print(f"\n📊 Validating link placement...")
    validation = internal_linker.validate_link_placement(final_content)
    
    if validation['valid']:
        print(f"✅ Links placed successfully!")
    else:
        print(f"⚠️ Some issues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    print(f"\n📈 Summary:")
    print(f"  Total links added: {validation['total_links']}")
    print(f"  Link positions:")
    for pos in validation['link_positions']:
        print(f"    - {pos['anchor']} in paragraph {pos['paragraph']} ({pos['quality']} placement)")
    
    # Save the result
    output_path = output_file or markdown_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"\n✅ Content saved to: {output_path}")
    
    return validation['total_links']

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python add_internal_links.py <markdown_file> [output_file]")
        print("\nExample:")
        print("  python add_internal_links.py data/saved_content/cloud_security_20250828_174510.md")
        print("  python add_internal_links.py input.md output_with_links.md")
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(markdown_file).exists():
        print(f"Error: File '{markdown_file}' not found")
        sys.exit(1)
    
    print(f"🔗 Adding Internal Links to: {markdown_file}")
    print("=" * 60)
    
    try:
        links_added = add_links_to_markdown(markdown_file, output_file)
        
        if links_added > 0:
            print(f"\n🎉 Successfully added {links_added} internal links!")
        else:
            print(f"\n⚠️ No suitable places for internal links were found.")
            print("This could be because:")
            print("  1. The content doesn't match any product/learning topics")
            print("  2. The relevance threshold is too high")
            print("  3. The content already has sufficient links")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()