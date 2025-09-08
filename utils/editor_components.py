"""
Editor UI Components for Rich Text Display
Provides Streamlit components for interactive content editing
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import re

def render_highlighted_content(content: str, issues: Dict[str, Any], container_key: str) -> str:
    """
    Render content with highlighted issues in Streamlit
    
    Args:
        content: Content to display
        issues: Issues identified by quality checker
        container_key: Unique key for the container
        
    Returns:
        Updated content after any edits
    """
    from core.content_editor import ContentEditor
    
    editor = ContentEditor()
    
    # Create columns for editor and suggestions
    col_editor, col_suggestions = st.columns([3, 1])
    
    with col_editor:
        # Display highlighted content
        # Extract the checks data for highlighting
        highlight_data = issues.get('checks', issues)
        highlighted_html = editor.highlight_issues(content, highlight_data)
        
        # Create an editable text area below the highlighted view
        st.markdown("### 📝 Content Editor")
        st.markdown(highlighted_html, unsafe_allow_html=True)
        
        # Editable version
        st.markdown("### ✏️ Edit Content")
        edited_content = st.text_area(
            "Edit the content below:",
            value=content,
            height=300,
            key=f"editor_{container_key}"
        )
    
    with col_suggestions:
        st.markdown("### 💡 Suggestions")
        
        # Get improvement suggestions - pass the checks data
        checks_data = issues.get('checks', issues)
        suggestions = editor.suggest_improvements(content, checks_data)
        
        # Display suggestions with action buttons
        for suggestion in suggestions:
            severity_color = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(suggestion['severity'], '⚪')
            
            st.markdown(f"{severity_color} **{suggestion['message']}**")
            st.caption(suggestion['action'])
            
            if suggestion['quick_fix']:
                if st.button(f"Fix: {suggestion['type']}", key=f"fix_{container_key}_{suggestion['quick_fix']}"):
                    edited_content = editor.apply_fix(edited_content, suggestion['quick_fix'])
                    st.rerun()
            
            st.markdown("---")
        
        # AI Word replacements
        ai_words_data = checks_data.get('ai_words', {})
        if ai_words_data.get('words'):
            st.markdown("### 🔄 Word Replacements")
            st.caption(f"Found {len(ai_words_data['words'])} AI words")
            
            for word in ai_words_data['words'][:5]:  # Show top 5
                replacements = editor.suggest_replacements(word)
                if replacements:
                    st.markdown(f"**{word}**")
                    for replacement in replacements[:3]:
                        if st.button(f"→ {replacement}", key=f"replace_{container_key}_{word}_{replacement}", use_container_width=True):
                            edited_content = editor.apply_fix(
                                edited_content, 
                                'replace_word',
                                target=word,
                                replacement=replacement
                            )
                            st.rerun()
                else:
                    st.markdown(f"**{word}**")
                    st.caption("No automatic replacements available")
                st.markdown("---")
        else:
            st.info("No AI words detected")
    
    return edited_content

def render_quality_metrics(original_scores: Dict, current_scores: Dict) -> None:
    """
    Render quality metrics comparison
    
    Args:
        original_scores: Original quality scores
        current_scores: Current quality scores
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        original = original_scores.get('overall_score', 0)
        current = current_scores.get('overall_score', 0)
        delta = current - original
        st.metric(
            "Quality Score",
            f"{current}%",
            delta=f"{delta:+.1f}%" if delta != 0 else None
        )
    
    with col2:
        original_ai = len(original_scores.get('checks', {}).get('ai_words', {}).get('words', []))
        current_ai = len(current_scores.get('checks', {}).get('ai_words', {}).get('words', []))
        delta_ai = original_ai - current_ai
        st.metric(
            "AI Words",
            current_ai,
            delta=f"-{delta_ai}" if delta_ai > 0 else None
        )
    
    with col3:
        readability = current_scores.get('checks', {}).get('readability', {}).get('score', 0)
        st.metric("Readability", f"{readability}%")

def render_issue_summary(issues: Dict[str, Any]) -> None:
    """
    Render a summary of all issues found
    
    Args:
        issues: Dictionary of issues from quality checker
    """
    st.markdown("### 📊 Issue Summary")
    
    # Count issues by type
    issue_counts = {
        'AI Words': len(issues.get('checks', {}).get('ai_words', {}).get('words', [])),
        'Long Sentences': len(issues.get('checks', {}).get('long_sentences', [])),
        'Passive Voice': issues.get('checks', {}).get('passive_voice', {}).get('count', 0),
        'Promotional Content': issues.get('checks', {}).get('promotional', {}).get('count', 0)
    }
    
    # Display as metrics
    cols = st.columns(4)
    for i, (issue_type, count) in enumerate(issue_counts.items()):
        with cols[i]:
            if count > 0:
                st.metric(issue_type, count, delta_color="inverse")
            else:
                st.metric(issue_type, count, delta="✓")

def render_quick_actions(content: str, container_key: str) -> str:
    """
    Render quick action buttons for common fixes
    
    Args:
        content: Current content
        container_key: Unique key for the container
        
    Returns:
        Updated content after any quick actions
    """
    from core.content_editor import ContentEditor
    
    editor = ContentEditor()
    
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Remove All AI Words", key=f"qa_ai_{container_key}"):
            content = editor.apply_fix(content, 'remove_all_ai_words')
            st.success("Removed AI words!")
            st.rerun()
    
    with col2:
        if st.button("✂️ Split Long Sentences", key=f"qa_split_{container_key}"):
            content = editor.apply_fix(content, 'split_long_sentences')
            st.success("Split long sentences!")
            st.rerun()
    
    with col3:
        if st.button("🚫 Remove Promotional", key=f"qa_promo_{container_key}"):
            content = editor.apply_fix(content, 'remove_promotional')
            st.success("Removed promotional content!")
            st.rerun()
    
    with col4:
        if st.button("🔧 Apply All Fixes", key=f"qa_all_{container_key}"):
            content = editor.batch_fix_content(content, [
                'remove_all_ai_words',
                'split_long_sentences',
                'remove_promotional'
            ])
            st.success("Applied all fixes!")
            st.rerun()
    
    return content

def render_diff_view(original: str, edited: str) -> None:
    """
    Render a diff view showing changes
    
    Args:
        original: Original content
        edited: Edited content
    """
    from core.content_editor import ContentEditor
    
    editor = ContentEditor()
    changes = editor.get_diff(original, edited)
    
    if not changes:
        st.info("No changes made yet")
        return
    
    st.markdown("### 📝 Changes Made")
    
    html_diff = "<div style='font-family: monospace; background: #f5f5f5; padding: 10px; border-radius: 5px;'>"
    
    for change_type, text in changes:
        if change_type == 'added':
            html_diff += f"<div style='color: green; background: #e6ffed;'>+ {text}</div>"
        elif change_type == 'removed':
            html_diff += f"<div style='color: red; background: #ffebe9;'>- {text}</div>"
        else:
            html_diff += f"<div style='color: #666;'> {text}</div>"
    
    html_diff += "</div>"
    
    st.markdown(html_diff, unsafe_allow_html=True)

def create_editor_interface(
    content: str,
    heading: str,
    issues: Dict[str, Any],
    container_key: str
) -> Dict[str, Any]:
    """
    Create complete editor interface for a content section
    
    Args:
        content: Original content
        heading: Section heading
        issues: Quality issues identified
        container_key: Unique key for the section
        
    Returns:
        Dictionary with edited content and metadata
    """
    st.markdown(f"## 📝 Editing: {heading}")
    
    # Store original content
    if f"original_{container_key}" not in st.session_state:
        st.session_state[f"original_{container_key}"] = content
    
    # Quick actions bar
    content = render_quick_actions(content, container_key)
    
    # Main editor with highlights and suggestions
    edited_content = render_highlighted_content(content, issues, container_key)
    
    # Show diff if content has changed
    if edited_content != st.session_state[f"original_{container_key}"]:
        with st.expander("View Changes", expanded=False):
            render_diff_view(st.session_state[f"original_{container_key}"], edited_content)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Changes", key=f"save_{container_key}", type="primary"):
            st.success("Changes saved!")
            return {
                'content': edited_content,
                'edited': True,
                'original': st.session_state[f"original_{container_key}"]
            }
    
    with col2:
        if st.button("↩️ Reset to Original", key=f"reset_{container_key}"):
            return {
                'content': st.session_state[f"original_{container_key}"],
                'edited': False,
                'original': st.session_state[f"original_{container_key}"]
            }
    
    with col3:
        if st.button("🔍 Re-check Quality", key=f"recheck_{container_key}"):
            return {
                'content': edited_content,
                'edited': True,
                'recheck': True,
                'original': st.session_state[f"original_{container_key}"]
            }
    
    return {
        'content': edited_content,
        'edited': edited_content != st.session_state[f"original_{container_key}"],
        'original': st.session_state[f"original_{container_key}"]
    }