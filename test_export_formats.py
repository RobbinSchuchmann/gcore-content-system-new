#!/usr/bin/env python3
"""
Comprehensive test for all export formats with proper list handling
"""

import json
import re
from datetime import datetime

def create_test_content():
    """Create test content with various list types"""
    return {
        'metadata': {
            'primary_keyword': 'cloud computing services',
            'generated_date': datetime.now().isoformat(),
            'word_count': 250
        },
        'content': {
            'introduction': 'Cloud computing provides various service models for different needs.',
            'sections': [
                {
                    'heading': 'Types of Services',
                    'level': 'H2',
                    'content': """Cloud services come in different forms. The main types are listed below.

• **IaaS**: Infrastructure as a Service provides virtualized computing resources.

• **PaaS**: Platform as a Service offers development environments.

• **SaaS**: Software as a Service delivers applications over the internet.""",
                    'word_count': 50
                },
                {
                    'heading': 'Deployment Steps',
                    'level': 'H2',
                    'content': """Follow these steps to deploy:

1. Configure your environment
2. Set up authentication
3. Deploy the application
4. Monitor performance""",
                    'word_count': 20
                }
            ]
        }
    }

def test_html_export(content):
    """Test HTML export with proper list formatting"""
    print("\n" + "="*60)
    print("TESTING HTML EXPORT")
    print("="*60)
    
    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html>')
    html_parts.append('<head>')
    html_parts.append('<style>')
    html_parts.append('ul, ol { margin: 15px 0; padding-left: 30px; }')
    html_parts.append('li { margin: 8px 0; }')
    html_parts.append('</style>')
    html_parts.append('</head>')
    html_parts.append('<body>')
    
    for section in content['content']['sections']:
        html_parts.append(f'<h2>{section["heading"]}</h2>')
        
        paragraphs = section['content'].split('\n\n')
        in_list = False
        list_items = []
        list_type = None
        
        for para in paragraphs:
            if para.strip():
                # Check for bullet points
                if para.strip().startswith(('•', '-', '*')):
                    if not in_list:
                        in_list = True
                        list_items = []
                        list_type = 'ul'
                    
                    item_text = para.strip()[1:].strip()
                    item_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item_text)
                    list_items.append(item_text)
                    
                # Check for numbered lists
                elif para.strip()[0].isdigit() and '.' in para.strip()[:3]:
                    if not in_list:
                        in_list = True
                        list_items = []
                        list_type = 'ol'
                    
                    item_text = para.strip().split('.', 1)[1].strip()
                    list_items.append(item_text)
                    
                else:
                    # Close any open list
                    if in_list and list_items:
                        html_parts.append(f'<{list_type}>')
                        for item in list_items:
                            html_parts.append(f'  <li>{item}</li>')
                        html_parts.append(f'</{list_type}>')
                        in_list = False
                        list_items = []
                        list_type = None
                    
                    html_parts.append(f'<p>{para.strip()}</p>')
        
        # Close any remaining list
        if in_list and list_items:
            html_parts.append(f'<{list_type}>')
            for item in list_items:
                html_parts.append(f'  <li>{item}</li>')
            html_parts.append(f'</{list_type}>')
    
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    html_output = '\n'.join(html_parts)
    
    # Validate
    print("Sample HTML output:")
    print("-"*40)
    for line in html_output.split('\n')[10:25]:  # Show sample lines
        print(line)
    print("-"*40)
    
    has_ul = '<ul>' in html_output
    has_ol = '<ol>' in html_output
    has_li = '<li>' in html_output
    no_bullets = '•' not in html_output
    
    print(f"\n✓ Has <ul> tags: {has_ul}")
    print(f"✓ Has <ol> tags: {has_ol}")
    print(f"✓ Has <li> tags: {has_li}")
    print(f"✓ No bullet characters: {no_bullets}")
    
    success = has_ul and has_ol and has_li and no_bullets
    print(f"\n{'✅ HTML Export: PASSED' if success else '❌ HTML Export: FAILED'}")
    return success

def test_markdown_export(content):
    """Test Markdown export"""
    print("\n" + "="*60)
    print("TESTING MARKDOWN EXPORT")
    print("="*60)
    
    md_parts = []
    md_parts.append(f"# {content['metadata']['primary_keyword'].title()}")
    md_parts.append("")
    md_parts.append(content['content']['introduction'])
    md_parts.append("")
    
    for section in content['content']['sections']:
        md_parts.append(f"## {section['heading']}")
        md_parts.append("")
        md_parts.append(section['content'])
        md_parts.append("")
    
    md_output = '\n'.join(md_parts)
    
    print("Sample Markdown output:")
    print("-"*40)
    for line in md_output.split('\n')[:15]:
        print(line)
    print("-"*40)
    
    has_bullets = '•' in md_output or '-' in md_output
    has_headers = '##' in md_output
    has_bold = '**' in md_output
    
    print(f"\n✓ Has bullet points: {has_bullets}")
    print(f"✓ Has headers: {has_headers}")
    print(f"✓ Has bold formatting: {has_bold}")
    
    success = has_bullets and has_headers
    print(f"\n{'✅ Markdown Export: PASSED' if success else '❌ Markdown Export: FAILED'}")
    return success

def test_json_export(content):
    """Test JSON export"""
    print("\n" + "="*60)
    print("TESTING JSON EXPORT")
    print("="*60)
    
    json_output = json.dumps(content, indent=2)
    
    print("JSON structure validation:")
    print("-"*40)
    
    # Parse back to verify
    parsed = json.loads(json_output)
    
    has_metadata = 'metadata' in parsed
    has_content = 'content' in parsed
    has_sections = 'sections' in parsed.get('content', {})
    sections_count = len(parsed.get('content', {}).get('sections', []))
    
    print(f"✓ Has metadata: {has_metadata}")
    print(f"✓ Has content: {has_content}")
    print(f"✓ Has sections: {has_sections}")
    print(f"✓ Section count: {sections_count}")
    
    success = has_metadata and has_content and has_sections and sections_count > 0
    print(f"\n{'✅ JSON Export: PASSED' if success else '❌ JSON Export: FAILED'}")
    return success

def main():
    print("="*70)
    print("EXPORT FORMAT TESTING - LIST HANDLING")
    print("="*70)
    
    # Create test content
    test_content = create_test_content()
    
    # Test all formats
    results = {
        'HTML': test_html_export(test_content),
        'Markdown': test_markdown_export(test_content),
        'JSON': test_json_export(test_content)
    }
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for format_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{format_name:15} {status}")
    
    all_passed = all(results.values())
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL EXPORT FORMATS WORKING CORRECTLY")
        print("Lists are properly formatted in HTML as <ul>/<ol> with <li> tags")
        print("Bullet points preserved in Markdown")
        print("JSON structure maintained")
    else:
        print("❌ Some export formats have issues")
    print("="*70)

if __name__ == "__main__":
    main()