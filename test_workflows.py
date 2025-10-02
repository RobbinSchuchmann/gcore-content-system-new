#!/usr/bin/env python3
"""
Comprehensive workflow testing for Content Creation and Optimization tabs
"""

import sys
import traceback
from pathlib import Path

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_test(test_name, status, message=""):
    """Log test result"""
    if status == "PASS":
        test_results["passed"].append(test_name)
        print(f"✅ {test_name}: PASS {message}")
    elif status == "FAIL":
        test_results["failed"].append(test_name)
        print(f"❌ {test_name}: FAIL {message}")
    elif status == "WARN":
        test_results["warnings"].append(test_name)
        print(f"⚠️  {test_name}: WARN {message}")

def test_imports():
    """Test all critical imports"""
    print("\n" + "="*60)
    print("TEST 1: IMPORTS & DEPENDENCIES")
    print("="*60)

    try:
        import streamlit as st
        log_test("Streamlit import", "PASS", f"(v{st.__version__})")
    except Exception as e:
        log_test("Streamlit import", "FAIL", str(e))
        return False

    try:
        from anthropic import Anthropic
        log_test("Anthropic SDK import", "PASS")
    except Exception as e:
        log_test("Anthropic SDK import", "FAIL", str(e))

    try:
        import requests
        log_test("Requests import", "PASS")
    except Exception as e:
        log_test("Requests import", "FAIL", str(e))

    try:
        from core.content_generator import ContentGenerator
        log_test("ContentGenerator import", "PASS")
    except Exception as e:
        log_test("ContentGenerator import", "FAIL", str(e))

    try:
        from core.content_optimizer import ContentOptimizer
        log_test("ContentOptimizer import", "PASS")
    except Exception as e:
        log_test("ContentOptimizer import", "FAIL", str(e))

    try:
        from core.content_scraper import ContentScraper
        log_test("ContentScraper import", "PASS")
    except Exception as e:
        log_test("ContentScraper import", "FAIL", str(e))

    try:
        from core.research_engine import ResearchEngine
        log_test("ResearchEngine import", "PASS")
    except Exception as e:
        log_test("ResearchEngine import", "FAIL", str(e))

    try:
        from core.quality_checker import QualityChecker
        log_test("QualityChecker import", "PASS")
    except Exception as e:
        log_test("QualityChecker import", "FAIL", str(e))

    try:
        from core.serp_analyzer import SERPAnalyzer
        log_test("SERPAnalyzer import", "PASS")
    except Exception as e:
        log_test("SERPAnalyzer import", "FAIL", str(e))

    return True

def test_config():
    """Test configuration and data files"""
    print("\n" + "="*60)
    print("TEST 2: CONFIGURATION & DATA FILES")
    print("="*60)

    try:
        import config
        log_test("Config file import", "PASS")

        # Check API keys
        if hasattr(config, 'ANTHROPIC_API_KEY') and config.ANTHROPIC_API_KEY:
            log_test("Anthropic API key configured", "PASS")
        else:
            log_test("Anthropic API key configured", "WARN", "- Not set")

        if hasattr(config, 'PERPLEXITY_API_KEY') and config.PERPLEXITY_API_KEY:
            log_test("Perplexity API key configured", "PASS")
        else:
            log_test("Perplexity API key configured", "WARN", "- Not set")

    except Exception as e:
        log_test("Config file import", "FAIL", str(e))

    # Check data files
    data_files = {
        'brand_guidelines.json': 'data/brand_guidelines.json',
        'ai_blacklist.txt': 'data/ai_blacklist.txt',
        'section_functions.json': 'data/section_functions.json',
        'gcore_products.json': 'data/gcore_products.json'
    }

    for name, path in data_files.items():
        if Path(path).exists():
            log_test(f"{name} exists", "PASS")
        else:
            log_test(f"{name} exists", "FAIL", f"- Not found at {path}")

def test_app_structure():
    """Test main app.py structure"""
    print("\n" + "="*60)
    print("TEST 3: APP STRUCTURE")
    print("="*60)

    try:
        with open('app.py', 'r') as f:
            content = f.read()

        # Check for main components
        if 'st.set_page_config' in content:
            log_test("Page config present", "PASS")
        else:
            log_test("Page config present", "FAIL")

        # Check for tabs
        if 'tab1, tab2 = st.tabs' in content or 'st.tabs([' in content:
            log_test("Tab structure present", "PASS")
        else:
            log_test("Tab structure present", "FAIL")

        # Check for step definitions
        steps_to_check = [
            ('Step 1: Import', 'current_step == 1'),
            ('Step 2: Analysis', 'current_step == 2'),
            ('Step 3: Structure Editor', 'current_step == 3'),
            ('Step 4: Generate', 'current_step == 4'),
            ('Step 5: Quality', 'current_step == 5'),
            ('Step 6: Export', 'current_step == 6')
        ]

        for step_name, step_check in steps_to_check:
            if step_check in content:
                log_test(f"{step_name} defined", "PASS")
            else:
                log_test(f"{step_name} defined", "FAIL")

        # Check for Accept/Customize buttons
        if 'Accept Recommendations' in content and 'Customize Structure' in content:
            log_test("Accept/Customize buttons present", "PASS")
        else:
            log_test("Accept/Customize buttons present", "FAIL")

        # Check for auto_accept handling
        if 'auto_accept' in content:
            log_test("Auto-accept logic present", "PASS")
        else:
            log_test("Auto-accept logic present", "FAIL")

    except Exception as e:
        log_test("App structure analysis", "FAIL", str(e))

def test_serp_analyzer():
    """Test SERP Analyzer improvements"""
    print("\n" + "="*60)
    print("TEST 4: SERP ANALYZER (AI RECOMMENDATIONS)")
    print("="*60)

    try:
        with open('core/serp_analyzer.py', 'r') as f:
            content = f.read()

        # Check that deduplication is removed
        if 'def deduplicate_recommendations' in content:
            log_test("Deduplication removed", "FAIL", "- Function still exists")
        else:
            log_test("Deduplication removed", "PASS")

        # Check for new AI prompt rules
        rules_to_check = [
            ('NEVER recommend the same heading for both REMOVE and ADD', 'No duplicate REMOVE/ADD rule'),
            ('DO NOT suggest transforming or restructuring headings', 'No transformation rule'),
            ('Only suggest H3s for complex technical sections', 'H3 usage rule')
        ]

        for rule_text, rule_name in rules_to_check:
            if rule_text in content:
                log_test(f"AI Prompt: {rule_name}", "PASS")
            else:
                log_test(f"AI Prompt: {rule_name}", "FAIL")

    except Exception as e:
        log_test("SERP Analyzer analysis", "FAIL", str(e))

def test_step3_structure():
    """Test Step 3 Structure Editor"""
    print("\n" + "="*60)
    print("TEST 5: STEP 3 STRUCTURE EDITOR")
    print("="*60)

    try:
        with open('app.py', 'r') as f:
            content = f.read()

        # Check for key Step 3 features
        step3_features = [
            ('optimized_headings initialization', 'optimized_headings'),
            ('Two-mode display', 'if auto_accept:'),
            ('Accept mode view', 'AI-Recommended Structure'),
            ('Customize mode view', 'Custom Structure Editor'),
            ('REMOVE sections expander', 'Sections That Will Be Removed'),
            ('Product CTA settings', 'CTA Product Settings'),
            ('Function auto-detection', 'auto_detect_function')
        ]

        for feature_name, feature_check in step3_features:
            if feature_check in content:
                log_test(f"Step 3: {feature_name}", "PASS")
            else:
                log_test(f"Step 3: {feature_name}", "FAIL")

    except Exception as e:
        log_test("Step 3 structure analysis", "FAIL", str(e))

def test_step_numbering():
    """Test step renumbering"""
    print("\n" + "="*60)
    print("TEST 6: STEP RENUMBERING (6 STEPS TOTAL)")
    print("="*60)

    try:
        with open('app.py', 'r') as f:
            lines = f.readlines()

        # Find step dictionary
        step_dict_found = False
        for i, line in enumerate(lines):
            if 'optimization_steps = {' in line:
                step_dict_found = True
                # Check next 6 lines for step definitions
                step_lines = ''.join(lines[i:i+8])

                expected_steps = [
                    '1: "📥 Import Content"',
                    '2: "🔍 Competitor Analysis"',
                    '3: "📋 Structure Editor"',
                    '4: "🔧 Generate/Optimize"',
                    '5: "✅ Quality Check"',
                    '6: "📤 Export"'
                ]

                for step in expected_steps:
                    if step in step_lines:
                        log_test(f"Step definition: {step}", "PASS")
                    else:
                        log_test(f"Step definition: {step}", "FAIL")
                break

        if not step_dict_found:
            log_test("Step dictionary found", "FAIL")
        else:
            log_test("Step dictionary found", "PASS")

        # Check for old step 7 references
        content = ''.join(lines)
        if 'current_step == 7' in content:
            log_test("No Step 7 references", "FAIL", "- Found step 7 reference")
        else:
            log_test("No Step 7 references", "PASS")

    except Exception as e:
        log_test("Step numbering analysis", "FAIL", str(e))

def test_indentation():
    """Test code indentation"""
    print("\n" + "="*60)
    print("TEST 7: CODE INDENTATION")
    print("="*60)

    try:
        with open('app.py', 'r') as f:
            lines = f.readlines()

        # Check for common indentation errors
        indentation_ok = True
        for i, line in enumerate(lines, 1):
            # Check elif statements (should not be indented)
            if line.strip().startswith('elif st.session_state.current_step =='):
                if line.startswith('    elif'):  # 4 spaces before elif
                    log_test(f"Line {i} indentation", "FAIL", f"- Indented elif statement")
                    indentation_ok = False
                    break

        if indentation_ok:
            log_test("Elif statement indentation", "PASS")

        # Try to compile the file
        try:
            with open('app.py', 'r') as f:
                compile(f.read(), 'app.py', 'exec')
            log_test("Python syntax valid", "PASS")
        except SyntaxError as e:
            log_test("Python syntax valid", "FAIL", f"- Line {e.lineno}: {e.msg}")

    except Exception as e:
        log_test("Indentation analysis", "FAIL", str(e))

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    total = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["warnings"])

    print(f"\n✅ Passed: {len(test_results['passed'])}/{total}")
    print(f"❌ Failed: {len(test_results['failed'])}/{total}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}/{total}")

    if test_results["failed"]:
        print("\n❌ Failed Tests:")
        for test in test_results["failed"]:
            print(f"  - {test}")

    if test_results["warnings"]:
        print("\n⚠️  Warnings:")
        for test in test_results["warnings"]:
            print(f"  - {test}")

    print("\n" + "="*60)
    if test_results["failed"]:
        print("❌ TESTING FAILED - Issues found")
        return False
    else:
        print("✅ ALL TESTS PASSED!")
        return True

if __name__ == "__main__":
    print("\n🧪 COMPREHENSIVE WORKFLOW TESTING")
    print("Testing Content Creation & Optimization Workflows")

    # Run all tests
    test_imports()
    test_config()
    test_app_structure()
    test_serp_analyzer()
    test_step3_structure()
    test_step_numbering()
    test_indentation()

    # Print summary
    success = print_summary()

    sys.exit(0 if success else 1)
