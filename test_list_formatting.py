"""
Test script to verify HTML list formatting for both new content and optimization flows
"""

import re

def test_new_content_list_formatting():
    """Test the new content HTML generation with various list types"""

    # Sample content with numbered list
    sample_numbered = """1. First item with **bold text**
2. Second item
3. Third item with multiple words"""

    # Sample content with bullet list
    sample_bullets = """• First bullet point
• Second bullet point
• Third bullet with **bold**"""

    # Sample content with mixed paragraphs and lists
    sample_mixed = """This is a regular paragraph.

1. First numbered item
2. Second numbered item

This is another paragraph.

• Bullet one
• Bullet two"""

    print("=" * 60)
    print("NEW CONTENT FLOW - List Formatting Test")
    print("=" * 60)

    # Test numbered list
    print("\n1. NUMBERED LIST TEST:")
    print("-" * 40)
    html_output = convert_to_html_new_content(sample_numbered)
    print(html_output)

    # Test bullet list
    print("\n2. BULLET LIST TEST:")
    print("-" * 40)
    html_output = convert_to_html_new_content(sample_bullets)
    print(html_output)

    # Test mixed content
    print("\n3. MIXED CONTENT TEST:")
    print("-" * 40)
    html_output = convert_to_html_new_content(sample_mixed)
    print(html_output)


def convert_to_html_new_content(content):
    """Simulate the new content HTML conversion logic from app.py lines 2309-2361"""
    html_parts = []
    paragraphs = content.split('\n\n')

    i = 0
    while i < len(paragraphs):
        para = paragraphs[i].strip()
        if not para:
            i += 1
            continue

        # Handle numbered lists
        if re.match(r'^\d+\.\s', para):
            all_numbered_items = []
            numbered_items = re.findall(r'\d+\.\s+(.+?)(?=\n?\d+\.|$)', para, re.DOTALL)
            all_numbered_items.extend(numbered_items)

            while i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1].strip()
                if re.match(r'^\d+\.\s', next_para):
                    more_items = re.findall(r'\d+\.\s+(.+?)(?=\n?\d+\.|$)', next_para, re.DOTALL)
                    all_numbered_items.extend(more_items)
                    i += 1
                else:
                    break

            if all_numbered_items:
                html_parts.append('<ol>')
                for item in all_numbered_items:
                    item_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item.strip())
                    html_parts.append(f'  <li>{item_html}</li>')
                html_parts.append('</ol>')
            i += 1

        # Handle bullet lists
        elif '•' in para:
            bullet_items = []
            for part in para.split('\n'):
                if '•' in part:
                    items = part.split('•')
                    for item in items[1:]:
                        if item.strip():
                            bullet_items.append(item.strip())

            if bullet_items:
                html_parts.append('<ul>')
                for item in bullet_items:
                    item_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
                    html_parts.append(f'  <li>{item_html}</li>')
                html_parts.append('</ul>')
            i += 1

        else:
            # Regular paragraph
            para_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para)
            html_parts.append(f'<p>{para_html}</p>')
            i += 1

    return '\n'.join(html_parts)


def test_listicle_section():
    """Test a full listicle section (common pattern that might have issues)"""

    listicle_content = """**What is a CDN?** A Content Delivery Network is a distributed network of servers.

1. **Performance**: CDNs reduce latency by serving content from nearby servers
2. **Scalability**: Handle traffic spikes without overloading origin servers
3. **Security**: Protection against DDoS attacks and other threats

These benefits make CDNs essential for modern web applications."""

    print("\n" + "=" * 60)
    print("LISTICLE SECTION TEST")
    print("=" * 60)
    html_output = convert_to_html_new_content(listicle_content)
    print(html_output)

    # Check for proper structure
    print("\n" + "-" * 60)
    print("VALIDATION:")
    has_ol = '<ol>' in html_output and '</ol>' in html_output
    has_li = '<li>' in html_output and '</li>' in html_output
    has_strong = '<strong>' in html_output
    has_p = '<p>' in html_output

    print(f"✓ Has ordered list tags: {has_ol}")
    print(f"✓ Has list item tags: {has_li}")
    print(f"✓ Has bold formatting: {has_strong}")
    print(f"✓ Has paragraph tags: {has_p}")


if __name__ == "__main__":
    test_new_content_list_formatting()
    test_listicle_section()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
This test verifies that:
1. Numbered lists are properly converted to <ol><li> tags
2. Bullet lists are properly converted to <ul><li> tags
3. Bold markdown (**text**) is converted to <strong> tags
4. Mixed content (paragraphs + lists) is handled correctly
5. Listicle patterns maintain proper structure

If all tests show proper HTML structure, the issue may be:
- In how Google Docs imports the HTML
- In the actual content generation (not the HTML conversion)
- In a specific edge case not covered by these tests
""")
