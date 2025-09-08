#!/usr/bin/env python3
"""
Test script for the internal linking system
Tests link database, relevance scoring, and link placement
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.link_manager import LinkManager
from core.internal_linker import InternalLinker
from core.content_generator import ContentGenerator

def test_link_manager():
    """Test the link manager functionality"""
    print("=" * 60)
    print("Testing Link Manager")
    print("=" * 60)
    
    try:
        # Initialize link manager
        link_manager = LinkManager()
        
        # Get statistics
        stats = link_manager.get_statistics()
        print("\n📊 Link Database Statistics:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        
        # Test keyword search
        test_keywords = ['cdn', 'cloud', 'ddos', 'kubernetes']
        print("\n🔍 Testing Keyword Search:")
        for keyword in test_keywords:
            links = link_manager.get_links_by_keyword(keyword)
            print(f"  - '{keyword}': {len(links)} links found")
            if links:
                print(f"    Example: {links[0].url}")
        
        # Test relevance finding
        test_content = """
        Content delivery networks (CDN) are essential for modern web applications.
        They help reduce latency and improve performance by caching content
        at edge locations closer to users. CDN services also provide
        DDoS protection and security features.
        """
        
        print("\n🎯 Testing Relevance Scoring:")
        print(f"  Test content: CDN and DDoS protection topic")
        relevant_links = link_manager.find_relevant_links(test_content, "What is a CDN?", max_links=5)
        for link in relevant_links:
            print(f"  - {link.url} ({link.category})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing link manager: {e}")
        return False

def test_internal_linker():
    """Test the internal linker functionality"""
    print("\n" + "=" * 60)
    print("Testing Internal Linker")
    print("=" * 60)
    
    try:
        # Initialize components
        link_manager = LinkManager()
        internal_linker = InternalLinker(link_manager)
        
        # Test content for link suggestions
        test_content = """
        Cloud computing has revolutionized how businesses deploy applications.
        With managed Kubernetes services, teams can orchestrate containers
        efficiently while maintaining security. Load balancers help distribute
        traffic across multiple instances, ensuring high availability.
        
        For video streaming applications, a robust CDN solution is essential.
        It reduces latency and improves user experience by serving content
        from edge locations. Additionally, DDoS protection safeguards
        your infrastructure from attacks.
        """
        
        # Get link suggestions
        print("\n🔗 Testing Link Suggestions:")
        suggestions = internal_linker.suggest_links_for_content(
            test_content, 
            "Cloud Infrastructure Best Practices",
            max_links=5
        )
        
        print(f"  Found {len(suggestions)} relevant links:")
        for link, anchor_text, score in suggestions:
            print(f"  - URL: {link.url}")
            print(f"    Anchor: '{anchor_text}'")
            print(f"    Score: {score:.2f}")
            print()
        
        # Test link placement
        if suggestions:
            print("📝 Testing Link Placement:")
            content_with_links = internal_linker.place_links_in_content(
                test_content, suggestions[:3]
            )
            print("  Links successfully placed in content")
            
            # Validate placement
            validation = internal_linker.validate_link_placement(content_with_links)
            print(f"  Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
            print(f"  Total links placed: {validation['total_links']}")
            if validation['issues']:
                print("  Issues found:")
                for issue in validation['issues']:
                    print(f"    - {issue}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing internal linker: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_content_generator_integration():
    """Test integration with content generator"""
    print("\n" + "=" * 60)
    print("Testing Content Generator Integration")
    print("=" * 60)
    
    try:
        # Initialize content generator with internal links enabled
        generator = ContentGenerator(enable_internal_links=True)
        
        print("\n✅ Content generator initialized with internal linking")
        print(f"  Internal links enabled: {generator.enable_internal_links}")
        
        if generator.link_manager:
            stats = generator.link_manager.get_statistics()
            print(f"  Links loaded: {stats['total_links']}")
        
        # Test with a sample generation (without actual API call)
        print("\n📄 Testing link prompt generation:")
        if generator.internal_linker:
            test_suggestions = [
                (generator.link_manager.links[0], "CDN solution", 0.85),
                (generator.link_manager.links[1], "cloud platform", 0.75)
            ] if generator.link_manager and len(generator.link_manager.links) >= 2 else []
            
            if test_suggestions:
                prompt_section = generator.internal_linker.generate_link_prompt_section(test_suggestions)
                print("  Link prompt section generated successfully")
                print("\nPrompt Preview:")
                print("-" * 40)
                print(prompt_section[:500] + "..." if len(prompt_section) > 500 else prompt_section)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing content generator integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n🚀 Starting Internal Link System Tests\n")
    
    results = {
        'Link Manager': test_link_manager(),
        'Internal Linker': test_internal_linker(),
        'Content Generator Integration': test_content_generator_integration()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed successfully!")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())