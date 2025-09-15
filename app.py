"""
Gcore Content System with Optimization Workflow
Main application with tab navigation for New Content and Content Optimization
"""

import streamlit as st
import json
import re
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, Tuple

# Load environment variables
load_dotenv()

# Import core modules
try:
    from core.semantic_patterns import detect_question_type, get_pattern_template
    from core.research_engine import ResearchEngine
    from core.content_generator import ContentGenerator
    from core.quality_checker import QualityChecker, fix_ai_words
    from core.content_editor import ContentEditor
    from config import validate_api_keys, ANTHROPIC_API_KEY, PERPLEXITY_API_KEY
    APIS_AVAILABLE = True
except ImportError:
    APIS_AVAILABLE = False
    ANTHROPIC_API_KEY = None
    PERPLEXITY_API_KEY = None

# Import scraper separately to handle its dependencies
try:
    from core.content_scraper import ContentScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Gcore Content System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication system
import time

def get_auth_file_path():
    """Get path to authentication file"""
    return Path("data/.auth_session")

def is_authenticated():
    """Check if authentication file exists and is still valid"""
    auth_file = get_auth_file_path()
    if not auth_file.exists():
        return False

    try:
        with open(auth_file, 'r') as f:
            stored_data = json.load(f)

        # Check if session is still valid (24 hours)
        if time.time() - stored_data.get('timestamp', 0) < 86400:  # 24 hours
            return True
        else:
            # Session expired, remove file
            auth_file.unlink()
            return False
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return False

def set_authenticated():
    """Mark session as authenticated"""
    auth_file = get_auth_file_path()
    auth_file.parent.mkdir(exist_ok=True)

    auth_data = {
        'authenticated': True,
        'timestamp': time.time()
    }

    with open(auth_file, 'w') as f:
        json.dump(auth_data, f)

def clear_authentication():
    """Clear authentication"""
    auth_file = get_auth_file_path()
    if auth_file.exists():
        auth_file.unlink()

def check_authentication():
    """Check if user is authenticated"""
    # Initialize authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = is_authenticated()

    if not st.session_state.authenticated:
        show_login_form()
        return False
    return True

def show_login_form():
    """Display login form"""
    st.title("🔒 Gcore Content System - Login")
    st.markdown("---")

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Please login to access the content system")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

            if submitted:
                # Hardcoded credentials
                if username == "Gcore" and password == "pqz@J5rkv@3$zGUv":
                    st.session_state.authenticated = True
                    set_authenticated()  # Save authentication to file
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

        st.markdown("---")
        st.caption("Contact your administrator if you need access.")

# Check authentication before showing main app
if not check_authentication():
    st.stop()

# Initialize session state
if 'content_brief' not in st.session_state:
    st.session_state.content_brief = {
        'primary_keyword': '',
        'introduction': '',
        'headings': [],
        'research_data': {},
        'generated_content': {},
        'quality_scores': {}
    }

if 'optimization_data' not in st.session_state:
    st.session_state.optimization_data = {
        'url': '',
        'primary_keyword': '',
        'additional_keywords': [],
        'original_content': '',
        'parsed_structure': {},
        'optimized_headings': [],
        'gap_analysis': {},
        'research_data': {},
        'optimized_content': {},
        'quality_comparison': {}
    }

if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

if 'active_mode' not in st.session_state:
    st.session_state.active_mode = "📝 New Content"

if 'ai_word_data' not in st.session_state:
    st.session_state.ai_word_data = {
        'blacklist': {},
        'test_text': '',
        'changes_made': False
    }

# Load section functions configuration
def load_section_functions():
    """Load section functions from JSON file"""
    functions_file = Path("data/section_functions.json")
    if functions_file.exists():
        with open(functions_file, 'r') as f:
            return json.load(f)
    return {"functions": {}, "auto_detection_map": {}}

def get_function_options(section_functions):
    """Get function options for dropdown"""
    functions = section_functions.get('functions', {})
    return {key: value['name'] for key, value in functions.items()}

def auto_detect_function(heading, section_functions, context=None):
    """Auto-detect the best function based on heading text and context
    
    Args:
        heading: The heading text to analyze
        section_functions: The loaded section functions configuration
        context: Optional context dict with 'in_faq_section' and 'heading_level'
    """
    if not heading:
        return "generate_definition"
    
    heading_lower = heading.lower().strip()
    auto_map = section_functions.get('auto_detection_map', {})
    
    # Check if we're in FAQ context (H3 after FAQ H2)
    if context and context.get('in_faq_section') and context.get('heading_level') == 'H3':
        # All H3s in FAQ section should use FAQ answer format
        return "generate_faq_answer"
    
    # Check for exact matches first
    for pattern, function in auto_map.items():
        if heading_lower.startswith(pattern):
            return function
    
    # Check for keywords anywhere in heading
    for pattern, function in auto_map.items():
        if pattern in heading_lower:
            return function
    
    return "generate_definition"

def parse_existing_content(content: str) -> Dict[str, Any]:
    """
    Parse existing content to extract structure and sections
    
    Args:
        content: Raw HTML or text content
        
    Returns:
        Dictionary with parsed structure
    """
    structure = {
        'title': '',
        'headings': [],
        'sections': {},
        'word_count': 0
    }
    
    # Check if content is HTML or plain text
    has_html = bool(re.search(r'<[^>]+>', content))
    
    if has_html:
        # Extract H1 title
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if h1_match:
            structure['title'] = h1_match.group(1).strip()
        
        # Extract all headings with proper closing tags
        heading_pattern = r'<(h[1-3])[^>]*>([^<]+)</\1>'
        headings = list(re.finditer(heading_pattern, content, re.IGNORECASE))
        
        if not headings:
            # Try alternative patterns for headings
            # Sometimes headings might have nested elements
            heading_pattern_alt = r'<(h[1-3])[^>]*>(.*?)</\1>'
            headings = list(re.finditer(heading_pattern_alt, content, re.IGNORECASE | re.DOTALL))
        
        last_position = 0
        last_heading = None
        
        for match in headings:
            level = match.group(1).upper()
            # Clean any nested HTML from heading text
            heading_text = re.sub(r'<[^>]+>', '', match.group(2)).strip()
            
            if heading_text:  # Only add non-empty headings
                position = match.start()
                
                # Save the content for the previous heading
                if last_heading:
                    section_content = content[last_position:position]
                    # Clean HTML tags from section content
                    clean_section = re.sub(r'<[^>]+>', '', section_content).strip()
                    if clean_section:
                        structure['sections'][last_heading['text']] = clean_section
                
                # Add current heading to structure
                structure['headings'].append({
                    'level': level,
                    'text': heading_text,
                    'original_text': heading_text
                })
                
                last_heading = structure['headings'][-1]
                last_position = match.end()
        
        # Save content for the last heading
        if last_heading and last_position < len(content):
            section_content = content[last_position:]
            clean_section = re.sub(r'<[^>]+>', '', section_content).strip()
            if clean_section:
                structure['sections'][last_heading['text']] = clean_section
        
        # Calculate actual word count from cleaned content
        all_text = ' '.join(structure['sections'].values())
        structure['word_count'] = len(all_text.split()) if all_text else 0
        
    else:
        # Handle plain text content - look for markdown-style headings
        lines = content.split('\n')
        current_section = []
        current_heading = None
        
        for line in lines:
            # Check for markdown headings
            if line.startswith('#'):
                # Save previous section
                if current_heading and current_section:
                    section_text = '\n'.join(current_section).strip()
                    if section_text:
                        structure['sections'][current_heading['text']] = section_text
                
                # Parse heading level and text
                heading_match = re.match(r'^(#+)\s+(.+)$', line)
                if heading_match:
                    level_count = len(heading_match.group(1))
                    heading_text = heading_match.group(2).strip()
                    
                    level = f'H{min(level_count, 3)}'  # Cap at H3
                    
                    structure['headings'].append({
                        'level': level,
                        'text': heading_text,
                        'original_text': heading_text
                    })
                    
                    current_heading = structure['headings'][-1]
                    current_section = []
            else:
                # Add line to current section
                if line.strip():
                    current_section.append(line)
        
        # Save last section
        if current_heading and current_section:
            section_text = '\n'.join(current_section).strip()
            if section_text:
                structure['sections'][current_heading['text']] = section_text
        
        # Calculate word count
        all_text = ' '.join(structure['sections'].values())
        structure['word_count'] = len(all_text.split()) if all_text else 0
    
    # If no headings were found, create a default structure
    if not structure['headings'] and content.strip():
        # Try to extract some structure from the content
        paragraphs = re.split(r'\n\s*\n', content)
        if paragraphs:
            # Use first paragraph as potential title
            first_para = paragraphs[0].strip()
            if len(first_para) < 100:  # Likely a title
                structure['title'] = re.sub(r'<[^>]+>', '', first_para).strip()
            
            # Create a default heading
            structure['headings'].append({
                'level': 'H2',
                'text': 'Main Content',
                'original_text': 'Main Content'
            })
            
            # Store all content under this heading
            clean_content = re.sub(r'<[^>]+>', '', content).strip()
            structure['sections']['Main Content'] = clean_content
            structure['word_count'] = len(clean_content.split())
    
    return structure

def analyze_content_gaps(parsed_structure: Dict, keywords: List[str]) -> Dict[str, Any]:
    """
    Analyze content gaps based on keywords and structure
    
    Args:
        parsed_structure: Parsed content structure
        keywords: Target keywords for optimization
        
    Returns:
        Gap analysis results
    """
    gaps = {
        'missing_keywords': [],
        'suggested_headings': [],
        'content_coverage': 0,
        'improvement_opportunities': []
    }
    
    # Check which keywords are missing from headings
    existing_headings_text = ' '.join([h['text'].lower() for h in parsed_structure['headings']])
    existing_content = ' '.join(parsed_structure['sections'].values()).lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower not in existing_headings_text:
            if keyword_lower not in existing_content:
                gaps['missing_keywords'].append(keyword)
                # Suggest heading for missing keyword
                gaps['suggested_headings'].append({
                    'text': f"What is {keyword}?",
                    'level': 'H2',
                    'reason': f'Missing coverage for keyword: {keyword}'
                })
    
    # Calculate content coverage score
    if keywords:
        covered = len([k for k in keywords if k.lower() in existing_content])
        gaps['content_coverage'] = (covered / len(keywords)) * 100
    
    # Identify improvement opportunities
    if gaps['content_coverage'] < 50:
        gaps['improvement_opportunities'].append("Low keyword coverage - consider adding more relevant sections")
    
    if len(parsed_structure['headings']) < 5:
        gaps['improvement_opportunities'].append("Limited content depth - consider adding more detailed sections")
    
    # Check for common missing sections
    common_sections = {
        'benefits': 'Benefits and Advantages',
        'how to': 'How to Guide',
        'best practices': 'Best Practices',
        'comparison': 'Comparison with Alternatives',
        'use cases': 'Common Use Cases'
    }
    
    for key, heading in common_sections.items():
        if key not in existing_headings_text:
            gaps['suggested_headings'].append({
                'text': heading,
                'level': 'H2',
                'reason': f'Common section type missing: {key}'
            })
    
    return gaps

# Function to implement AI Word Manager (defined before use)
def implement_ai_word_manager():
    """Implement the AI Word Manager interface"""
    
    # Load current blacklist
    replacements_file = Path("data/ai_word_replacements.json")
    if replacements_file.exists():
        with open(replacements_file, 'r') as f:
            blacklist_data = json.load(f)
    else:
        blacklist_data = {
            "word_groups": {},
            "simple_replacements": {},
            "usage_notes": {}
        }
    
    # Store in session state for editing
    if 'blacklist_data' not in st.session_state or st.button("🔄 Reload from File", key="reload_blacklist_manager"):
        st.session_state.blacklist_data = blacklist_data
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_groups = len(st.session_state.blacklist_data.get('word_groups', {}))
        st.metric("Word Groups", total_groups)
    with col2:
        total_simple = len(st.session_state.blacklist_data.get('simple_replacements', {}))
        st.metric("Simple Replacements", total_simple)
    with col3:
        total_words = total_groups * 3 + total_simple  # Approximate
        st.metric("Total Blacklisted", f"~{total_words}")
    with col4:
        if st.button("💾 Save Changes", type="primary", use_container_width=True, key="save_changes_manager"):
            with open(replacements_file, 'w') as f:
                json.dump(st.session_state.blacklist_data, f, indent=2)
            st.success("✅ Changes saved successfully!")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Word Groups", "🔤 Simple Replacements", "🧪 Test Tool", "📥 Import/Export"])
    
    with tab1:
        st.markdown("### Word Groups Management")
        st.caption("Manage groups of related words with shared replacements")
        
        # Add new group
        with st.expander("➕ Add New Word Group", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_group_name = st.text_input("Group Name", placeholder="e.g., leverage_group", key="new_group_name_manager")
                new_words = st.text_area("Words (one per line)", placeholder="leverage\nleveraging\nleveraged", key="new_words_manager")
            with col2:
                new_replacements = st.text_area("Replacements (one per line)", placeholder="use\napply\nemploy", key="new_replacements_manager")
                new_context = st.text_input("Context", placeholder="For utilizing resources", key="new_context_manager")
            
            if st.button("Add Group", key="add_group_manager"):
                if new_group_name and new_words and new_replacements:
                    st.session_state.blacklist_data['word_groups'][new_group_name] = {
                        'words': new_words.strip().split('\n'),
                        'replacements': new_replacements.strip().split('\n'),
                        'context': new_context
                    }
                    st.success(f"Added group: {new_group_name}")
                    st.rerun()
        
        # Display and edit existing groups
        for group_name, group_data in st.session_state.blacklist_data.get('word_groups', {}).items():
            with st.expander(f"📦 {group_name}", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown("**Forbidden Words:**")
                    for word in group_data.get('words', []):
                        st.caption(f"• {word}")
                with col2:
                    st.markdown("**Replacements:**")
                    for replacement in group_data.get('replacements', []):
                        st.caption(f"✓ {replacement}")
                with col3:
                    if st.button(f"🗑️ Delete", key=f"del_{group_name}"):
                        del st.session_state.blacklist_data['word_groups'][group_name]
                        st.rerun()
                
                if group_data.get('context'):
                    st.info(f"Context: {group_data['context']}")
    
    with tab2:
        st.markdown("### Simple Replacements")
        st.caption("Direct word-to-word replacements")
        
        # Add new simple replacement
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            new_forbidden = st.text_input("Forbidden Word", placeholder="utilize", key="new_forbidden_manager")
        with col2:
            new_replacement = st.text_input("Replacement", placeholder="use", key="new_replacement_manager")
        with col3:
            if st.button("➕ Add", use_container_width=True, key="add_simple_manager"):
                if new_forbidden and new_replacement:
                    st.session_state.blacklist_data['simple_replacements'][new_forbidden] = new_replacement
                    st.success(f"Added: {new_forbidden} → {new_replacement}")
                    st.rerun()
        
        # Display existing replacements in a table-like format
        if st.session_state.blacklist_data.get('simple_replacements'):
            st.markdown("#### Current Replacements")
            
            # Search filter
            search_term = st.text_input("🔍 Search replacements", placeholder="Type to filter...", key="search_term_manager")
            
            # Display filtered replacements
            for forbidden, replacement in sorted(st.session_state.blacklist_data['simple_replacements'].items()):
                if search_term.lower() in forbidden.lower() or search_term.lower() in replacement.lower():
                    col1, col2, col3 = st.columns([3, 3, 1])
                    with col1:
                        st.text(f"❌ {forbidden}")
                    with col2:
                        st.text(f"✅ {replacement}")
                    with col3:
                        if st.button("🗑️", key=f"del_simple_{forbidden}"):
                            del st.session_state.blacklist_data['simple_replacements'][forbidden]
                            st.rerun()
    
    with tab3:
        st.markdown("### Test AI Word Detection & Replacement")
        st.caption("Test how your text will be processed")
        
        test_text = st.text_area(
            "Enter text to test:",
            placeholder="We will leverage our expertise to utilize cutting-edge technology...",
            height=150,
            key="test_text_manager"
        )
        
        if test_text:
            # Process the text
            processed_text = test_text
            replacements_made = []
            
            # Apply word group replacements
            for group in st.session_state.blacklist_data.get('word_groups', {}).values():
                words = group.get('words', [])
                replacements = group.get('replacements', [])
                if words and replacements:
                    for word in words:
                        pattern = r'\b' + re.escape(word) + r'\b'
                        if re.search(pattern, processed_text, re.IGNORECASE):
                            processed_text = re.sub(pattern, replacements[0], processed_text, flags=re.IGNORECASE)
                            replacements_made.append(f"{word} → {replacements[0]}")
            
            # Apply simple replacements
            for forbidden, replacement in st.session_state.blacklist_data.get('simple_replacements', {}).items():
                pattern = r'\b' + re.escape(forbidden) + r'\b'
                if re.search(pattern, processed_text, re.IGNORECASE):
                    processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE)
                    replacements_made.append(f"{forbidden} → {replacement}")
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Original Text")
                st.text_area("Before:", test_text, height=150, disabled=True, key="before_text_manager")
            with col2:
                st.markdown("#### Processed Text")
                st.text_area("After:", processed_text, height=150, disabled=True, key="after_text_manager")
            
            if replacements_made:
                st.success(f"✅ {len(replacements_made)} replacements made:")
                for replacement in replacements_made:
                    st.caption(f"• {replacement}")
            else:
                st.info("No AI words detected in the text")
    
    with tab4:
        st.markdown("### Import/Export Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Import Blacklist")
            uploaded_file = st.file_uploader("Upload text file (one word per line)", type=['txt'], key="upload_file_manager")
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                words = [word.strip() for word in content.split('\n') if word.strip()]
                st.info(f"Found {len(words)} words to import")
                
                default_replacement = st.text_input("Default replacement for all", "", key="default_repl_manager")
                if st.button("Import Words", key="import_words_manager"):
                    for word in words:
                        if word and default_replacement:
                            st.session_state.blacklist_data['simple_replacements'][word.lower()] = default_replacement
                    st.success(f"Imported {len(words)} words")
                    st.rerun()
        
        with col2:
            st.markdown("#### Export Configuration")
            
            export_format = st.selectbox("Export Format", ["JSON", "Text List", "CSV"], key="export_format_manager")
            
            if st.button("📥 Generate Export", key="generate_export_manager"):
                if export_format == "JSON":
                    export_data = json.dumps(st.session_state.blacklist_data, indent=2)
                    st.download_button(
                        "⬇️ Download JSON",
                        export_data,
                        "ai_word_replacements.json",
                        "application/json"
                    )
                elif export_format == "Text List":
                    all_words = []
                    for group in st.session_state.blacklist_data.get('word_groups', {}).values():
                        all_words.extend(group.get('words', []))
                    all_words.extend(st.session_state.blacklist_data.get('simple_replacements', {}).keys())
                    export_data = '\n'.join(sorted(all_words))
                    st.download_button(
                        "⬇️ Download Text",
                        export_data,
                        "blacklisted_words.txt",
                        "text/plain"
                    )
                elif export_format == "CSV":
                    csv_lines = ["Forbidden,Replacement"]
                    for group in st.session_state.blacklist_data.get('word_groups', {}).values():
                        words = group.get('words', [])
                        replacements = group.get('replacements', [])
                        if words and replacements:
                            for word in words:
                                csv_lines.append(f"{word},{replacements[0]}")
                    for forbidden, replacement in st.session_state.blacklist_data.get('simple_replacements', {}).items():
                        csv_lines.append(f"{forbidden},{replacement}")
                    export_data = '\n'.join(csv_lines)
                    st.download_button(
                        "⬇️ Download CSV",
                        export_data,
                        "word_replacements.csv",
                        "text/csv"
                    )

# Check API keys if available
if APIS_AVAILABLE:
    api_valid, api_message = validate_api_keys()
else:
    api_valid = False
    api_message = "Core modules not available - running in demo mode"

# Sidebar navigation
st.sidebar.title("📝 Gcore Content System")

# Mode Selection in Sidebar
st.sidebar.markdown("### 🎯 Select Mode")
mode_options = [
    "📝 New Content",
    "🔧 Content Optimization",
    "🚫 AI Word Manager",
    "⚙️ Settings"
]

selected_mode = st.sidebar.radio(
    "Choose your workflow:",
    mode_options,
    index=mode_options.index(st.session_state.active_mode) if st.session_state.active_mode in mode_options else 0,
    label_visibility="collapsed"
)

# Update session state
st.session_state.active_mode = selected_mode

st.sidebar.markdown("---")

# API Status
st.sidebar.markdown("### 📡 API Status")
if api_valid:
    st.sidebar.success("✅ APIs Connected")
    with st.sidebar.expander("View Details", expanded=False):
        if ANTHROPIC_API_KEY:
            st.caption("✓ Claude API")
        if PERPLEXITY_API_KEY:
            st.caption("✓ Perplexity API")
else:
    st.sidebar.warning("⚠️ Demo Mode")
    with st.sidebar.expander("Setup Required", expanded=False):
        if APIS_AVAILABLE:
            st.caption(api_message)
        else:
            st.caption("Running without API integration")

st.sidebar.markdown("---")

# Main content area - Title based on selected mode
if selected_mode == "📝 New Content":
    st.title("📝 New Content Generation")
elif selected_mode == "🔧 Content Optimization":
    st.title("🔧 Content Optimization")
elif selected_mode == "🚫 AI Word Manager":
    st.title("🚫 AI Word Manager")
elif selected_mode == "⚙️ Settings":
    st.title("⚙️ System Settings")

# Content based on selected mode
if selected_mode == "📝 New Content":
    # NEW CONTENT WORKFLOW
    st.header("Create New Content")
    
    # Workflow steps for new content
    new_content_steps = {
        1: "📋 Content Brief",
        2: "🔍 Research",  
        3: "✍️ Generate",
        4: "✅ Quality Check",
        5: "📤 Export"
    }
    
    # Progress indicator
    progress_cols = st.columns(5)
    for i, (step_num, step_name) in enumerate(new_content_steps.items()):
        with progress_cols[i]:
            if st.session_state.active_mode == "📝 New Content":
                if step_num < st.session_state.current_step:
                    st.success(f"✓ {step_name}")
                elif step_num == st.session_state.current_step:
                    st.info(f"→ {step_name}")
                else:
                    st.text(f"  {step_name}")
    
    st.markdown("---")
    
    # Step content based on current step
    if st.session_state.current_step == 1:
        st.subheader("Step 1: Create Content Brief")
        
        # Primary keyword input
        primary_keyword = st.text_input(
            "Primary Keyword/Topic",
            value=st.session_state.content_brief.get('primary_keyword', ''),
            placeholder="e.g., CDN caching, Edge computing benefits",
            key="new_content_primary_keyword"
        )
        st.session_state.content_brief['primary_keyword'] = primary_keyword
        
        if primary_keyword:
            st.info(f"✨ An introduction will be auto-generated for **{primary_keyword}**")
        
        # Heading structure builder
        st.subheader("Heading Structure")
        
        section_functions = load_section_functions()
        function_options = get_function_options(section_functions)
        
        # Template loading section
        col_template, col_clear = st.columns([2, 1])
        with col_template:
            if st.button("📋 Load Cloud Security Template", type="secondary", use_container_width=True):
                # Pre-defined template based on cloud security article structure
                template_headings = [
                    {"text": "What is {topic}?", "level": "H2", "function": "generate_definition"},
                    {"text": "How does {topic} work?", "level": "H2", "function": "generate_how"},
                    {"text": "What are the main {topic} challenges?", "level": "H2", "function": "generate_listicle"},
                    {"text": "What are the essential {topic} technologies and tools?", "level": "H2", "function": "generate_listicle"},
                    {"text": "What are the key benefits of {topic}?", "level": "H2", "function": "generate_listicle"},
                    {"text": "How to implement {topic} best practices?", "level": "H2", "function": "generate_how_list"},
                    {"text": "Frequently asked questions", "level": "H2", "function": "generate_faq_intro"},
                    {"text": "What's the difference between {topic} and traditional approaches?", "level": "H3", "function": "generate_differences"},
                    {"text": "Is {topic} more secure?", "level": "H3", "function": "generate_yes_no_answer"},
                    {"text": "What is {topic} posture management?", "level": "H3", "function": "generate_definition"},
                    {"text": "How does Zero Trust apply to {topic}?", "level": "H3", "function": "generate_faq_answer"},
                    {"text": "What compliance standards apply?", "level": "H3", "function": "generate_faq_answer"},
                    {"text": "How much does {topic} cost?", "level": "H3", "function": "generate_how_stats_answer"},
                    {"text": "What happens during a {topic} breach?", "level": "H3", "function": "generate_faq_answer"}
                ]
                
                # Replace {topic} with the primary keyword if available
                keyword = st.session_state.content_brief.get('primary_keyword', 'topic').lower()
                for heading in template_headings:
                    heading['text'] = heading['text'].replace('{topic}', keyword)
                
                st.session_state.content_brief['headings'] = template_headings
                st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                st.session_state.content_brief['headings'] = []
                st.rerun()
        
        # Add new heading
        with st.expander("➕ Add New Heading", expanded=True):
            col_text, col_level, col_function = st.columns([3, 1, 2])
            with col_text:
                new_heading = st.text_input("Heading Text", placeholder="e.g., What is CDN caching?", key="new_heading_text")
            with col_level:
                heading_level = st.selectbox("Level", ["H2", "H3", "H4"], index=0, key="new_heading_level")
            with col_function:
                # Check if we're in FAQ context
                in_faq_section = False
                
                if 'headings' in st.session_state.content_brief and heading_level == 'H3':
                    # Check if the last H2 was an FAQ section
                    for heading in reversed(st.session_state.content_brief['headings']):
                        if heading['level'] == 'H2':
                            heading_text_lower = heading['text'].lower()
                            if any(faq_keyword in heading_text_lower for faq_keyword in ['faq', 'frequently asked', 'common questions']):
                                in_faq_section = True
                            break
                
                # Show FAQ detection hint
                if in_faq_section and heading_level == 'H3':
                    st.caption("💡 FAQ mode detected - will use FAQ answer format")
                
                # Prepare context for auto-detection
                detection_context = {
                    'in_faq_section': in_faq_section,
                    'heading_level': heading_level
                }
                
                # Auto-detect function based on heading and context
                default_function = auto_detect_function(new_heading, section_functions, detection_context) if new_heading else "generate_definition"
                selected_function = st.selectbox(
                    "Function",
                    options=list(function_options.keys()),
                    format_func=lambda x: function_options.get(x, x),
                    index=list(function_options.keys()).index(default_function) if default_function in function_options else 0,
                    key="new_heading_function"
                )
            
            if st.button("Add Heading", type="primary"):
                if new_heading:
                    if 'headings' not in st.session_state.content_brief:
                        st.session_state.content_brief['headings'] = []
                    
                    st.session_state.content_brief['headings'].append({
                        'text': new_heading,
                        'level': heading_level,
                        'function': selected_function
                    })
                    st.success(f"Added: {new_heading}")
                    st.rerun()
        
        # Display current headings with reordering controls
        if st.session_state.content_brief.get('headings'):
            st.subheader("Current Structure")
            st.caption("💡 Use ↑↓ arrows to reorder headings")
            
            headings = st.session_state.content_brief['headings']
            
            for i, heading in enumerate(headings):
                col1, col2, col3, col4, col5 = st.columns([2.5, 2, 1, 1, 1])
                
                with col1:
                    # Level indicator and heading text
                    level_emoji = {"H1": "🔷", "H2": "🔹", "H3": "▪️"}.get(heading['level'], "•")
                    st.text(f"{level_emoji} {heading['level']}: {heading['text']}")
                
                with col2:
                    # Function type
                    st.caption(function_options.get(heading.get('function', 'generate_definition'), 'General'))
                
                with col3:
                    # Move up button
                    if i > 0:  # Not the first item
                        if st.button("↑", key=f"up_{i}", help="Move heading up"):
                            # Swap with previous item
                            headings[i], headings[i-1] = headings[i-1], headings[i]
                            st.session_state.content_brief['headings'] = headings
                            st.rerun()
                    else:
                        st.write("")  # Empty space for alignment
                
                with col4:
                    # Move down button  
                    if i < len(headings) - 1:  # Not the last item
                        if st.button("↓", key=f"down_{i}", help="Move heading down"):
                            # Swap with next item
                            headings[i], headings[i+1] = headings[i+1], headings[i]
                            st.session_state.content_brief['headings'] = headings
                            st.rerun()
                    else:
                        st.write("")  # Empty space for alignment
                
                with col5:
                    # Delete button
                    if st.button("🗑️", key=f"delete_{i}", help="Delete heading"):
                        st.session_state.content_brief['headings'].pop(i)
                        st.rerun()
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col2:
            if primary_keyword and st.session_state.content_brief.get('headings'):
                if st.button("Continue to Research →", type="primary"):
                    st.session_state.current_step = 2
                    st.rerun()
    
    elif st.session_state.current_step == 2:
        st.header("🔍 Step 2: Research Topic")
        
        st.info(f"**Topic**: {st.session_state.content_brief['primary_keyword']}")
        
        use_perplexity = st.checkbox("Use Perplexity for research", value=PERPLEXITY_API_KEY is not None)
        
        if st.button("🚀 Start Research", type="primary"):
            with st.spinner("Researching topic..."):
                if use_perplexity and APIS_AVAILABLE:
                    research_engine = ResearchEngine()
                    research_result = research_engine.research_topic(
                        st.session_state.content_brief['primary_keyword'],
                        st.session_state.content_brief['headings'],
                        context="Focus on Gcore-relevant information about edge computing, CDN, and cloud infrastructure"
                    )
                    st.session_state.content_brief['research_data'] = research_result
                else:
                    # Fallback mock data
                    st.session_state.content_brief['research_data'] = {
                        'status': 'completed',
                        'timestamp': datetime.now().isoformat(),
                        'topic': st.session_state.content_brief['primary_keyword'],
                        'data': {
                            'facts': [
                                f"Key fact about {st.session_state.content_brief['primary_keyword']}",
                                "Edge computing reduces latency by processing data closer to users",
                                "CDN improves performance by caching content globally",
                                "Cloud infrastructure enables scalable applications"
                            ],
                            'statistics': [
                                {'text': "99.99% uptime SLA for enterprise services"},
                                {'text': "30ms average global latency"},
                                {'text': "180+ Points of Presence worldwide"}
                            ],
                            'key_points': [
                                "Scalability is essential for modern applications",
                                "Performance optimization reduces costs",
                                "Security must be built-in from the start"
                            ],
                            'examples': ["E-commerce platforms", "Video streaming services", "Gaming applications"],
                            'sources': []
                        }
                    }
                st.success("✅ Research completed!")
                st.rerun()
        
        if st.session_state.content_brief.get('research_data'):
            st.subheader("Research Results")
            
            research = st.session_state.content_brief['research_data'].get('data', {})
            
            # Display quality score if available
            if research.get('quality_score'):
                score = research['quality_score']['overall']
                rating = research['quality_score']['rating']
                st.metric("Research Quality", f"{score}/100 - {rating}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Facts
                if research.get('facts'):
                    st.markdown("### 📌 Key Facts")
                    facts_to_show = research['facts'][:5] if isinstance(research['facts'][0], dict) else [{'text': f} for f in research['facts'][:5]]
                    for fact in facts_to_show:
                        fact_text = fact.get('text', fact) if isinstance(fact, dict) else fact
                        st.markdown(f"• {fact_text}")
                
                # Statistics
                if research.get('statistics'):
                    st.markdown("### 📊 Statistics")
                    stats_to_show = research['statistics'][:5] if isinstance(research['statistics'][0], dict) else [{'text': s} for s in research['statistics'][:5]]
                    for stat in stats_to_show:
                        stat_text = stat.get('text', stat) if isinstance(stat, dict) else stat
                        st.markdown(f"• {stat_text}")
            
            with col2:
                # Key Points
                if research.get('key_points'):
                    st.markdown("### 🎯 Key Points")
                    for point in research['key_points'][:5]:
                        st.markdown(f"• {point}")
                
                # Examples
                if research.get('examples'):
                    st.markdown("### 💡 Examples")
                    for example in research['examples'][:5]:
                        st.markdown(f"• {example}")
            
            # Sources
            if research.get('sources'):
                with st.expander("📚 View Sources"):
                    for source in research['sources'][:10]:
                        if isinstance(source, dict):
                            st.markdown(f"• [{source.get('title', 'Source')}]({source.get('url', '#')})")
                        else:
                            st.markdown(f"• {source}")
        
        # Navigation
        st.markdown("---")
        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("← Back to Brief", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()
        with col_right:
            if st.button("Continue to Generate →", type="primary", use_container_width=True):
                if st.session_state.content_brief.get('research_data'):
                    st.session_state.current_step = 3
                    st.rerun()
                else:
                    st.warning("Please complete research first")
    
    elif st.session_state.current_step == 3:
        st.header("✍️ Step 3: Generate Content")
        
        st.info(f"**Topic**: {st.session_state.content_brief['primary_keyword']}")
        
        # Internal Links Configuration - DISABLED (broken functionality)
        enable_internal_links = False  # Permanently disabled
        
        # Hidden internal links section - uncomment to re-enable
        # with st.expander("🔗 Internal Link Settings", expanded=False):
        #     enable_internal_links = st.checkbox(
        #         "Enable Internal Link Suggestions", 
        #         value=False,
        #         help="Automatically suggest relevant Gcore product pages and learning content links"
        #     )
        
        if False:  # Disabled block
            if enable_internal_links and APIS_AVAILABLE:
                # Show link database statistics
                try:
                    from core.link_manager import LinkManager
                    link_manager = LinkManager()
                    stats = link_manager.get_statistics()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Links", stats['total_links'])
                    with col2:
                        st.metric("Product Pages", stats['product_services'] + stats['product_solutions'] + stats['product_features'])
                    with col3:
                        st.metric("Learning Content", stats['learning_content'])
                except Exception as e:
                    st.info("Internal link database not available. Links will be suggested during generation.")
        # End disabled internal links block
        
        # CTA Product Selection
        with st.expander("🎯 CTA Product Settings", expanded=False):
            st.markdown("**Configure product CTAs for your content**")
            
            if APIS_AVAILABLE:
                try:
                    from core.product_loader import product_loader
                    
                    # Get available products
                    products = product_loader.get_product_list()
                    
                    # Auto-suggest relevant products based on content brief
                    article_keywords = st.session_state.content_brief['primary_keyword'].lower().split()
                    suggested_products = product_loader.suggest_relevant_products(article_keywords)
                    
                    # Product selection
                    product_options = ["None (No CTA)"] + [f"{p['name']} - {p['tagline']}" for p in products]
                    product_ids = ["none"] + [p['id'] for p in products]
                    
                    # Default selection - use first suggested product if available
                    default_idx = 0
                    if suggested_products:
                        try:
                            default_idx = product_ids.index(suggested_products[0])
                        except ValueError:
                            default_idx = 0
                    
                    selected_product_idx = st.selectbox(
                        "Select Product for CTA",
                        range(len(product_options)),
                        format_func=lambda x: product_options[x],
                        index=default_idx,
                        help="Choose which Gcore product to feature in call-to-action sections"
                    )
                    
                    selected_product_id = product_ids[selected_product_idx]
                    
                    # Store the selection in session state
                    st.session_state.content_brief['selected_product'] = selected_product_id
                    
                    if selected_product_id != "none":
                        # Show product info and available CTA templates
                        product_data = product_loader.get_product(selected_product_id)
                        if product_data:
                            st.success(f"✅ **{product_data['name']}** selected")
                            st.caption(f"URL: {product_data.get('url', 'N/A')}")
                            
                            # Show available CTA templates
                            cta_templates = product_loader.get_cta_templates(selected_product_id)
                            if cta_templates:
                                st.write("**Available CTA Templates:**")
                                for template_name, template_text in list(cta_templates.items())[:3]:
                                    with st.expander(f"📝 {template_name.replace('_', ' ').title()}", expanded=False):
                                        st.write(template_text[:200] + "..." if len(template_text) > 200 else template_text)
                    else:
                        st.info("No product CTA will be included")
                        
                    # Show suggestions if products were auto-detected
                    if suggested_products and len(suggested_products) > 1:
                        st.write("**💡 Other Suggested Products:**")
                        for product_id in suggested_products[1:3]:  # Show top 2 alternatives
                            product = product_loader.get_product(product_id)
                            if product:
                                st.caption(f"• {product['name']}: {product.get('tagline', '')}")
                
                except Exception as e:
                    st.warning("Product data not available. CTAs will use basic templates.")
                    st.session_state.content_brief['selected_product'] = "none"
            else:
                st.warning("API not available. Product CTAs disabled.")
                st.session_state.content_brief['selected_product'] = "none"
        
        # Gcore context handled by dedicated CTA sections - no need to include globally
        include_gcore = False
        
        if st.button("🚀 Generate Content", type="primary"):
            with st.spinner("Generating content..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                if APIS_AVAILABLE:
                    from core.content_generator import ContentGenerator
                    # Use session-persistent generator to maintain fact tracking
                    if 'content_generator' not in st.session_state:
                        st.session_state.content_generator = ContentGenerator(enable_internal_links=enable_internal_links)
                    generator = st.session_state.content_generator
                    
                    # Reset fact tracking for new content generation
                    generator.reset_fact_tracking()
                    
                    # Generate introduction using dedicated method
                    status_text.text("Generating introduction...")
                    intro_result = generator.generate_introduction(
                        topic=st.session_state.content_brief['primary_keyword'],
                        headings=st.session_state.content_brief.get('headings', []),
                        research_data=st.session_state.content_brief.get('research_data'),
                        include_gcore=include_gcore
                    )
                    
                    if intro_result['status'] == 'success' and intro_result.get('content'):
                        st.session_state.content_brief['introduction'] = intro_result['content']
                    else:
                        # Generate proper fallback introduction
                        keyword = st.session_state.content_brief['primary_keyword']
                        fallback_intro = f"{keyword} is a fundamental aspect of modern technology infrastructure that organizations must understand and implement effectively. This comprehensive guide explores the essential concepts, implementation strategies, and best practices for {keyword.lower()}. By understanding these key principles, organizations can make informed decisions and optimize their approach to {keyword.lower()} challenges."
                        st.session_state.content_brief['introduction'] = fallback_intro
                    
                    # Generate content for each heading
                    total_headings = len(st.session_state.content_brief['headings'])
                    generated_content = {}
                    
                    for idx, heading in enumerate(st.session_state.content_brief['headings']):
                        heading_text = heading['text']
                        function_name = heading.get('function', 'generate_definition')
                        
                        progress = (idx + 1) / (total_headings + 1)
                        progress_bar.progress(progress)
                        status_text.text(f"Generating: {heading_text}...")
                        
                        # Build generation context
                        generation_context = {
                            'include_gcore': include_gcore,
                            'heading_level': heading['level'],
                            'pattern': heading.get('pattern'),
                            'gcore_product': st.session_state.content_brief.get('selected_product', 'cdn'),
                            'gcore_features': []  # Can be extended later for feature-specific CTAs
                        }
                        
                        result = generator.generate_section(
                            heading=heading_text,
                            research_data=st.session_state.content_brief.get('research_data'),
                            parent_context=generation_context,
                            include_gcore=include_gcore,
                            function_name=function_name,
                            include_internal_links=enable_internal_links
                        )
                        
                        if result['status'] == 'success':
                            generated_content[heading_text] = {
                                'content': result['content'],
                                'word_count': result.get('word_count', 0),
                                'function': function_name,
                                'internal_links': result.get('internal_links', [])
                            }
                        else:
                            generated_content[heading_text] = {
                                'content': f"Content for {heading_text}",
                                'word_count': 10,
                                'function': function_name
                            }
                    
                    st.session_state.content_brief['generated_content'] = generated_content
                    progress_bar.progress(1.0)
                    status_text.text("Generation complete!")
                    st.success("✅ Content generated successfully!")
                else:
                    # Demo mode - generate placeholder content
                    topic = st.session_state.content_brief['primary_keyword']
                    st.session_state.content_brief['introduction'] = f"{topic} is a technology that enables organizations to optimize their digital infrastructure. This approach provides significant benefits in terms of scalability and performance."
                    
                    generated_content = {}
                    for heading in st.session_state.content_brief['headings']:
                        heading_text = heading['text']
                        generated_content[heading_text] = {
                            'content': f"This is demo content for {heading_text}. In production, this would contain AI-generated content based on your research and specifications.",
                            'word_count': 50,
                            'function': heading.get('function', 'generate_definition')
                        }
                    
                    st.session_state.content_brief['generated_content'] = generated_content
                    st.success("✅ Demo content generated!")
                
                st.rerun()
        
        # Display generated content if available
        if st.session_state.content_brief.get('generated_content') or st.session_state.content_brief.get('introduction'):
            st.subheader("Generated Content Preview")
            
            # Display introduction
            if st.session_state.content_brief.get('introduction'):
                with st.expander("📝 Introduction", expanded=True):
                    st.write(st.session_state.content_brief['introduction'])
            
            # Display section content
            for heading in st.session_state.content_brief.get('headings', []):
                if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                    content_data = st.session_state.content_brief['generated_content'][heading['text']]
                    with st.expander(f"{heading['level']}: {heading['text']}", expanded=False):
                        st.write(content_data['content'])
                        
                        # Display internal links if available
                        if content_data.get('internal_links'):
                            st.markdown("**🔗 Internal Links Suggested:**")
                            for link in content_data['internal_links']:
                                st.markdown(f"- [{link['anchor_text']}](https://gcore.com{link['url']}) (relevance: {link['relevance_score']:.2f})")
                        
                        st.caption(f"Words: {content_data.get('word_count', 0)} | Function: {content_data.get('function', 'N/A')}")
        
        # Navigation
        st.markdown("---")
        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("← Back to Research", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
        with col_right:
            if st.button("Continue to Quality Check →", type="primary", use_container_width=True):
                if st.session_state.content_brief.get('generated_content'):
                    st.session_state.current_step = 4
                    st.rerun()
                else:
                    st.warning("Please generate content first")
    
    elif st.session_state.current_step == 4:
        st.subheader("Step 4: Quality Check")
        
        # Check if we have content to analyze
        if not st.session_state.content_brief.get('generated_content'):
            st.warning("Please generate content first")
            if st.button("← Back to Generate"):
                st.session_state.current_step = 3
                st.rerun()
        else:
            # Import quality checker
            if APIS_AVAILABLE:
                from core.quality_checker import QualityChecker, fix_ai_words
                from core.content_editor import ContentEditor
                quality_checker = QualityChecker()
                editor = ContentEditor()
            
            # Combine all content for analysis
            full_content = []
            
            # Add introduction
            if st.session_state.content_brief.get('introduction'):
                full_content.append(st.session_state.content_brief['introduction'])
            
            # Add all generated sections
            for heading in st.session_state.content_brief.get('headings', []):
                if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                    content_data = st.session_state.content_brief['generated_content'][heading['text']]
                    full_content.append(f"## {heading['text']}\n\n{content_data['content']}")
            
            combined_content = '\n\n'.join(full_content)
            
            # Run quality check button
            if st.button("🔍 Run Quality Analysis", type="primary"):
                with st.spinner("Analyzing content quality..."):
                    quality_results = {}
                    overall_issues = []
                    
                    if APIS_AVAILABLE:
                        # Check introduction quality
                        if st.session_state.content_brief.get('introduction'):
                            intro_quality = quality_checker.check_quality(
                                st.session_state.content_brief['introduction'],
                                st.session_state.content_brief['primary_keyword'],
                                'introduction'
                            )
                            quality_results['Introduction'] = intro_quality
                        
                        # Check each section
                        for heading in st.session_state.content_brief.get('headings', []):
                            if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                                content_data = st.session_state.content_brief['generated_content'][heading['text']]
                                section_quality = quality_checker.check_quality(
                                    content_data['content'],
                                    heading['text'],
                                    content_data.get('function')
                                )
                                quality_results[heading['text']] = section_quality
                                
                                # Collect overall issues
                                if section_quality['issues']:
                                    overall_issues.extend(section_quality['issues'])
                    else:
                        # Demo quality results
                        quality_results = {
                            'Introduction': {
                                'overall_score': 85,
                                'checks': {
                                    'ai_words': {'found': True, 'count': 3, 'words': ['leverage', 'utilize', 'delve']},
                                    'seo': {'score': 90, 'metrics': {'keyword_density': 2.5}},
                                    'readability': {'score': 85, 'avg_sentence_length': 18}
                                }
                            }
                        }
                    
                    st.session_state.content_brief['quality_scores'] = quality_results
                    st.success("✅ Quality analysis complete!")
                    st.rerun()
            
            # Display quality results if available
            if st.session_state.content_brief.get('quality_scores'):
                quality_scores = st.session_state.content_brief['quality_scores']
                
                # Create visual quality summary with progress bars
                st.markdown("### 🎯 Quality Assessment Dashboard")
                
                # Calculate overall statistics
                all_scores = [score['overall_score'] for score in quality_scores.values()]
                avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
                
                # Overall quality progress bar
                score_color = "green" if avg_score >= 80 else "orange" if avg_score >= 60 else "red"
                st.progress(avg_score / 100, text=f"Overall Quality Score: {avg_score:.1f}%")
                
                # Overall metrics
                st.markdown("### 📊 Overall Quality Metrics")
                
                # Count total issues
                total_ai_words = sum(
                    score.get('checks', {}).get('ai_words', {}).get('count', 0)
                    for score in quality_scores.values()
                )
                
                # Count internal links if they were generated
                total_internal_links = 0
                for heading in st.session_state.content_brief.get('headings', []):
                    if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                        content_data = st.session_state.content_brief['generated_content'][heading['text']]
                        total_internal_links += len(content_data.get('internal_links', []))
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    score_color = "🟢" if avg_score >= 80 else "🟡" if avg_score >= 60 else "🔴"
                    st.metric(f"{score_color} Average Quality", f"{avg_score:.1f}%")
                with col2:
                    ai_color = "🔴" if total_ai_words > 10 else "🟡" if total_ai_words > 5 else "🟢"
                    st.metric(f"{ai_color} AI Words Found", total_ai_words)
                with col3:
                    link_color = "🟢" if total_internal_links >= 3 else "🟡" if total_internal_links >= 1 else "🔴"
                    st.metric(f"{link_color} Internal Links", total_internal_links)
                with col4:
                    sections_count = len(quality_scores)
                    st.metric("Sections Analyzed", sections_count)
                with col5:
                    high_quality = len([s for s in all_scores if s >= 80])
                    st.metric("High Quality", f"{high_quality}/{sections_count}")
                
                # Section-by-section breakdown
                st.markdown("### 📝 Section Quality Breakdown")
                
                for section_name, quality_data in quality_scores.items():
                    score = quality_data['overall_score']
                    score_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                    
                    with st.expander(f"{score_emoji} {section_name} - Quality: {score}%", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Quality checks
                            st.markdown("**Quality Checks:**")
                            
                            # AI Words
                            ai_words = quality_data.get('checks', {}).get('ai_words', {})
                            if ai_words.get('found'):
                                st.error(f"🤖 AI Words: {ai_words.get('count', 0)} found")
                                if ai_words.get('words'):
                                    st.caption(f"Words: {', '.join(ai_words['words'][:5])}")
                            else:
                                st.success("✓ No AI words detected")
                            
                            # SEO
                            seo = quality_data.get('checks', {}).get('seo', {})
                            if seo.get('score', 0) >= 80:
                                st.success(f"✓ SEO Score: {seo.get('score', 0)}%")
                            else:
                                st.warning(f"⚠ SEO Score: {seo.get('score', 0)}%")
                            if seo.get('metrics'):
                                st.caption(f"Keyword density: {seo['metrics'].get('keyword_density', 0):.1f}%")
                            
                            # Readability
                            readability = quality_data.get('checks', {}).get('readability', {})
                            if readability.get('score', 0) >= 80:
                                st.success(f"✓ Readability: {readability.get('score', 0)}%")
                            else:
                                st.warning(f"⚠ Readability: {readability.get('score', 0)}%")
                            if readability.get('avg_sentence_length'):
                                st.caption(f"Avg sentence: {readability['avg_sentence_length']:.1f} words")
                        
                        with col2:
                            # Issues and suggestions
                            st.markdown("**Issues & Suggestions:**")
                            
                            issues = quality_data.get('issues', [])
                            if issues:
                                for issue in issues[:5]:
                                    st.warning(f"• {issue}")
                            else:
                                st.success("No major issues found")
                            
                            suggestions = quality_data.get('suggestions', [])
                            if suggestions:
                                st.markdown("**Improvements:**")
                                for suggestion in suggestions[:3]:
                                    st.info(f"💡 {suggestion}")
                
                # Quick Fix Options
                st.markdown("---")
                st.markdown("### 🔧 Quick Fix Options")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🤖 Remove All AI Words", use_container_width=True):
                        if APIS_AVAILABLE:
                            with st.spinner("Removing AI words..."):
                                # Fix introduction
                                if st.session_state.content_brief.get('introduction'):
                                    fixed_intro, _ = fix_ai_words(st.session_state.content_brief['introduction'])
                                    st.session_state.content_brief['introduction'] = fixed_intro
                                
                                # Fix all sections
                                for heading in st.session_state.content_brief.get('headings', []):
                                    if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                                        content = st.session_state.content_brief['generated_content'][heading['text']]['content']
                                        fixed_content, _ = fix_ai_words(content)
                                        st.session_state.content_brief['generated_content'][heading['text']]['content'] = fixed_content
                                
                                st.success("✅ AI words removed!")
                                st.rerun()
                        else:
                            st.info("Feature available with API integration")
                
                with col2:
                    if st.button("📝 Improve Readability", use_container_width=True):
                        if APIS_AVAILABLE:
                            with st.spinner("Improving readability..."):
                                # Apply readability fixes using content editor
                                for heading in st.session_state.content_brief.get('headings', []):
                                    if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                                        content = st.session_state.content_brief['generated_content'][heading['text']]['content']
                                        # Split long sentences
                                        fixed_content = editor.apply_fix(content, 'split_long_sentences')
                                        st.session_state.content_brief['generated_content'][heading['text']]['content'] = fixed_content
                                
                                st.success("✅ Readability improved!")
                                st.rerun()
                        else:
                            st.info("Feature available with API integration")
                
                with col3:
                    if st.button("🎯 Fix All Issues", use_container_width=True):
                        if APIS_AVAILABLE:
                            with st.spinner("Applying all fixes..."):
                                # Apply all fixes
                                for heading in st.session_state.content_brief.get('headings', []):
                                    if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                                        content = st.session_state.content_brief['generated_content'][heading['text']]['content']
                                        # Apply multiple fixes
                                        fixed_content = editor.batch_fix_content(content, [
                                            'remove_all_ai_words',
                                            'split_long_sentences',
                                            'remove_promotional'
                                        ])
                                        st.session_state.content_brief['generated_content'][heading['text']]['content'] = fixed_content
                                
                                st.success("✅ All fixes applied!")
                                st.rerun()
                        else:
                            st.info("Feature available with API integration")
                
                # Quality Gate
                st.markdown("---")
                if avg_score < 70:
                    st.warning("⚠️ **Quality Gate**: Average score is below 70%. Consider applying fixes before exporting.")
                else:
                    st.success("✅ **Quality Gate Passed**: Content meets quality standards.")
            
            # Navigation
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("← Back to Generate"):
                    st.session_state.current_step = 3
                    st.rerun()
            with col3:
                # Only allow export if quality check has been run
                can_export = st.session_state.content_brief.get('quality_scores') is not None
                if st.button("Continue to Export →", type="primary", disabled=not can_export):
                    st.session_state.current_step = 5
                    st.rerun()
                if not can_export:
                    st.caption("Run quality check before exporting")
    
    elif st.session_state.current_step == 5:
        st.subheader("Step 5: Export Content")
        
        # Source validation function
        def validate_source_attribution(content_sections, research_sources):
            """Validate that all cited sources in content exist in research sources"""
            validation_errors = []
            research_source_names = set()
            
            # Extract source names from research
            if research_sources:
                for source in research_sources:
                    if isinstance(source, dict):
                        title = source.get('title', '').lower()
                        url = source.get('url', '')
                        if title:
                            research_source_names.add(title)
                        if url:
                            # Extract domain name
                            domain = url.split('//')[1].split('/')[0] if '//' in url else url
                            research_source_names.add(domain.replace('www.', '').lower())
            
            # Check for fabricated sources in content
            forbidden_sources = [
                'market research future', 'fortune business insights',
                'according to research', 'according to market research',
                'according to industry analysis', 'according to studies'
            ]
            
            all_content_text = ""
            for section in content_sections:
                content = section.get('content', '')
                if isinstance(content, str):
                    all_content_text += content.lower() + " "
            
            for forbidden in forbidden_sources:
                if forbidden in all_content_text:
                    validation_errors.append(f"⚠️ Found fabricated source: '{forbidden}' - not in research data")
            
            return validation_errors
        
        # Check if we have content to export
        if not st.session_state.content_brief.get('generated_content'):
            st.warning("Please generate content first")
            if st.button("← Back to Generate"):
                st.session_state.current_step = 3
                st.rerun()
        else:
            # Prepare full content for export
            # Build complete content structure
            export_content = {
                'metadata': {
                    'primary_keyword': st.session_state.content_brief.get('primary_keyword', ''),
                    'generated_date': datetime.now().isoformat(),
                    'quality_scores': st.session_state.content_brief.get('quality_scores', {}),
                    'word_count': 0
                },
                'content': {
                    'introduction': st.session_state.content_brief.get('introduction', ''),
                    'sections': []
                }
            }
            
            # Calculate total word count
            total_words = len(st.session_state.content_brief.get('introduction', '').split())
            
            # Add sections
            for heading in st.session_state.content_brief.get('headings', []):
                if heading['text'] in st.session_state.content_brief.get('generated_content', {}):
                    content_data = st.session_state.content_brief['generated_content'][heading['text']]
                    export_content['content']['sections'].append({
                        'heading': heading['text'],
                        'level': heading['level'],
                        'content': content_data['content'],
                        'word_count': content_data.get('word_count', len(content_data['content'].split())),
                        'function': content_data.get('function', '')
                    })
                    total_words += content_data.get('word_count', len(content_data['content'].split()))
            
            export_content['metadata']['word_count'] = total_words
            
            # Display export preview
            st.markdown("### 📄 Content Preview")
            
            # Show metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Words", total_words)
            with col2:
                sections_count = len(export_content['content']['sections'])
                st.metric("Sections", sections_count + 1)  # +1 for introduction
            with col3:
                avg_quality = 0
                if st.session_state.content_brief.get('quality_scores'):
                    scores = [s['overall_score'] for s in st.session_state.content_brief['quality_scores'].values()]
                    avg_quality = sum(scores) / len(scores) if scores else 0
                st.metric("Avg Quality", f"{avg_quality:.1f}%")
            
            # Source validation function (defined inline to avoid scope issues)
            def validate_source_attribution_inline(content_sections, research_sources):
                """Validate that all cited sources in content exist in research sources"""
                validation_errors = []
                
                # Check for fabricated sources in content (comprehensive list)
                forbidden_sources = [
                    'market research future', 'fortune business insights',
                    'according to research', 'according to market research', 
                    'according to industry analysis', 'according to studies',
                    'according to reports', 'according to data',
                    'market research data', 'market research reports',
                    'research shows', 'studies indicate', 'data suggests',
                    'based on research', 'research findings'
                ]
                
                all_content_text = ""
                for section in content_sections:
                    content = section.get('content', '')
                    if isinstance(content, str):
                        all_content_text += content.lower() + " "
                
                for forbidden in forbidden_sources:
                    if forbidden in all_content_text:
                        validation_errors.append(f"⚠️ Found fabricated source: '{forbidden}' - not in research data")
                
                return validation_errors
            
            # Validate source attribution before export
            research_data = st.session_state.content_brief.get('research_data', {})
            research_sources = research_data.get('data', {}).get('sources', [])
            content_sections = export_content['content']['sections']
            
            validation_errors = validate_source_attribution_inline(content_sections, research_sources)
            if validation_errors:
                st.error("⚠️ **Source Attribution Issues Found:**")
                for error in validation_errors:
                    st.error(error)
                st.warning("These issues may indicate fabricated sources that don't exist in the research data. Please review the content before export.")
            
            # Export format selection
            st.markdown("---")
            st.markdown("### 📤 Export Options")
            
            export_format = st.selectbox(
                "Select Export Format",
                ["Markdown (.md)", "HTML (.html)", "Plain Text (.txt)", "JSON (.json)", "Google Docs Format"],
                help="Choose the format that best suits your needs"
            )
            
            # Add metadata options
            st.markdown("**Include in Export:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                include_metadata = st.checkbox("Metadata", value=True, help="Include generation date, keywords, etc.")
            with col2:
                include_quality = st.checkbox("Quality Scores", value=True, help="Include quality analysis results")
            with col3:
                include_sources = st.checkbox("Research Sources", value=True, help="Include research references")
            
            # Generate export content based on format
            def generate_markdown():
                """Generate Markdown format"""
                md_content = []
                
                # Add metadata as comments
                if include_metadata:
                    md_content.append(f"<!-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -->")
                    md_content.append(f"<!-- Primary Keyword: {export_content['metadata']['primary_keyword']} -->")
                    md_content.append(f"<!-- Word Count: {export_content['metadata']['word_count']} -->")
                    if include_quality and avg_quality > 0:
                        md_content.append(f"<!-- Quality Score: {avg_quality:.1f}% -->")
                    md_content.append("")
                
                # Add title
                md_content.append(f"# {export_content['metadata']['primary_keyword'].title()}")
                md_content.append("")
                
                # Add introduction
                if export_content['content']['introduction']:
                    md_content.append(export_content['content']['introduction'])
                    md_content.append("")
                
                # Add sections
                for section in export_content['content']['sections']:
                    level = section['level']
                    if level == 'H1':
                        md_content.append(f"# {section['heading']}")
                    elif level == 'H2':
                        md_content.append(f"## {section['heading']}")
                    elif level == 'H3':
                        md_content.append(f"### {section['heading']}")
                    else:
                        md_content.append(f"## {section['heading']}")
                    
                    md_content.append("")
                    md_content.append(section['content'])
                    md_content.append("")
                
                # Add sources if available
                if include_sources and st.session_state.content_brief.get('research_data'):
                    research = st.session_state.content_brief['research_data'].get('data', {})
                    if research.get('sources'):
                        md_content.append("---")
                        md_content.append("")
                        md_content.append("## Sources")
                        md_content.append("")
                        for i, source in enumerate(research['sources'][:10], 1):
                            if isinstance(source, dict):
                                md_content.append(f"{i}. [{source.get('title', 'Source')}]({source.get('url', '#')})")
                            else:
                                md_content.append(f"{i}. {source}")
                
                return '\n'.join(md_content)
            
            def generate_html():
                """Generate HTML format"""
                html_parts = []
                
                # HTML header
                html_parts.append('<!DOCTYPE html>')
                html_parts.append('<html lang="en">')
                html_parts.append('<head>')
                html_parts.append('    <meta charset="UTF-8">')
                html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
                html_parts.append(f'    <title>{export_content["metadata"]["primary_keyword"].title()}</title>')
                
                if include_metadata:
                    html_parts.append(f'    <meta name="keywords" content="{export_content["metadata"]["primary_keyword"]}">')
                    html_parts.append(f'    <meta name="generated" content="{datetime.now().isoformat()}">')
                
                html_parts.append('    <style>')
                html_parts.append('        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; ')
                html_parts.append('               line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }')
                html_parts.append('        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }')
                html_parts.append('        h2 { color: #555; margin-top: 30px; }')
                html_parts.append('        h3 { color: #666; }')
                html_parts.append('        ul, ol { margin: 15px 0; padding-left: 30px; }')
                html_parts.append('        li { margin: 8px 0; line-height: 1.6; }')
                html_parts.append('        li strong { color: #333; }')
                html_parts.append('        p { margin: 15px 0; }')
                html_parts.append('        .metadata { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }')
                html_parts.append('        .metadata dl { margin: 0; }')
                html_parts.append('        .metadata dt { font-weight: bold; display: inline-block; width: 120px; }')
                html_parts.append('        .metadata dd { display: inline; margin: 0; }')
                html_parts.append('    </style>')
                html_parts.append('</head>')
                html_parts.append('<body>')
                
                # Metadata section
                if include_metadata:
                    html_parts.append('    <div class="metadata">')
                    html_parts.append('        <h3>Document Information</h3>')
                    html_parts.append('        <dl>')
                    html_parts.append(f'            <dt>Keyword:</dt><dd>{export_content["metadata"]["primary_keyword"]}</dd><br>')
                    html_parts.append(f'            <dt>Generated:</dt><dd>{datetime.now().strftime("%Y-%m-%d %H:%M")}</dd><br>')
                    html_parts.append(f'            <dt>Word Count:</dt><dd>{export_content["metadata"]["word_count"]}</dd><br>')
                    if include_quality and avg_quality > 0:
                        html_parts.append(f'            <dt>Quality Score:</dt><dd>{avg_quality:.1f}%</dd>')
                    html_parts.append('        </dl>')
                    html_parts.append('    </div>')
                
                # Main content
                html_parts.append(f'    <h1>{export_content["metadata"]["primary_keyword"].title()}</h1>')
                
                # Introduction - properly split into paragraphs
                if export_content['content']['introduction']:
                    intro_paragraphs = export_content['content']['introduction'].split('\n\n')
                    for para in intro_paragraphs:
                        if para.strip():
                            # Convert markdown bold to HTML
                            para_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para.strip())
                            html_parts.append(f'    <p>{para_html}</p>')
                
                # Sections
                for section in export_content['content']['sections']:
                    level = section['level']
                    tag = 'h1' if level == 'H1' else 'h2' if level == 'H2' else 'h3'
                    html_parts.append(f'    <{tag}>{section["heading"]}</{tag}>')
                    
                    # Convert content to paragraphs and lists
                    content = section['content']
                    
                    # First, split by double newlines for paragraphs
                    paragraphs = content.split('\n\n')
                    
                    # Process each paragraph - but handle lists specially
                    i = 0
                    while i < len(paragraphs):
                        para = paragraphs[i].strip()
                        if not para:
                            i += 1
                            continue
                            
                        # Check if this is a numbered list (starts with number and period)
                        if re.match(r'^\d+\.\s', para):
                            # Check for intro text before the list
                            intro_match = re.match(r'^(.+?)(?=\n?\d+\.\s)', para)
                            if intro_match and not intro_match.group(1).strip().startswith('1.'):
                                intro_text = intro_match.group(1).strip()
                                html_parts.append(f'    <p>{intro_text}</p>')
                            
                            # Collect all numbered items from this paragraph and subsequent ones
                            all_numbered_items = []
                            
                            # Extract items from current paragraph
                            numbered_items = re.findall(r'\d+\.\s+(.+?)(?=\n?\d+\.|$)', para, re.DOTALL)
                            all_numbered_items.extend(numbered_items)
                            
                            # Look ahead for more numbered items in next paragraphs
                            while i + 1 < len(paragraphs):
                                next_para = paragraphs[i + 1].strip()
                                if re.match(r'^\d+\.\s', next_para):
                                    # This is a continuation of the list
                                    more_items = re.findall(r'\d+\.\s+(.+?)(?=\n?\d+\.|$)', next_para, re.DOTALL)
                                    all_numbered_items.extend(more_items)
                                    i += 1
                                else:
                                    break
                            
                            # Now output all items in a single <ol>
                            if all_numbered_items:
                                html_parts.append('    <ol>')
                                for item in all_numbered_items:
                                    # Convert markdown bold to HTML and clean up
                                    item_text = item.strip()
                                    # Fix incomplete sentences
                                    if item_text.endswith('-') or item_text.endswith('affect'):
                                        # Try to complete common patterns
                                        if 'AES-' in item_text and item_text.endswith('-'):
                                            item_text = item_text[:-1] + '256.'
                                        elif item_text.endswith('which affect'):
                                            item_text = item_text + ' 98.6% of organizations.'
                                        elif item_text.endswith('affect'):
                                            item_text = item_text + ' your security posture.'
                                    # Also check for other incomplete patterns
                                    if not item_text.rstrip().endswith(('.', '!', '?', ')', '"')):
                                        # Sentence seems incomplete, add a period
                                        item_text = item_text.rstrip() + '.'
                                    item_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item_text)
                                    html_parts.append(f'        <li>{item_html}</li>')
                                html_parts.append('    </ol>')
                            
                            i += 1
                        
                        # Check if this is a bullet list (contains bullet points)
                        elif '•' in para:
                            # Check for list introduction
                            parts = para.split('\n')
                            list_intro = None
                            bullet_items = []
                            
                            for part in parts:
                                if '•' in part:
                                    # This line contains bullet points
                                    items = part.split('•')
                                    # First item might be introduction text
                                    if items[0].strip() and 'listed below' in items[0].lower():
                                        list_intro = items[0].strip()
                                    # Add all bullet items
                                    for item in items[1:]:
                                        if item.strip():
                                            bullet_items.append(item.strip())
                                elif part.strip() and not bullet_items:
                                    # This is likely the introduction
                                    if 'listed below' in part.lower() or 'following' in part.lower():
                                        list_intro = part.strip()
                                elif part.strip():
                                    # Additional bullet item on its own line
                                    if part.strip().startswith('**'):
                                        bullet_items.append(part.strip())
                            
                            # Output list introduction if present
                            if list_intro:
                                html_parts.append(f'    <p>{list_intro}</p>')
                            
                            # Output all bullet items in a single list
                            if bullet_items:
                                html_parts.append('    <ul>')
                                for item in bullet_items:
                                    # Convert markdown bold to HTML
                                    item_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
                                    html_parts.append(f'        <li>{item_html}</li>')
                                html_parts.append('    </ul>')
                            
                            i += 1
                        
                        else:
                            # Regular paragraph
                            para_text = para.strip()
                            
                            # Convert markdown bold to HTML
                            para_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para_text)
                            
                            # Clean up malformed punctuation from previous processing
                            para_html = re.sub(r',\.\s*', '. ', para_html)  # Fix ",. " -> ". "
                            para_html = re.sub(r',\s+([A-Z])', r'. \1', para_html)  # Fix ", Who" -> ". Who"
                            para_html = re.sub(r',\s*$', '.', para_html)  # Fix sentences ending with comma
                            
                            # Fix periods that should be commas in lists
                            para_html = re.sub(r'\. (ISO \d+)\. (GDPR)\.', r', \1, \2', para_html)  # Fix "SOC 2. ISO 27001. GDPR."
                            para_html = re.sub(r'management\. (DDoS)', r'management, \1', para_html)  # Fix "management. DDoS"
                            
                            # Fix content generation errors
                            para_html = para_html.replace('cooperation cloud security', 'comprehensive cloud security')
                            
                            # Check if paragraph is very long and needs splitting
                            word_count = len(para_html.split())
                            
                            if word_count > 120:  # Only split very long paragraphs
                                # Split on sentence boundaries more carefully
                                # First, protect common abbreviations by temporarily replacing them
                                protected_text = para_html
                                abbreviations = ['Mr.', 'Mrs.', 'Dr.', 'Prof.', 'Inc.', 'Ltd.', 'Corp.', 'vs.', 'etc.', 'i.e.', 'e.g.']
                                temp_replacements = {}
                                
                                for i, abbrev in enumerate(abbreviations):
                                    placeholder = f"__ABBREV_{i}__"
                                    temp_replacements[placeholder] = abbrev
                                    protected_text = protected_text.replace(abbrev, placeholder)
                                
                                # Now split on period + space + capital letter
                                sentences = re.split(r'\.\s+(?=[A-Z])', protected_text)
                                
                                # Restore abbreviations
                                for j, sentence in enumerate(sentences):
                                    for placeholder, abbrev in temp_replacements.items():
                                        sentence = sentence.replace(placeholder, abbrev)
                                    sentences[j] = sentence
                                
                                if len(sentences) > 1:
                                    # Group sentences into smaller paragraphs (max 60 words each)
                                    current_para = []
                                    current_word_count = 0
                                    
                                    for sentence in sentences:
                                        sentence = sentence.strip()
                                        if not sentence:
                                            continue
                                            
                                        # Ensure sentence ends with proper punctuation
                                        if not sentence.endswith(('.', '!', '?', ':', ';')):
                                            sentence += '.'
                                            
                                        sentence_words = len(sentence.split())
                                        
                                        # If adding this sentence would make paragraph too long, start new one
                                        if current_word_count > 0 and current_word_count + sentence_words > 60:
                                            if current_para:
                                                html_parts.append(f'    <p>{" ".join(current_para)}</p>')
                                            current_para = [sentence]
                                            current_word_count = sentence_words
                                        else:
                                            current_para.append(sentence)
                                            current_word_count += sentence_words
                                    
                                    # Add remaining sentences
                                    if current_para:
                                        html_parts.append(f'    <p>{" ".join(current_para)}</p>')
                                else:
                                    # No good split points found, keep as single paragraph
                                    html_parts.append(f'    <p>{para_html}</p>')
                            else:
                                # Paragraph is reasonable length, keep as is
                                html_parts.append(f'    <p>{para_html}</p>')
                            
                            i += 1
                
                # Sources
                if include_sources and st.session_state.content_brief.get('research_data'):
                    research = st.session_state.content_brief['research_data'].get('data', {})
                    if research.get('sources'):
                        html_parts.append('    <hr>')
                        html_parts.append('    <h2>Sources</h2>')
                        html_parts.append('    <ol>')
                        for source in research['sources'][:10]:
                            if isinstance(source, dict):
                                url = source.get("url", "").strip()
                                title = source.get("title", "").strip()
                                
                                # Only include sources with proper URL and title
                                if url and title and url.startswith('http') and len(title) > 3:
                                    html_parts.append(f'        <li><a href="{url}">{title}</a></li>')
                                elif title and len(title) > 10:  # Title-only sources
                                    html_parts.append(f'        <li>{title}</li>')
                            elif isinstance(source, str) and len(source.strip()) > 10:
                                html_parts.append(f'        <li>{source}</li>')
                        html_parts.append('    </ol>')
                
                html_parts.append('</body>')
                html_parts.append('</html>')
                
                # Post-process to merge consecutive <ul> tags into single lists
                html_content = '\n'.join(html_parts)
                
                # Merge consecutive </ul>\n    <ul> patterns
                html_content = re.sub(r'</ul>\s*<ul>', '', html_content)
                
                # Convert all <ul> to <ol> for better Google Sheets compatibility
                html_content = html_content.replace('<ul>', '<ol>')
                html_content = html_content.replace('</ul>', '</ol>')
                
                return html_content
            
            def generate_text():
                """Generate plain text format"""
                text_parts = []
                
                # Header
                text_parts.append(export_content['metadata']['primary_keyword'].upper())
                text_parts.append('=' * len(export_content['metadata']['primary_keyword']))
                text_parts.append('')
                
                if include_metadata:
                    text_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    text_parts.append(f"Word Count: {export_content['metadata']['word_count']}")
                    if include_quality and avg_quality > 0:
                        text_parts.append(f"Quality Score: {avg_quality:.1f}%")
                    text_parts.append('')
                    text_parts.append('-' * 40)
                    text_parts.append('')
                
                # Introduction
                if export_content['content']['introduction']:
                    text_parts.append(export_content['content']['introduction'])
                    text_parts.append('')
                
                # Sections
                for section in export_content['content']['sections']:
                    text_parts.append(section['heading'].upper())
                    text_parts.append('-' * len(section['heading']))
                    text_parts.append('')
                    text_parts.append(section['content'])
                    text_parts.append('')
                
                # Sources
                if include_sources and st.session_state.content_brief.get('research_data'):
                    research = st.session_state.content_brief['research_data'].get('data', {})
                    if research.get('sources'):
                        text_parts.append('-' * 40)
                        text_parts.append('')
                        text_parts.append('SOURCES')
                        text_parts.append('')
                        for i, source in enumerate(research['sources'][:10], 1):
                            if isinstance(source, dict):
                                text_parts.append(f"{i}. {source.get('title', 'Source')} - {source.get('url', '')}")
                            else:
                                text_parts.append(f"{i}. {source}")
                
                return '\n'.join(text_parts)
            
            def generate_json():
                """Generate JSON format"""
                json_export = {
                    'metadata': export_content['metadata'],
                    'content': {
                        'title': export_content['metadata']['primary_keyword'].title(),
                        'introduction': export_content['content']['introduction'],
                        'sections': export_content['content']['sections']
                    }
                }
                
                if include_quality:
                    json_export['quality_analysis'] = st.session_state.content_brief.get('quality_scores', {})
                
                if include_sources and st.session_state.content_brief.get('research_data'):
                    json_export['research'] = st.session_state.content_brief.get('research_data', {})
                
                return json.dumps(json_export, indent=2)
            
            # Generate content based on selected format
            if "Markdown" in export_format:
                export_data = generate_markdown()
                file_extension = "md"
                mime_type = "text/markdown"
            elif "HTML" in export_format:
                export_data = generate_html()
                file_extension = "html"
                mime_type = "text/html"
            elif "Plain Text" in export_format:
                export_data = generate_text()
                file_extension = "txt"
                mime_type = "text/plain"
            elif "JSON" in export_format:
                export_data = generate_json()
                file_extension = "json"
                mime_type = "application/json"
            else:  # Google Docs format
                export_data = generate_html()
                file_extension = "html"
                mime_type = "text/html"
            
            # Preview area
            st.markdown("---")
            st.markdown("### 👁️ Export Preview")
            
            # Show preview in expandable area
            with st.expander("View Export Content", expanded=False):
                if "HTML" in export_format or "Google" in export_format:
                    st.code(export_data[:2000] + "..." if len(export_data) > 2000 else export_data, language="html")
                elif "JSON" in export_format:
                    st.code(export_data[:2000] + "..." if len(export_data) > 2000 else export_data, language="json")
                elif "Markdown" in export_format:
                    st.code(export_data[:2000] + "..." if len(export_data) > 2000 else export_data, language="markdown")
                else:
                    st.text(export_data[:2000] + "..." if len(export_data) > 2000 else export_data)
            
            # Export actions
            st.markdown("---")
            st.markdown("### 💾 Export Actions")
            
            col1, col2, col3 = st.columns(3)
            
            # Generate filename
            keyword_slug = re.sub(r'[^a-z0-9]+', '_', export_content['metadata']['primary_keyword'].lower())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{keyword_slug}_{timestamp}.{file_extension}"
            
            with col1:
                # Download button
                st.download_button(
                    label=f"⬇️ Download {export_format.split()[0]}",
                    data=export_data,
                    file_name=filename,
                    mime=mime_type,
                    use_container_width=True
                )
            
            with col2:
                # Save to data directory
                if st.button("💾 Save to Project", use_container_width=True):
                    try:
                        # Create saved_content directory if it doesn't exist
                        save_dir = Path("data/saved_content")
                        save_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Save file
                        save_path = save_dir / filename
                        with open(save_path, 'w', encoding='utf-8') as f:
                            f.write(export_data)
                        
                        st.success(f"✅ Saved to: data/saved_content/{filename}")
                        
                        # Also save metadata
                        meta_filename = f"{keyword_slug}_{timestamp}_metadata.json"
                        meta_path = save_dir / meta_filename
                        with open(meta_path, 'w', encoding='utf-8') as f:
                            json.dump(export_content['metadata'], f, indent=2)
                        
                    except Exception as e:
                        st.error(f"Error saving file: {str(e)}")
            
            with col3:
                # Copy to clipboard (using code block as workaround)
                if st.button("📋 Show for Copy", use_container_width=True):
                    st.text_area("Copy this content:", export_data, height=300)
            
            # Export summary
            st.markdown("---")
            st.success(f"""
            ✅ **Export Ready!**
            - Format: {export_format}
            - Filename: {filename}
            - Size: {len(export_data):,} characters
            - Sections: {len(export_content['content']['sections']) + 1}
            - Quality: {avg_quality:.1f}%
            """)
            
            # Navigation
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("← Back to Quality Check"):
                    st.session_state.current_step = 4
                    st.rerun()
            with col2:
                if st.button("📝 Start New Content", type="secondary"):
                    # Reset session state
                    st.session_state.content_brief = {
                        'primary_keyword': '',
                        'introduction': '',
                        'headings': [],
                        'research_data': {},
                        'generated_content': {},
                        'quality_scores': {}
                    }
                    st.session_state.current_step = 1
                    st.rerun()
            with col3:
                if st.button("✨ Generate More", type="primary"):
                    st.session_state.current_step = 1
                    st.rerun()

elif selected_mode == "🔧 Content Optimization":
    # CONTENT OPTIMIZATION WORKFLOW
    st.header("Optimize Existing Content")
    
    # Workflow steps for optimization
    optimization_steps = {
        1: "📥 Import & Analyze",
        2: "🔍 Gap Analysis",
        3: "🔬 Research Gaps",
        4: "🔧 Optimize Content",
        5: "✅ Quality Compare",
        6: "📤 Export Changes"
    }
    
    # Progress indicator
    progress_cols = st.columns(6)
    for i, (step_num, step_name) in enumerate(optimization_steps.items()):
        with progress_cols[i]:
            if st.session_state.active_mode == "🔧 Content Optimization":
                if step_num < st.session_state.current_step:
                    st.success(f"✓ {step_name}")
                elif step_num == st.session_state.current_step:
                    st.info(f"→ {step_name}")
                else:
                    st.text(f"  {step_name}")
    
    st.markdown("---")
    
    # Step content for optimization workflow
    if st.session_state.current_step == 1:
        st.subheader("Step 1: Import & Analyze Existing Content")
        
        # Initialize scraper
        scraper = ContentScraper() if SCRAPER_AVAILABLE else None
        
        # URL input with fetch button
        col_url, col_fetch = st.columns([4, 1])
        
        with col_url:
            url = st.text_input(
                "Article URL",
                value=st.session_state.optimization_data.get('url', ''),
                placeholder="https://gcore.com/learning/what-is-cdn"
            )
            st.session_state.optimization_data['url'] = url
        
        with col_fetch:
            st.write("")  # Spacing
            st.write("")  # Spacing
            fetch_button = st.button("🔍 Fetch", type="primary", disabled=not url)
        
        # Fetch content if button clicked
        if fetch_button and url:
            if not scraper:
                st.error("Scraper module not available. Please check installation.")
            else:
                # Create a placeholder for status messages
                status_placeholder = st.empty()
                
                try:
                    status_placeholder.info("🔄 Fetching content from URL... Please wait...")
                    
                    # First validate the URL
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                        st.session_state.optimization_data['url'] = url
                    
                    # Fetch the content
                    scraped_data = scraper.fetch_from_url(url)
                    
                    if scraped_data.get('success'):
                        # Update session state with scraped content
                        st.session_state.optimization_data['original_content'] = scraped_data.get('content_html', '')
                        
                        # Auto-detect primary keyword
                        suggested_keyword = scraper.extract_primary_keyword(
                            url, 
                            scraped_data.get('title', ''),
                            scraped_data.get('content_text', '')
                        )
                        if suggested_keyword and not st.session_state.optimization_data.get('primary_keyword'):
                            st.session_state.optimization_data['primary_keyword'] = suggested_keyword
                        
                        status_placeholder.success(f"✅ Successfully fetched: {scraped_data.get('title', 'Article')}")
                        
                        # Show fetched info
                        with st.expander("📄 Fetched Content Info", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Title:** {scraped_data.get('title', 'N/A')}")
                                st.write(f"**Headings Found:** {len(scraped_data.get('headings', []))}")
                            with col2:
                                if scraped_data.get('meta_description'):
                                    st.write(f"**Meta Description:** {scraped_data.get('meta_description')[:100]}...")
                                st.write(f"**Content Length:** {len(scraped_data.get('content_text', '').split())} words")
                            
                            if scraped_data.get('headings'):
                                st.write("**Structure Preview:**")
                                for h in scraped_data.get('headings', [])[:5]:
                                    level_indent = "  " * (int(h['level'][1]) - 1)
                                    st.write(f"{level_indent}• {h['level']}: {h['text']}")
                        
                        # Force a rerun to update the UI
                        st.rerun()
                    else:
                        status_placeholder.error(f"❌ Failed to fetch: {scraped_data.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    status_placeholder.error(f"❌ Error fetching content: {str(e)}")
        
        # Primary keyword (auto-filled if fetched)
        primary_keyword = st.text_input(
            "Primary Target Keyword",
            value=st.session_state.optimization_data.get('primary_keyword', ''),
            placeholder="e.g., CDN caching",
            help="This will be auto-detected from the URL/title if you fetch the content"
        )
        st.session_state.optimization_data['primary_keyword'] = primary_keyword
        
        # Existing content input (hidden if already fetched)
        if st.session_state.optimization_data.get('original_content'):
            with st.expander("📝 View/Edit Fetched Content"):
                existing_content = st.text_area(
                    "Current Article Content (HTML)",
                    value=st.session_state.optimization_data.get('original_content', ''),
                    height=200,
                    help="Content was automatically fetched from the URL"
                )
                st.session_state.optimization_data['original_content'] = existing_content
        else:
            st.subheader("Or Paste Content Manually")
            existing_content = st.text_area(
                "Current Article Content (HTML or Text)",
                value=st.session_state.optimization_data.get('original_content', ''),
                height=300,
                placeholder="Paste your existing article content here if not using URL fetch..."
            )
            st.session_state.optimization_data['original_content'] = existing_content
        
        # Parse and analyze button
        current_content = st.session_state.optimization_data.get('original_content', '')
        current_keyword = st.session_state.optimization_data.get('primary_keyword', '')
        
        # Debug info
        if current_content:
            st.info(f"✓ Content loaded ({len(current_content)} characters)")
        if current_keyword:
            st.info(f"✓ Primary keyword: {current_keyword}")
        
        if current_content and current_keyword:
            if st.button("Analyze Content Structure", type="primary"):
                with st.spinner("Analyzing content structure..."):
                    # Parse the content
                    try:
                        parsed = parse_existing_content(current_content)
                        st.session_state.optimization_data['parsed_structure'] = parsed
                        st.success("Content parsed successfully!")
                        # Force rerun to show results
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error parsing content: {str(e)}")
        
        # Show analysis results if already parsed
        if st.session_state.optimization_data.get('parsed_structure'):
            parsed = st.session_state.optimization_data['parsed_structure']
            
            st.success("✅ Content analyzed successfully!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Word Count", parsed['word_count'])
                st.metric("Headings Found", len(parsed['headings']))
            
            with col2:
                st.metric("H1 Title", parsed.get('title', 'Not found'))
                st.metric("Content Sections", len(parsed['sections']))
            
            # Show extracted structure
            if parsed['headings']:
                st.subheader("Extracted Structure")
                for heading in parsed['headings']:
                    level_emoji = {"H1": "🔷", "H2": "🔹", "H3": "▪️", "H4": "◦"}.get(heading['level'], "•")
                    st.text(f"{level_emoji} {heading['level']}: {heading['text']}")
        
        # Show continue button if content has been analyzed
        if st.session_state.optimization_data.get('parsed_structure'):
            st.markdown("---")
            if st.button("Continue to Gap Analysis →", type="primary"):
                st.session_state.current_step = 2
                st.rerun()
    
    elif st.session_state.current_step == 2:
        st.subheader("Step 2: Define Target Structure")
        
        parsed = st.session_state.optimization_data.get('parsed_structure', {})
        
        if not parsed:
            st.warning("Please complete Step 1 first")
            if st.button("← Back to Import"):
                st.session_state.current_step = 1
                st.rerun()
        else:
            # Load section functions for content generation
            section_functions = load_section_functions()
            function_options = get_function_options(section_functions)
            
            
            # Initialize or refresh optimized headings list
            # Always refresh if we have parsed data but no optimized headings
            if ('optimized_headings' not in st.session_state.optimization_data or 
                len(st.session_state.optimization_data.get('optimized_headings', [])) == 0):
                optimized_headings = []
                existing_headings = parsed.get('headings', [])
                
                if existing_headings:
                    for h in existing_headings:
                        # Store original content for preservation
                        section_content = parsed.get('sections', {}).get(h['text'], '')
                        
                        heading_dict = {
                            'level': h.get('level', 'H2'),
                            'text': h.get('text', ''),
                            'original_text': h.get('text', ''),
                            'original_content': section_content,  # Store for preservation
                            'word_count': len(section_content.split()) if section_content else 0,
                            'action': 'keep',  # Default to keep
                            'function': auto_detect_function(h.get('text', ''), section_functions)
                        }
                        optimized_headings.append(heading_dict)
                    
                    st.session_state.optimization_data['optimized_headings'] = optimized_headings
                else:
                    st.session_state.optimization_data['optimized_headings'] = []
            
            # Part A: Review Existing Content
            st.markdown("### 📋 Review Existing Content")
            st.info("Choose what to do with each existing section • Use ↑↓ arrows to reorder")
            
            if st.session_state.optimization_data.get('optimized_headings'):
                # Filter existing headings (skip new ones for this section)
                existing_headings = [h for h in st.session_state.optimization_data['optimized_headings'] if h.get('original_text', '') != '']
                
                # Display each existing heading with reordering controls
                for i, heading in enumerate(existing_headings):
                    # Get the actual index in the full headings list
                    actual_index = st.session_state.optimization_data['optimized_headings'].index(heading)
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([0.4, 2.5, 1.5, 1, 0.6, 0.6])
                    
                    with col1:
                        # Visual hierarchy indicator
                        level = heading['level']
                        level_emoji = {"H1": "🔷", "H2": "🔹", "H3": "▪️"}.get(level, "•")
                        st.write(f"{level_emoji} {level}")
                    
                    with col2:
                        # Editable heading text with word count
                        new_text = st.text_input(
                            f"Heading {actual_index}",
                            value=heading['text'],
                            key=f"opt_heading_{actual_index}",
                            label_visibility="collapsed",
                            help=f"{heading.get('word_count', 0)} words"
                        )
                        if new_text != heading['text']:
                            heading['text'] = new_text
                            heading['function'] = auto_detect_function(new_text, section_functions)
                        
                        # Show word count below
                        st.caption(f"📝 {heading.get('word_count', 0)} words")
                    
                    with col3:
                        # Simple action selector - only Keep/Improve/Remove
                        action_options = ["keep", "improve", "remove"]
                        action_labels = {
                            "keep": "✅ Keep",
                            "improve": "🔧 Improve", 
                            "remove": "❌ Remove"
                        }
                        
                        action = st.selectbox(
                            "Action",
                            options=action_options,
                            format_func=lambda x: action_labels.get(x, x),
                            index=action_options.index(heading.get('action', 'keep')),
                            key=f"action_{actual_index}",
                            label_visibility="collapsed"
                        )
                        heading['action'] = action
                    
                    with col4:
                        # Function selector (only for improve action)
                        if action == "improve":
                            function = st.selectbox(
                                "Function",
                                options=list(function_options.keys()),
                                format_func=lambda x: function_options.get(x, x),
                                index=list(function_options.keys()).index(heading.get('function', 'generate_definition')),
                                key=f"func_{actual_index}",
                                label_visibility="collapsed",
                                help="Content function to use"
                            )
                            heading['function'] = function
                        else:
                            st.write("—")
                    
                    with col5:
                        # Move up button
                        if actual_index > 0:  # Not the first item
                            if st.button("↑", key=f"opt_up_{actual_index}", help="Move heading up"):
                                # Swap with previous item in full list
                                all_headings = st.session_state.optimization_data['optimized_headings']
                                all_headings[actual_index], all_headings[actual_index-1] = all_headings[actual_index-1], all_headings[actual_index]
                                st.session_state.optimization_data['optimized_headings'] = all_headings
                                st.rerun()
                        else:
                            st.write("")  # Empty space for alignment
                    
                    with col6:
                        # Move down button  
                        if actual_index < len(st.session_state.optimization_data['optimized_headings']) - 1:  # Not the last item
                            if st.button("↓", key=f"opt_down_{actual_index}", help="Move heading down"):
                                # Swap with next item in full list
                                all_headings = st.session_state.optimization_data['optimized_headings']
                                all_headings[actual_index], all_headings[actual_index+1] = all_headings[actual_index+1], all_headings[actual_index]
                                st.session_state.optimization_data['optimized_headings'] = all_headings
                                st.rerun()
                        else:
                            st.write("")  # Empty space for alignment
            else:
                st.info("No existing content found. You can add new sections below.")
            
            # Part B: Add New Sections  
            st.markdown("---")
            st.markdown("### ➕ Add New Sections")
            st.info("Define new sections to add to the article")
            
            # Template loading section (same as new content)
            col_template, col_clear = st.columns([2, 1])
            with col_template:
                if st.button("📋 Load Cloud Security Template", type="secondary", use_container_width=True):
                    # Pre-defined template based on cloud security article structure
                    keyword = st.session_state.optimization_data.get('primary_keyword', 'topic').lower()
                    template_headings = [
                        {"text": f"What are the main {keyword} challenges?", "level": "H2", "function": "generate_listicle"},
                        {"text": f"What are the key benefits of {keyword}?", "level": "H2", "function": "generate_listicle"},
                        {"text": f"How to implement {keyword} best practices?", "level": "H2", "function": "generate_how_list"},
                        {"text": "Frequently asked questions", "level": "H2", "function": "generate_faq_intro"},
                        {"text": f"What's the difference between {keyword} and traditional approaches?", "level": "H3", "function": "generate_differences"},
                        {"text": f"How much does {keyword} cost?", "level": "H3", "function": "generate_how_stats_answer"}
                    ]
                    
                    # Add template headings as new sections
                    for template_heading in template_headings:
                        # Check if heading doesn't already exist
                        existing_texts = [h['text'].lower() for h in st.session_state.optimization_data['optimized_headings']]
                        if template_heading['text'].lower() not in existing_texts:
                            st.session_state.optimization_data['optimized_headings'].append({
                                'level': template_heading['level'],
                                'text': template_heading['text'],
                                'original_text': '',  # Mark as new
                                'original_content': '',
                                'word_count': 0,
                                'action': 'new',
                                'function': template_heading['function']
                            })
                    st.rerun()
            
            with col_clear:
                if st.button("🗑️ Remove All New", type="secondary", use_container_width=True):
                    # Remove all new headings (those without original_text)
                    st.session_state.optimization_data['optimized_headings'] = [
                        h for h in st.session_state.optimization_data['optimized_headings'] 
                        if h.get('original_text', '') != ''
                    ]
                    st.rerun()
            
            # Add new heading interface
            with st.expander("➕ Add Custom Heading", expanded=True):
                col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                with col1:
                    new_level = st.selectbox("Level", ["H2", "H3"], key="new_opt_heading_level")
                with col2:
                    new_heading_text = st.text_input("Heading Text", key="new_opt_heading_text", 
                                                    placeholder="e.g., Best practices for CDN configuration")
                with col3:
                    if new_heading_text:
                        # Check if we're in FAQ context
                        in_faq_section = False
                        if 'optimized_headings' in st.session_state.optimization_data and new_level == 'H3':
                            for heading in reversed(st.session_state.optimization_data['optimized_headings']):
                                if heading['level'] == 'H2':
                                    heading_text_lower = heading['text'].lower()
                                    if any(faq_keyword in heading_text_lower for faq_keyword in ['faq', 'frequently asked', 'common questions']):
                                        in_faq_section = True
                                    break
                        
                        # Show FAQ detection hint
                        if in_faq_section and new_level == 'H3':
                            st.caption("💡 FAQ mode detected")
                        
                        detection_context = {
                            'in_faq_section': in_faq_section,
                            'heading_level': new_level
                        }
                        
                        detected_function = auto_detect_function(new_heading_text, section_functions, detection_context)
                        new_function = st.selectbox(
                            "Function",
                            options=list(function_options.keys()),
                            format_func=lambda x: function_options.get(x, x),
                            index=list(function_options.keys()).index(detected_function) if detected_function in function_options else 0,
                            key="new_opt_heading_function"
                        )
                    else:
                        new_function = "generate_definition"
                with col4:
                    if st.button("Add", type="primary", key="add_custom_heading"):
                        if new_heading_text:
                            st.session_state.optimization_data['optimized_headings'].append({
                                'level': new_level,
                                'text': new_heading_text,
                                'original_text': '',  # Mark as new
                                'original_content': '',
                                'word_count': 0,
                                'action': 'new',
                                'function': new_function
                            })
                            st.rerun()
            
            # Display currently added new sections
            new_sections = [h for h in st.session_state.optimization_data.get('optimized_headings', []) if h.get('action') == 'new']
            if new_sections:
                st.markdown("#### 📝 New Sections to Add")
                for i, section in enumerate(new_sections):
                    col1, col2, col3 = st.columns([0.5, 4, 0.5])
                    with col1:
                        level_emoji = {"H2": "🔹", "H3": "▪️"}.get(section['level'], "•")
                        st.write(f"{level_emoji} {section['level']}")
                    with col2:
                        st.write(f"**{section['text']}**")
                        st.caption(f"Function: {function_options.get(section['function'], section['function'])}")
                    with col3:
                        # Find the actual index in the full list
                        full_idx = st.session_state.optimization_data['optimized_headings'].index(section)
                        if st.button("🗑️", key=f"del_new_{i}"):
                            st.session_state.optimization_data['optimized_headings'].pop(full_idx)
                            st.rerun()
            
            # Show optimization summary
            st.markdown("---")
            st.markdown("### 📊 Structure Summary")
            
            actions_count = {
                'keep': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'keep']),
                'improve': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'improve']),
                'new': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'new']),
                'remove': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'remove'])
            }
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Keep", actions_count['keep'])
            with col2:
                st.metric("🔧 Improve", actions_count['improve'])
            with col3:
                st.metric("✨ New", actions_count['new'])
            with col4:
                st.metric("❌ Remove", actions_count['remove'])
            
            # CTA Product Selection for Optimization
            st.markdown("---")
            with st.expander("🎯 CTA Product Settings", expanded=False):
                st.markdown("**Configure product CTAs for optimized content**")
                
                if APIS_AVAILABLE:
                    try:
                        from core.product_loader import product_loader
                        
                        # Get available products
                        products = product_loader.get_product_list()
                        
                        # Auto-suggest relevant products based on primary keyword
                        article_keywords = st.session_state.optimization_data.get('primary_keyword', '').lower().split()
                        suggested_products = product_loader.suggest_relevant_products(article_keywords)
                        
                        # Product selection
                        product_options = ["None (No CTA)"] + [f"{p['name']} - {p['tagline']}" for p in products]
                        product_ids = ["none"] + [p['id'] for p in products]
                        
                        # Default selection - use first suggested product if available
                        default_idx = 0
                        if suggested_products:
                            try:
                                default_idx = product_ids.index(suggested_products[0])
                            except ValueError:
                                default_idx = 0
                        
                        selected_product_idx = st.selectbox(
                            "Select Product for CTA",
                            range(len(product_options)),
                            format_func=lambda x: product_options[x],
                            index=default_idx,
                            help="Choose which Gcore product to feature in call-to-action sections",
                            key="opt_product_selection"
                        )
                        
                        selected_product_id = product_ids[selected_product_idx]
                        
                        # Store the selection in session state
                        st.session_state.optimization_data['selected_product'] = selected_product_id
                        
                        if selected_product_id != "none":
                            # Show product info and available CTA templates
                            product_data = product_loader.get_product(selected_product_id)
                            if product_data:
                                st.success(f"✅ **{product_data['name']}** selected")
                                st.caption(f"URL: {product_data.get('url', 'N/A')}")
                                
                                # Show available CTA templates
                                cta_templates = product_loader.get_cta_templates(selected_product_id)
                                if cta_templates:
                                    st.write("**Available CTA Templates:**")
                                    for template_name, template_text in list(cta_templates.items())[:3]:
                                        with st.expander(f"📝 {template_name.replace('_', ' ').title()}", expanded=False):
                                            st.write(template_text[:200] + "..." if len(template_text) > 200 else template_text)
                        else:
                            st.info("No product CTA will be included")
                            
                        # Show suggestions if products were auto-detected
                        if suggested_products and len(suggested_products) > 1:
                            st.write("**💡 Other Suggested Products:**")
                            for product_id in suggested_products[1:3]:  # Show top 2 alternatives
                                product = product_loader.get_product(product_id)
                                if product:
                                    st.caption(f"• {product['name']}: {product.get('tagline', '')}")
                    
                    except Exception as e:
                        st.warning("Product data not available. CTAs will use basic templates.")
                        st.session_state.optimization_data['selected_product'] = "none"
                else:
                    st.warning("API not available. Product CTAs disabled.")
                    st.session_state.optimization_data['selected_product'] = "none"
            
            # Navigation
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("← Back to Import"):
                    st.session_state.current_step = 1
                    st.rerun()
            with col3:
                if st.button("Continue to Research →", type="primary"):
                    st.session_state.current_step = 3
                    st.rerun()
    
    elif st.session_state.current_step == 3:
        st.subheader("Step 3: Research Enhancement")
        
        # Initialize variables
        sections_to_research = []
        sections_to_keep = []
        
        # Analyze what needs research (only improve and new sections)
        if st.session_state.optimization_data.get('optimized_headings'):
            sections_to_research = [h for h in st.session_state.optimization_data['optimized_headings'] 
                                   if h.get('action') in ['improve', 'new']]
            sections_to_keep = [h for h in st.session_state.optimization_data['optimized_headings'] 
                               if h.get('action') == 'keep']
            
            # Display research scope
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔬 Sections to Research", len(sections_to_research), 
                         help="New and Improve sections")
            with col2:
                st.metric("✅ No Research Needed", len(sections_to_keep),
                         help="Sections to preserve as-is")
            
            # Show sections requiring research
            if sections_to_research:
                st.markdown("---")
                st.markdown("### 📋 Research Plan")
                
                with st.expander(f"🔬 Research Needed ({len(sections_to_research)} sections)", expanded=True):
                    for section in sections_to_research:
                        action_emoji = "✨" if section['action'] == 'new' else "🔧"
                        st.write(f"{action_emoji} **{section['text']}**")
                        action_label = "New content" if section['action'] == 'new' else "Improve existing"
                        st.caption(f"{action_label} | Function: {section.get('function', 'generate_definition')}")
                
                # Research configuration
                st.markdown("---")
                
                use_perplexity = st.checkbox("Use Perplexity for research", 
                                            value=PERPLEXITY_API_KEY is not None,
                                            help="Enable real-time web research")
                
                # Execute research button
                if st.button("🚀 Start Research", type="primary"):
                    with st.spinner("Researching topic..."):
                        if use_perplexity and PERPLEXITY_API_KEY and APIS_AVAILABLE:
                            try:
                                from core.research_engine import ResearchEngine
                                research_engine = ResearchEngine()
                                
                                # Build research query based on sections
                                primary_keyword = st.session_state.optimization_data['primary_keyword']
                                research_topics = []
                                
                                # Add topics from sections needing research (as dict format)
                                for section in sections_to_research:
                                    research_topics.append({
                                        'text': section['text'],
                                        'level': section.get('level', 'H2')
                                    })
                                
                                # Conduct research
                                research_result = research_engine.research_topic(
                                    primary_keyword,
                                    research_topics[:10],  # Limit to 10 topics
                                    context="Focus on Gcore-relevant information about edge computing, CDN, and cloud infrastructure"
                                )
                                
                                st.session_state.optimization_data['research_data'] = research_result
                                st.success("✅ Research completed successfully!")
                                
                                # Show research summary
                                if research_result.get('data'):
                                    st.markdown("#### 📊 Research Summary")
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Facts Found", len(research_result['data'].get('facts', [])))
                                    with col2:
                                        st.metric("Statistics", len(research_result['data'].get('statistics', [])))
                                    with col3:
                                        st.metric("Sources", len(research_result['data'].get('sources', [])))
                                
                            except Exception as e:
                                st.error(f"Research failed: {str(e)}")
                        else:
                            # Mock research for demo mode
                            st.session_state.optimization_data['research_data'] = {
                                'status': 'completed',
                                'timestamp': datetime.now().isoformat(),
                                'data': {
                                    'facts': [f"Research fact about {st.session_state.optimization_data['primary_keyword']}"],
                                    'statistics': ["Industry growth: 25% YoY"],
                                    'sources': ["Demo source"]
                                }
                            }
                            st.success("✅ Demo research data loaded")
                        
                        st.rerun()
                
                # Show existing research if available
                if st.session_state.optimization_data.get('research_data'):
                    st.markdown("---")
                    st.markdown("### 📚 Current Research Data")
                    
                    research = st.session_state.optimization_data['research_data'].get('data', {})
                    
                    with st.expander("View Research Results", expanded=False):
                        if research.get('facts'):
                            st.markdown("**Key Facts:**")
                            for fact in research['facts'][:5]:
                                st.write(f"• {fact}")
                        
                        if research.get('statistics'):
                            st.markdown("**Statistics:**")
                            for stat in research['statistics'][:5]:
                                st.write(f"• {stat}")
            else:
                st.info("ℹ️ No sections require research. All content is marked to be kept as-is.")
        else:
            st.warning("Please complete Step 2 (Gap Analysis) first")
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Structure"):
                st.session_state.current_step = 2
                st.rerun()
        with col3:
            # Only allow continuing if research is done or not needed
            can_continue = (st.session_state.optimization_data.get('research_data') or 
                          not sections_to_research)
            if st.button("Continue to Generate →", type="primary", disabled=not can_continue):
                st.session_state.current_step = 4
                st.rerun()
            if not can_continue:
                st.caption("Complete research before continuing")
    
    elif st.session_state.current_step == 4:
        st.subheader("Step 4: Generate Optimized Content")
        
        # Check prerequisites
        if not st.session_state.optimization_data.get('optimized_headings'):
            st.warning("Please complete structure planning first")
            if st.button("← Back to Structure"):
                st.session_state.current_step = 2
                st.rerun()
        else:
            # Import optimization modules
            try:
                from core.content_optimizer import ContentOptimizer
                from core.content_generator import ContentGenerator
                OPTIMIZER_AVAILABLE = True
                
                # Initialize optimizer with generator if available
                if ANTHROPIC_API_KEY and APIS_AVAILABLE:
                    content_generator = ContentGenerator()
                    optimizer = ContentOptimizer(content_generator)
                else:
                    optimizer = ContentOptimizer()
            except ImportError:
                OPTIMIZER_AVAILABLE = False
                optimizer = None
            
            # Show generation plan summary
            st.markdown("### 📋 Content Generation Plan")
            
            actions_summary = {
                'keep': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'keep']),
                'improve': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'improve']),
                'new': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'new']),
                'remove': len([h for h in st.session_state.optimization_data['optimized_headings'] if h.get('action') == 'remove'])
            }
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Keep As-Is", actions_summary['keep'])
            with col2:
                st.metric("🔧 Improve", actions_summary['improve'])
            with col3:
                st.metric("✨ Generate New", actions_summary['new'])
            with col4:
                st.metric("❌ Remove", actions_summary['remove'])
            
            # Generate optimized content button
            st.markdown("---")
            if st.button("🚀 Generate Optimized Content", type="primary"):
                with st.spinner("Generating optimized content..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    if APIS_AVAILABLE and content_generator:
                        # Initialize results storage
                        optimized_sections = {}
                        total_headings = len([h for h in st.session_state.optimization_data['optimized_headings'] 
                                             if h.get('action') != 'remove'])
                        processed = 0
                        
                        # Generate introduction
                        status_text.text("Generating introduction...")
                        intro_result = content_generator.generate_introduction(
                            topic=st.session_state.optimization_data['primary_keyword'],
                            headings=st.session_state.optimization_data.get('optimized_headings', []),
                            research_data=st.session_state.optimization_data.get('research_data'),
                            include_gcore=False
                        )
                        
                        if intro_result['status'] == 'success' and intro_result.get('content'):
                            st.session_state.optimization_data['introduction'] = intro_result['content']
                        else:
                            keyword = st.session_state.optimization_data['primary_keyword']
                            st.session_state.optimization_data['introduction'] = f"{keyword} is a fundamental aspect of modern technology infrastructure."
                        
                        # Process each heading based on action
                        for heading in st.session_state.optimization_data['optimized_headings']:
                            action = heading.get('action', 'keep')
                            heading_text = heading['text']
                            
                            if action == 'remove':
                                # Skip removed sections
                                continue
                            
                            processed += 1
                            progress = processed / total_headings
                            progress_bar.progress(progress)
                            status_text.text(f"Processing: {heading_text[:50]}...")
                            
                            if action == 'keep':
                                # Use original content as-is
                                optimized_sections[heading_text] = {
                                    'content': heading.get('original_content', ''),
                                    'word_count': heading.get('word_count', 0),
                                    'action': 'kept',
                                    'function': heading.get('function', '')
                                }
                            
                            elif action == 'improve':
                                # Generate improved content with preservation
                                if optimizer and OPTIMIZER_AVAILABLE:
                                    # Extract valuable elements from original
                                    valuable_elements = optimizer._extract_valuable_elements(
                                        heading.get('original_content', '')
                                    )
                                    
                                    # Generate new content
                                    result = content_generator.generate_section(
                                        heading=heading_text,
                                        research_data=st.session_state.optimization_data.get('research_data'),
                                        parent_context={
                                            'heading_level': heading['level'],
                                            'gcore_product': st.session_state.optimization_data.get('selected_product', 'cdn'),
                                            'gcore_features': []
                                        },
                                        include_gcore=False,
                                        function_name=heading.get('function', 'generate_definition')
                                    )
                                    
                                    if result['status'] == 'success':
                                        # Merge valuable elements with new content
                                        improved_content = optimizer.merge_content(
                                            heading.get('original_content', ''),
                                            result['content'],
                                            'preserve_valuable'
                                        )
                                        optimized_sections[heading_text] = {
                                            'content': improved_content,
                                            'word_count': len(improved_content.split()),
                                            'action': 'improved',
                                            'preserved_elements': valuable_elements,
                                            'function': heading.get('function', '')
                                        }
                                    else:
                                        # Fallback to original
                                        optimized_sections[heading_text] = {
                                            'content': heading.get('original_content', ''),
                                            'word_count': heading.get('word_count', 0),
                                            'action': 'kept',
                                            'function': heading.get('function', '')
                                        }
                                else:
                                    # No optimizer available, generate new
                                    result = content_generator.generate_section(
                                        heading=heading_text,
                                        research_data=st.session_state.optimization_data.get('research_data'),
                                        parent_context={
                                            'heading_level': heading['level'],
                                            'gcore_product': st.session_state.optimization_data.get('selected_product', 'cdn'),
                                            'gcore_features': []
                                        },
                                        include_gcore=False,
                                        function_name=heading.get('function', 'generate_definition')
                                    )
                                    
                                    if result['status'] == 'success':
                                        optimized_sections[heading_text] = {
                                            'content': result['content'],
                                            'word_count': result.get('word_count', 0),
                                            'action': 'improved',
                                            'function': heading.get('function', '')
                                        }
                            
                            elif action == 'new':
                                # Generate completely new content
                                result = content_generator.generate_section(
                                    heading=heading_text,
                                    research_data=st.session_state.optimization_data.get('research_data'),
                                    parent_context={
                                        'heading_level': heading['level'],
                                        'gcore_product': st.session_state.optimization_data.get('selected_product', 'cdn'),
                                        'gcore_features': []
                                    },
                                    include_gcore=False,
                                    function_name=heading.get('function', 'generate_definition')
                                )
                                
                                if result['status'] == 'success':
                                    optimized_sections[heading_text] = {
                                        'content': result['content'],
                                        'word_count': result.get('word_count', 0),
                                        'action': 'generated',
                                        'function': heading.get('function', '')
                                    }
                                else:
                                    optimized_sections[heading_text] = {
                                        'content': f"Content for {heading_text}",
                                        'word_count': 10,
                                        'action': 'generated',
                                        'function': heading.get('function', '')
                                    }
                        
                        # Store results
                        st.session_state.optimization_data['optimized_content'] = optimized_sections
                        progress_bar.progress(1.0)
                        status_text.text("Generation complete!")
                        st.success("✅ Content optimized successfully!")
                        
                    else:
                        # Fallback demo mode
                        topic = st.session_state.optimization_data['primary_keyword']
                        st.session_state.optimization_data['introduction'] = f"{topic} is a technology that enables organizations to optimize their digital infrastructure."
                        
                        optimized_sections = {}
                        for heading in st.session_state.optimization_data['optimized_headings']:
                            if heading.get('action') != 'remove':
                                heading_text = heading['text']
                                if heading.get('action') == 'keep':
                                    content = heading.get('original_content', 'Original content preserved.')
                                else:
                                    content = f"This is demo content for {heading_text}. In production, this would contain AI-optimized content."
                                
                                optimized_sections[heading_text] = {
                                    'content': content,
                                    'word_count': len(content.split()),
                                    'action': heading.get('action', 'generated'),
                                    'function': heading.get('function', '')
                                }
                        
                        st.session_state.optimization_data['optimized_content'] = optimized_sections
                        st.success("✅ Demo content generated!")
                    
                    st.rerun()
            
            # Show current optimization results if available
            if st.session_state.optimization_data.get('optimized_content'):
                st.markdown("---")
                st.markdown("### 📄 Optimized Content Preview")
                
                # Display introduction if available
                if st.session_state.optimization_data.get('introduction'):
                    with st.expander("📝 Introduction", expanded=False):
                        st.write(st.session_state.optimization_data['introduction'])
                
                optimized = st.session_state.optimization_data['optimized_content']
                
                # Show optimized sections
                if optimized:
                    for heading in st.session_state.optimization_data.get('optimized_headings', []):
                        heading_text = heading['text']
                        if heading_text in optimized and heading.get('action') != 'remove':
                            section_data = optimized[heading_text]
                            
                            # Section header with action indicator
                            action_emoji = {
                                'kept': '✅',
                                'improved': '🔧',
                                'generated': '✨'
                            }.get(section_data.get('action', ''), '•')
                            
                            with st.expander(f"{action_emoji} {heading['level']}: {heading_text}", expanded=False):
                                st.write(section_data.get('content', ''))
                                st.caption(f"Action: {section_data.get('action', 'unknown')} | Words: {section_data.get('word_count', 0)} | Function: {section_data.get('function', 'N/A')}")
        
        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Research"):
                st.session_state.current_step = 3
                st.rerun()
        with col3:
            can_continue = st.session_state.optimization_data.get('optimized_content') is not None
            if st.button("Continue to Quality Comparison →", type="primary", disabled=not can_continue):
                st.session_state.current_step = 5
                st.rerun()
            if not can_continue:
                st.caption("Execute optimization before continuing")
    
    elif st.session_state.current_step == 5:
        st.subheader("Step 5: Quality Comparison")
        st.info("Compare original vs optimized content quality...")
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Optimize"):
                st.session_state.current_step = 4
                st.rerun()
        with col3:
            if st.button("Continue to Export →", type="primary"):
                st.session_state.current_step = 6
                st.rerun()
    
    elif st.session_state.current_step == 6:
        st.subheader("Step 6: Export Optimized Content")
        st.info("Export your optimized content with change tracking...")
        
        # Check if we have optimized content to export
        optimized_content = st.session_state.optimization_data.get('optimized_content', {})
        if not optimized_content:
            st.warning("No optimized content available. Please complete the optimization steps first.")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← Back to Quality Check"):
                    st.session_state.current_step = 5
                    st.rerun()
        else:
            # Prepare content for export
            primary_keyword = st.session_state.optimization_data.get('primary_keyword', 'Optimized Content')
            export_content = {
                'metadata': {
                    'primary_keyword': primary_keyword,
                    'word_count': 0,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'optimized_content'
                },
                'content': {
                    'introduction': optimized_content.get('introduction', ''),
                    'sections': []
                }
            }

            # Add sections and calculate word count
            total_words = 0
            for section_data in optimized_content.get('sections', []):
                if isinstance(section_data, dict) and 'content' in section_data:
                    section_content = section_data['content']
                    section_title = section_data.get('heading', 'Section')
                    
                    export_content['content']['sections'].append({
                        'heading': section_title,
                        'content': section_content
                    })
                    
                    # Count words
                    words = len(section_content.split()) if section_content else 0
                    total_words += words

            # Add introduction word count
            if export_content['content']['introduction']:
                intro_words = len(export_content['content']['introduction'].split())
                total_words += intro_words

            export_content['metadata']['word_count'] = total_words

            # Export format selection
            st.markdown("---")
            st.markdown("### 📤 Export Options")
            
            export_format = st.selectbox(
                "Select Export Format",
                ["Markdown (.md)", "HTML (.html)", "Plain Text (.txt)", "JSON (.json)", "Google Docs Format", "📊 Change Report"],
                help="Choose the format that best suits your needs"
            )
            
            # Add metadata options
            st.markdown("**Include in Export:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                include_metadata = st.checkbox("Metadata", value=True, help="Include keyword and word count")
            with col2:
                include_quality = st.checkbox("Quality Scores", value=True, help="Include quality analysis results")
            with col3:
                include_changes = st.checkbox("Change Summary", value=True, help="Include optimization changes made")

            # Generate export content based on format
            def generate_markdown():
                """Generate Markdown format"""
                md_content = []
                
                # Add metadata as comments
                if include_metadata:
                    md_content.append(f"<!-- Primary Keyword: {export_content['metadata']['primary_keyword']} -->")
                    md_content.append(f"<!-- Word Count: {export_content['metadata']['word_count']} -->")
                    md_content.append(f"<!-- Export Date: {export_content['metadata']['timestamp']} -->")
                    md_content.append("")

                # Title
                md_content.append(f"# {export_content['metadata']['primary_keyword'].title()}")
                md_content.append("")

                # Introduction
                if export_content['content']['introduction']:
                    md_content.append(export_content['content']['introduction'])
                    md_content.append("")

                # Sections
                for section in export_content['content']['sections']:
                    heading_level = 2  # Default to H2 for optimized content sections
                    heading_prefix = "#" * heading_level
                    md_content.append(f"{heading_prefix} {section['heading']}")
                    md_content.append("")
                    md_content.append(section['content'])
                    md_content.append("")

                # Add change summary if requested
                if include_changes:
                    quality_comparison = st.session_state.optimization_data.get('quality_comparison', {})
                    if quality_comparison:
                        md_content.append("## Optimization Summary")
                        md_content.append("")
                        md_content.append(f"- **Original Score**: {quality_comparison.get('original_score', 'N/A')}%")
                        md_content.append(f"- **Optimized Score**: {quality_comparison.get('optimized_score', 'N/A')}%")
                        md_content.append(f"- **Improvement**: +{quality_comparison.get('improvement', 'N/A')}%")
                
                return '\n'.join(md_content)

            def generate_html():
                """Generate HTML format"""
                html_parts = []
                
                # HTML header
                html_parts.append('<!DOCTYPE html>')
                html_parts.append('<html lang="en">')
                html_parts.append('<head>')
                html_parts.append('    <meta charset="UTF-8">')
                html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
                html_parts.append(f'    <title>{export_content["metadata"]["primary_keyword"].title()}</title>')
                html_parts.append('    <style>')
                html_parts.append('        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; max-width: 800px; }')
                html_parts.append('        h1, h2, h3 { color: #333; }')
                html_parts.append('        .metadata { background: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 5px; }')
                html_parts.append('    </style>')
                html_parts.append('</head>')
                html_parts.append('<body>')

                # Metadata section
                if include_metadata:
                    html_parts.append('    <div class="metadata">')
                    html_parts.append('        <h3>Content Information</h3>')
                    html_parts.append('        <dl>')
                    html_parts.append(f'            <dt>Keyword:</dt><dd>{export_content["metadata"]["primary_keyword"]}</dd><br>')
                    html_parts.append(f'            <dt>Word Count:</dt><dd>{export_content["metadata"]["word_count"]}</dd><br>')
                    html_parts.append(f'            <dt>Export Date:</dt><dd>{export_content["metadata"]["timestamp"]}</dd>')
                    html_parts.append('        </dl>')
                    html_parts.append('    </div>')

                # Title
                html_parts.append(f'    <h1>{export_content["metadata"]["primary_keyword"].title()}</h1>')

                # Introduction
                if export_content['content']['introduction']:
                    intro_paragraphs = export_content['content']['introduction'].split('\n\n')
                    for para in intro_paragraphs:
                        if para.strip():
                            # Convert markdown bold to HTML
                            para_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para.strip())
                            html_parts.append(f'    <p>{para_html}</p>')

                # Sections
                for section in export_content['content']['sections']:
                    html_parts.append(f'    <h2>{section["heading"]}</h2>')
                    
                    # Process section content
                    content = section['content']
                    paragraphs = content.split('\n\n')
                    
                    for para in paragraphs:
                        if para.strip():
                            # Convert markdown bold to HTML
                            para_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', para.strip())
                            html_parts.append(f'    <p>{para_html}</p>')

                # Add change summary if requested
                if include_changes:
                    quality_comparison = st.session_state.optimization_data.get('quality_comparison', {})
                    if quality_comparison:
                        html_parts.append('    <h2>Optimization Summary</h2>')
                        html_parts.append('    <ul>')
                        html_parts.append(f'        <li><strong>Original Score</strong>: {quality_comparison.get("original_score", "N/A")}%</li>')
                        html_parts.append(f'        <li><strong>Optimized Score</strong>: {quality_comparison.get("optimized_score", "N/A")}%</li>')
                        html_parts.append(f'        <li><strong>Improvement</strong>: +{quality_comparison.get("improvement", "N/A")}%</li>')
                        html_parts.append('    </ul>')

                html_parts.append('</body>')
                html_parts.append('</html>')
                
                # Post-process to merge consecutive <ul> tags into single lists
                html_content = '\n'.join(html_parts)
                
                # Merge consecutive </ul>\n    <ul> patterns
                html_content = re.sub(r'</ul>\s*<ul>', '', html_content)
                
                # Convert all <ul> to <ol> for better Google Sheets compatibility
                html_content = html_content.replace('<ul>', '<ol>')
                html_content = html_content.replace('</ul>', '</ol>')
                
                return html_content

            def generate_text():
                """Generate plain text format"""
                text_parts = []
                
                # Title
                text_parts.append(export_content['metadata']['primary_keyword'].upper())
                text_parts.append('=' * len(export_content['metadata']['primary_keyword']))
                text_parts.append('')

                # Metadata
                if include_metadata:
                    text_parts.append(f"Word Count: {export_content['metadata']['word_count']}")
                    text_parts.append(f"Export Date: {export_content['metadata']['timestamp']}")
                    text_parts.append('')

                # Introduction
                if export_content['content']['introduction']:
                    text_parts.append(export_content['content']['introduction'])
                    text_parts.append('')

                # Sections
                for section in export_content['content']['sections']:
                    text_parts.append(section['heading'].upper())
                    text_parts.append('-' * len(section['heading']))
                    text_parts.append('')
                    text_parts.append(section['content'])
                    text_parts.append('')

                return '\n'.join(text_parts)

            def generate_json():
                """Generate JSON format"""
                json_export = {
                    'metadata': export_content['metadata'],
                    'content': {
                        'title': export_content['metadata']['primary_keyword'].title(),
                        'introduction': export_content['content']['introduction'],
                        'sections': export_content['content']['sections']
                    }
                }
                
                if include_quality:
                    json_export['quality_analysis'] = st.session_state.optimization_data.get('quality_comparison', {})
                
                if include_changes:
                    json_export['optimization_changes'] = st.session_state.optimization_data.get('gap_analysis', {})
                
                return json.dumps(json_export, indent=2)

            def generate_change_report():
                """Generate detailed change report"""
                report_parts = []
                
                # Header
                report_parts.append(f"# Optimization Report: {export_content['metadata']['primary_keyword'].title()}")
                report_parts.append("")
                report_parts.append(f"**Generated**: {export_content['metadata']['timestamp']}")
                report_parts.append("")
                
                # Quality comparison
                quality_comparison = st.session_state.optimization_data.get('quality_comparison', {})
                if quality_comparison:
                    report_parts.append("## Quality Score Comparison")
                    report_parts.append("")
                    report_parts.append(f"- **Before**: {quality_comparison.get('original_score', 'N/A')}%")
                    report_parts.append(f"- **After**: {quality_comparison.get('optimized_score', 'N/A')}%")
                    report_parts.append(f"- **Improvement**: +{quality_comparison.get('improvement', 'N/A')}%")
                    report_parts.append("")
                
                # Gap analysis
                gap_analysis = st.session_state.optimization_data.get('gap_analysis', {})
                if gap_analysis:
                    report_parts.append("## Content Gaps Addressed")
                    report_parts.append("")
                    missing_sections = gap_analysis.get('missing_sections', [])
                    if missing_sections:
                        report_parts.append("### New Sections Added:")
                        for section in missing_sections:
                            report_parts.append(f"- {section}")
                        report_parts.append("")
                
                # Optimization summary
                report_parts.append("## Changes Made")
                report_parts.append("- Content structure optimized for semantic SEO")
                report_parts.append("- AI-sounding words replaced with natural language")
                report_parts.append("- Brand compliance improved")
                report_parts.append("- Missing sections added based on competitor analysis")
                
                return '\n'.join(report_parts)

            # Generate content based on selected format
            if "Change Report" in export_format:
                export_data = generate_change_report()
                file_extension = "md"
                mime_type = "text/markdown"
            elif "Markdown" in export_format:
                export_data = generate_markdown()
                file_extension = "md"
                mime_type = "text/markdown"
            elif "HTML" in export_format:
                export_data = generate_html()
                file_extension = "html"
                mime_type = "text/html"
            elif "Plain Text" in export_format:
                export_data = generate_text()
                file_extension = "txt"
                mime_type = "text/plain"
            elif "JSON" in export_format:
                export_data = generate_json()
                file_extension = "json"
                mime_type = "application/json"
            else:  # Google Docs format
                export_data = generate_html()
                file_extension = "html"
                mime_type = "text/html"

            # Preview area
            st.markdown("---")
            st.markdown("### 👁️ Export Preview")
            
            # Show preview in expandable area
            with st.expander("View Export Content", expanded=False):
                if "HTML" in export_format or "Google" in export_format:
                    st.code(export_data[:2000] + "..." if len(export_data) > 2000 else export_data, language="html")
                elif "JSON" in export_format:
                    st.code(export_data[:2000] + "..." if len(export_data) > 2000 else export_data, language="json")
                elif "Markdown" in export_format or "Change Report" in export_format:
                    st.code(export_data[:2000] + "..." if len(export_data) > 2000 else export_data, language="markdown")
                else:
                    st.text(export_data[:2000] + "..." if len(export_data) > 2000 else export_data)

            # Export actions
            st.markdown("---")
            st.markdown("### 💾 Download & Export")
            
            col1, col2 = st.columns(2)
            
            # Generate filename
            import re
            from datetime import datetime
            keyword_slug = re.sub(r'[^a-z0-9]+', '_', export_content['metadata']['primary_keyword'].lower())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{keyword_slug}_optimized_{timestamp}.{file_extension}"

            with col1:
                # Download button
                st.download_button(
                    label=f"⬇️ Download {export_format.split()[0]}",
                    data=export_data,
                    file_name=filename,
                    mime=mime_type,
                    use_container_width=True
                )

            with col2:
                # Copy to clipboard option
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    # This will be handled by the browser
                    st.text_area("Copy this content:", export_data, height=300)

            # Export summary
            st.markdown("---")
            avg_quality = st.session_state.optimization_data.get('quality_comparison', {}).get('optimized_score', 0)
            st.success(f"""
            ✅ **Export Ready!**
            - Format: {export_format}
            - Filename: {filename}
            - Size: {len(export_data):,} characters
            - Sections: {len(export_content['content']['sections']) + 1}
            - Quality: {avg_quality}%
            """)
            
            # Navigation
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← Back to Quality Check"):
                    st.session_state.current_step = 5
                    st.rerun()

elif selected_mode == "🚫 AI Word Manager":
    # AI WORD MANAGER INTERFACE
    implement_ai_word_manager()

elif selected_mode == "⚙️ Settings":
    # SETTINGS INTERFACE
    st.info("Settings interface coming soon...")
    st.markdown("### Configuration Options")
    st.markdown("- API Keys Management")
    st.markdown("- Default Templates")
    st.markdown("- Export Preferences")
    st.markdown("- Quality Thresholds")

# Quick actions in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")

if st.sidebar.button("🔄 Start New Project"):
    st.session_state.content_brief = {
        'primary_keyword': '',
        'introduction': '',
        'headings': [],
        'research_data': {},
        'generated_content': {},
        'quality_scores': {}
    }
    st.session_state.optimization_data = {
        'url': '',
        'primary_keyword': '',
        'additional_keywords': [],
        'original_content': '',
        'parsed_structure': {},
        'optimized_headings': [],
        'gap_analysis': {},
        'research_data': {},
        'optimized_content': {},
        'quality_comparison': {}
    }
    st.session_state.current_step = 1
    st.rerun()

# Quick actions in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")

if st.sidebar.button("🔄 Start New Project", key="start_new_project_sidebar"):
    st.session_state.content_brief = {
        'primary_keyword': '',
        'introduction': '',
        'headings': [],
        'research_data': {},
        'generated_content': {},
        'quality_scores': {}
    }
    st.session_state.optimization_data = {
        'url': '',
        'primary_keyword': '',
        'additional_keywords': [],
        'original_content': '',
        'parsed_structure': {},
        'optimized_headings': [],
        'gap_analysis': {},
        'research_data': {},
        'optimized_content': {},
        'quality_comparison': {}
    }
    st.session_state.current_step = 1
    st.rerun()

# Display current workflow in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Current Workflow")
st.sidebar.info(f"Mode: {st.session_state.active_mode}")
st.sidebar.info(f"Step: {st.session_state.current_step}")

# Logout button
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
    st.session_state.authenticated = False
    clear_authentication()  # Clear authentication file
    st.rerun()
