"""
Markdown to HTML converter for proper list handling
"""

import re
from typing import List


def convert_markdown_to_html(content: str, format_type: str = "HTML") -> str:
    """
    Convert markdown content to proper HTML with correct list handling
    
    Args:
        content: Markdown formatted content
        format_type: Either "HTML" or "Google Docs" 
        
    Returns:
        Properly formatted HTML
    """
    # Split into paragraphs
    paragraphs = content.split('\n\n')
    html_parts = []
    
    i = 0
    while i < len(paragraphs):
        para = paragraphs[i].strip()
        
        if not para:
            i += 1
            continue
            
        # Check if this is a list (starts with bullet or number)
        # Also check if paragraph contains multiple lines that are list items
        lines = para.split('\n')
        is_list = False
        is_ordered = False
        
        # Check if this looks like a list
        if para.startswith('• ') or re.match(r'^\d+\.\s', para):
            is_list = True
            is_ordered = re.match(r'^\d+\.\s', para) is not None
        elif len(lines) > 1:
            # Check if multiple lines start with bullets
            bullet_count = sum(1 for line in lines if line.strip().startswith('• '))
            number_count = sum(1 for line in lines if re.match(r'^\d+\.\s', line.strip()))
            if bullet_count > 1 or number_count > 1:
                is_list = True
                is_ordered = number_count > bullet_count
        
        if is_list:
            # Collect all list items
            list_items = []
            
            # Process current paragraph as list
            for line in lines:
                line = line.strip()
                if line.startswith('• '):
                    list_items.append(line[2:])  # Remove bullet
                elif re.match(r'^\d+\.\s', line):
                    # Remove number and period
                    list_items.append(re.sub(r'^\d+\.\s*', '', line))
                elif line and list_items:
                    # This might be a continuation of the previous item
                    list_items[-1] += ' ' + line
            
            # Check next paragraphs for continuation of list
            while i + 1 < len(paragraphs):
                next_para = paragraphs[i + 1].strip()
                if next_para.startswith('• ') or (is_ordered and re.match(r'^\d+\.\s', next_para)):
                    i += 1
                    lines = next_para.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('• '):
                            list_items.append(line[2:])
                        elif re.match(r'^\d+\.\s', line):
                            list_items.append(re.sub(r'^\d+\.\s*', '', line))
                else:
                    break
            
            # Build HTML list
            if is_ordered:
                html_parts.append('<ol>')
            else:
                html_parts.append('<ul>')
                
            for item in list_items:
                # Convert markdown formatting within list items
                item_html = convert_inline_markdown(item, format_type)
                html_parts.append(f'<li>{item_html}</li>')
                
            if is_ordered:
                html_parts.append('</ol>')
            else:
                html_parts.append('</ul>')
                
        else:
            # Regular paragraph
            para_html = convert_inline_markdown(para, format_type)
            html_parts.append(f'<p>{para_html}</p>')
        
        i += 1
    
    return '\n'.join(html_parts)


def convert_inline_markdown(text: str, format_type: str = "HTML") -> str:
    """
    Convert inline markdown formatting to HTML
    
    Args:
        text: Text with markdown formatting
        format_type: Either "HTML" or "Google Docs"
        
    Returns:
        HTML formatted text
    """
    # For Google Docs, remove all markdown formatting
    if format_type == "Google Docs":
        text = text.replace('**', '')
        text = text.replace('*', '')
        text = text.replace('`', '')
        return text
    
    # Convert bold (**text** or __text__)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
    
    # Convert italic (*text* or _text_) - but not if it's part of bold
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'(?<!_)_(?!_)([^_]+)(?<!_)_(?!_)', r'<em>\1</em>', text)
    
    # Convert code (`text`)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Convert links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    
    return text


def convert_sources_section_to_html(sources_markdown: str) -> str:
    """
    Convert the sources section from markdown to HTML
    
    Args:
        sources_markdown: Markdown formatted sources section
        
    Returns:
        HTML formatted sources section
    """
    html_parts = []
    lines = sources_markdown.split('\n')
    
    in_list = False
    for line in lines:
        line = line.strip()
        
        if not line:
            if in_list:
                html_parts.append('</ol>')
                in_list = False
            continue
            
        # Convert headers
        if line.startswith('## '):
            if in_list:
                html_parts.append('</ol>')
                in_list = False
            html_parts.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            if in_list:
                html_parts.append('</ol>')
                in_list = False
            html_parts.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#'):
            # Sometimes there might be other header levels
            level = len(line.split()[0])
            if in_list:
                html_parts.append('</ol>')
                in_list = False
            html_parts.append(f'<h{level}>{line[level+1:].strip()}</h{level}>')
        # Convert numbered lists
        elif re.match(r'^\d+\.\s', line):
            if not in_list:
                html_parts.append('<ol>')
                in_list = True
            # Extract the list item content
            item_content = re.sub(r'^\d+\.\s*', '', line)
            # Convert markdown links to HTML
            item_html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', item_content)
            html_parts.append(f'<li>{item_html}</li>')
        else:
            if in_list:
                html_parts.append('</ol>')
                in_list = False
            # Regular paragraph
            para_html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', line)
            if para_html:
                html_parts.append(f'<p>{para_html}</p>')
    
    # Close any open list
    if in_list:
        html_parts.append('</ol>')
    
    return '\n'.join(html_parts)