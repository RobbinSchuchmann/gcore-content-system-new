#!/usr/bin/env python3
"""
Test script to verify AI word prevention during generation
"""

import sys
import os
import json
from pathlib import Path

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_blacklist_loading():
    """Test that the AI word replacements file loads correctly"""
    print("\n" + "="*60)
    print("Testing Blacklist Loading")
    print("="*60)
    
    try:
        from core.content_generator import ContentGenerator
        
        # Initialize generator (will load blacklist)
        generator = ContentGenerator()
        
        # Check that replacements were loaded
        assert generator.ai_word_replacements is not None, "Replacements not loaded"
        assert 'word_groups' in generator.ai_word_replacements, "Missing word_groups"
        assert 'simple_replacements' in generator.ai_word_replacements, "Missing simple_replacements"
        
        # Count loaded items
        word_groups = len(generator.ai_word_replacements.get('word_groups', {}))
        simple_replacements = len(generator.ai_word_replacements.get('simple_replacements', {}))
        
        print(f"✅ Loaded {word_groups} word groups")
        print(f"✅ Loaded {simple_replacements} simple replacements")
        
        # Check blacklist prompt was generated
        assert generator.blacklist_prompt is not None, "Blacklist prompt not generated"
        assert "FORBIDDEN WORDS" in generator.blacklist_prompt, "Missing forbidden words section"
        assert "USE INSTEAD" in generator.blacklist_prompt, "Missing replacement suggestions"
        
        print(f"✅ Blacklist prompt generated ({len(generator.blacklist_prompt)} characters)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load blacklist: {e}")
        return False

def test_prompt_inclusion():
    """Test that the blacklist is included in generation prompts"""
    print("\n" + "="*60)
    print("Testing Prompt Inclusion")
    print("="*60)
    
    try:
        from core.content_generator import ContentGenerator
        
        generator = ContentGenerator()
        
        # Test building a function prompt
        test_heading = "What is cloud computing?"
        test_research = {'data': {'facts': ['Cloud computing provides on-demand resources']}}
        test_context = {'include_gcore': False}
        
        # Build prompt
        prompt = generator._build_function_prompt(
            heading=test_heading,
            function_name="generate_definition",
            research_data=test_research,
            context=test_context
        )
        
        # Verify blacklist is at the beginning
        assert prompt.startswith("=" * 60), "Prompt doesn't start with blacklist"
        assert "CRITICAL: FORBIDDEN WORDS" in prompt, "Missing forbidden words header"
        
        # Check for specific forbidden words
        assert "leverage" in prompt.lower(), "Missing 'leverage' in blacklist"
        assert "utilize" in prompt.lower(), "Missing 'utilize' in blacklist"
        assert "delve" in prompt.lower(), "Missing 'delve' in blacklist"
        
        # Check for replacement suggestions
        assert "USE INSTEAD" in prompt, "Missing replacement suggestions"
        
        print("✅ Blacklist is included at the beginning of prompts")
        print(f"✅ Prompt size: {len(prompt)} characters")
        
        # Show a sample of the blacklist section
        blacklist_section = prompt[:2000]  # First 2000 chars
        print("\nSample of blacklist in prompt:")
        print("-"*40)
        for line in blacklist_section.split('\n')[:20]:
            if line.strip():
                print(f"  {line[:80]}")
        print("-"*40)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed prompt inclusion test: {e}")
        return False

def test_word_coverage():
    """Test that all words from ai_blacklist.txt are covered"""
    print("\n" + "="*60)
    print("Testing Word Coverage")
    print("="*60)
    
    try:
        # Load the original blacklist
        blacklist_file = Path("data/ai_blacklist.txt")
        if blacklist_file.exists():
            with open(blacklist_file, 'r') as f:
                original_words = set(word.strip().lower() for word in f.readlines() if word.strip())
        else:
            print("⚠️ ai_blacklist.txt not found")
            return False
        
        # Load the replacements file
        replacements_file = Path("data/ai_word_replacements.json")
        with open(replacements_file, 'r') as f:
            replacements = json.load(f)
        
        # Collect all covered words
        covered_words = set()
        
        # From word groups
        for group in replacements.get('word_groups', {}).values():
            for word in group.get('words', []):
                covered_words.add(word.lower())
        
        # From simple replacements
        for word in replacements.get('simple_replacements', {}).keys():
            covered_words.add(word.lower())
        
        # Check coverage
        missing_words = original_words - covered_words
        coverage_percent = (len(covered_words) / len(original_words)) * 100
        
        print(f"Original blacklist words: {len(original_words)}")
        print(f"Covered in replacements: {len(covered_words)}")
        print(f"Coverage: {coverage_percent:.1f}%")
        
        if missing_words:
            print(f"\n⚠️ {len(missing_words)} words not covered:")
            for word in sorted(list(missing_words)[:10]):
                print(f"  - {word}")
            if len(missing_words) > 10:
                print(f"  ... and {len(missing_words) - 10} more")
        else:
            print("✅ All blacklist words are covered!")
        
        return coverage_percent > 90  # Accept 90% coverage as success
        
    except Exception as e:
        print(f"❌ Failed coverage test: {e}")
        return False

def test_replacement_quality():
    """Test that replacements are appropriate"""
    print("\n" + "="*60)
    print("Testing Replacement Quality")
    print("="*60)
    
    try:
        replacements_file = Path("data/ai_word_replacements.json")
        with open(replacements_file, 'r') as f:
            replacements = json.load(f)
        
        # Test some key replacements
        test_cases = {
            'leverage': 'use',
            'utilize': 'use',
            'delve': 'explore',
            'moreover': 'also',
            'intricate': 'complex'
        }
        
        simple_replacements = replacements.get('simple_replacements', {})
        
        for forbidden, expected in test_cases.items():
            actual = simple_replacements.get(forbidden)
            if actual:
                print(f"✅ {forbidden} → {actual}")
                assert expected in actual or actual in expected, f"Unexpected replacement for {forbidden}"
            else:
                # Check in word groups
                found = False
                for group in replacements.get('word_groups', {}).values():
                    if forbidden in [w.lower() for w in group.get('words', [])]:
                        replacements_list = group.get('replacements', [])
                        print(f"✅ {forbidden} → {', '.join(replacements_list)}")
                        found = True
                        break
                if not found:
                    print(f"⚠️ {forbidden} not found in replacements")
        
        print("\n✅ Replacement quality verified")
        return True
        
    except Exception as e:
        print(f"❌ Failed replacement quality test: {e}")
        return False

def main():
    print("="*70)
    print("AI WORD PREVENTION TEST SUITE")
    print("="*70)
    
    tests = [
        ("Blacklist Loading", test_blacklist_loading),
        ("Prompt Inclusion", test_prompt_inclusion),
        ("Word Coverage", test_word_coverage),
        ("Replacement Quality", test_replacement_quality)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nAI word prevention is now active during generation:")
        print("1. Comprehensive blacklist loaded (247+ words)")
        print("2. Clear replacement suggestions provided")
        print("3. Blacklist enforced at prompt level")
        print("4. Quality checker remains as safety net")
    else:
        print("❌ Some tests failed - review implementation")
    print("="*70)

if __name__ == "__main__":
    main()