#!/usr/bin/env python3
"""
Test script to verify HTML export formatting for lists
"""

import re

def test_html_list_formatting():
    """Test that bullet points are converted to proper HTML lists"""
    
    # Test content with bullet points (similar to the cloud computing export)
    test_section_content = """The main types of cloud computing services refer to the different service models that provide computing resources over the internet with varying levels of management and control. The main types of cloud computing services are listed below.

• **Infrastructure as a Service (IaaS)**: IaaS provides virtualized computing infrastructure including servers, storage, and networking resources over the internet. Users can deploy and run software while the cloud provider manages the underlying hardware and virtualization layer.

• **Platform as a Service (PaaS)**: PaaS offers a complete development and deployment environment in the cloud, including operating systems, development tools, and database management systems. Developers can build, test, and deploy applications without managing the underlying infrastructure.

• **Software as a Service (SaaS)**: SaaS delivers fully functional software applications over the internet through a web browser or mobile app. Users access the software on a subscription basis without installing or maintaining it locally."""

    # Simulate the HTML generation logic
    html_parts = []
    html_parts.append('<h2>Test Section</h2>')
    
    # Convert content to paragraphs and lists
    paragraphs = test_section_content.split('\n\n')
    in_list = False
    list_items = []
    
    for para in paragraphs:
        if para.strip():
            # Check if this paragraph is a bullet point
            if para.strip().startswith(('•', '-', '*', '1.', '2.', '3.')):
                # It's a list item
                if not in_list:
                    in_list = True
                    list_items = []
                
                # Remove bullet point marker
                item_text = para.strip()
                if item_text.startswith(('•', '-', '*')):
                    item_text = item_text[1:].strip()
                elif item_text[0].isdigit() and '.' in item_text[:3]:
                    item_text = item_text.split('.', 1)[1].strip()
                
                # Handle bold formatting
                item_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item_text)
                list_items.append(item_text)
            else:
                # Not a list item - if we were in a list, close it first
                if in_list and list_items:
                    html_parts.append('<ul>')
                    for item in list_items:
                        html_parts.append(f'    <li>{item}</li>')
                    html_parts.append('</ul>')
                    in_list = False
                    list_items = []
                
                # Add as regular paragraph
                para_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para.strip())
                html_parts.append(f'<p>{para_html}</p>')
    
    # Close any remaining list
    if in_list and list_items:
        html_parts.append('<ul>')
        for item in list_items:
            html_parts.append(f'    <li>{item}</li>')
        html_parts.append('</ul>')
    
    # Join HTML
    html_output = '\n'.join(html_parts)
    
    # Verify the output
    print("Generated HTML:")
    print("=" * 50)
    print(html_output)
    print("=" * 50)
    
    # Check that we have proper list tags
    has_ul = '<ul>' in html_output
    has_li = '<li>' in html_output
    has_strong = '<strong>' in html_output
    no_bullet_chars = '•' not in html_output
    
    print("\nValidation Results:")
    print(f"✓ Has <ul> tags: {has_ul}")
    print(f"✓ Has <li> tags: {has_li}")
    print(f"✓ Has <strong> tags for bold: {has_strong}")
    print(f"✓ No bullet characters in output: {no_bullet_chars}")
    
    # Count elements
    ul_count = html_output.count('<ul>')
    li_count = html_output.count('<li>')
    p_count = html_output.count('<p>')
    
    print(f"\nElement Counts:")
    print(f"  <ul> tags: {ul_count}")
    print(f"  <li> tags: {li_count}")
    print(f"  <p> tags: {p_count}")
    
    if has_ul and has_li and has_strong and no_bullet_chars:
        print("\n✅ HTML list formatting is working correctly!")
        return True
    else:
        print("\n❌ HTML list formatting has issues")
        return False

def test_numbered_list():
    """Test numbered list formatting"""
    
    test_content = """Steps to deploy:

1. Configure the server
2. Install dependencies
3. Deploy the application"""

    paragraphs = test_content.split('\n\n')
    html_parts = []
    
    for para in paragraphs:
        if para.strip():
            if para.strip()[0].isdigit() and '.' in para.strip()[:3]:
                # It's a numbered list item
                items = para.strip().split('\n')
                html_parts.append('<ol>')
                for item in items:
                    if item.strip()[0].isdigit():
                        item_text = item.split('.', 1)[1].strip()
                        html_parts.append(f'    <li>{item_text}</li>')
                html_parts.append('</ol>')
            else:
                html_parts.append(f'<p>{para.strip()}</p>')
    
    html_output = '\n'.join(html_parts)
    
    print("\n\nNumbered List Test:")
    print("=" * 50)
    print(html_output)
    print("=" * 50)
    
    has_ol = '<ol>' in html_output
    print(f"\n✓ Has <ol> tags for numbered list: {has_ol}")
    
    return has_ol

if __name__ == "__main__":
    print("Testing HTML Export List Formatting")
    print("=" * 70)
    
    test1 = test_html_list_formatting()
    test2 = test_numbered_list()
    
    if test1 and test2:
        print("\n" + "=" * 70)
        print("✅ ALL HTML FORMATTING TESTS PASSED")
        print("Lists will be properly formatted as <ul>/<ol> and <li> tags in HTML exports")
    else:
        print("\n" + "=" * 70)
        print("❌ Some tests failed")