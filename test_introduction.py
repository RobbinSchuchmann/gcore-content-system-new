#!/usr/bin/env python3
"""
Test script to verify introduction generation is working properly
"""

from core.content_generator import ContentGenerator
from config import ANTHROPIC_API_KEY
import json

def test_introduction_generation():
    """Test that introduction generation works correctly"""
    
    # Check if API key is available
    if not ANTHROPIC_API_KEY:
        print("❌ No Anthropic API key found. Please set ANTHROPIC_API_KEY in .env")
        return False
    
    print("Testing introduction generation...")
    print("-" * 50)
    
    # Initialize generator
    generator = ContentGenerator()
    
    # Test topic
    topic = "cloud security"
    
    # Sample headings for context
    headings = [
        {"level": "H2", "text": "What is cloud security?"},
        {"level": "H2", "text": "Types of cloud security"},
        {"level": "H2", "text": "How to implement cloud security"},
        {"level": "H2", "text": "Cloud security best practices"}
    ]
    
    # Sample research data
    research_data = {
        "data": {
            "facts": [
                "Cloud security protects data, applications, and infrastructure in cloud computing",
                "93% of organizations use cloud services",
                "The global cloud security market is expected to reach $68.5 billion by 2025"
            ],
            "statistics": [
                {"text": "60% of corporate data is stored in the cloud"},
                {"text": "95% of cloud security failures are due to human error"}
            ]
        }
    }
    
    # Test generation
    print(f"Generating introduction for topic: '{topic}'")
    print()
    
    result = generator.generate_introduction(
        topic=topic,
        headings=headings,
        research_data=research_data,
        include_gcore=False
    )
    
    # Check result
    if result.get('status') == 'success':
        print("✅ Introduction generated successfully!")
        print()
        print("Generated Introduction:")
        print("-" * 50)
        print(result.get('content', 'No content'))
        print("-" * 50)
        print()
        print(f"Word count: {result.get('word_count', 0)}")
        
        # Verify it starts correctly
        content = result.get('content', '')
        if content.lower().startswith(f"{topic} is"):
            print("✅ Introduction starts with proper definition format")
        else:
            print(f"⚠️  Introduction doesn't start with '{topic} is...'")
            print(f"   Actual start: {content[:50]}...")
        
        return True
    else:
        print("❌ Failed to generate introduction")
        print(f"   Error: {result.get('error', result.get('message', 'Unknown error'))}")
        return False

if __name__ == "__main__":
    success = test_introduction_generation()
    print()
    if success:
        print("🎉 Introduction generation is working correctly!")
    else:
        print("⚠️  There are issues with introduction generation")