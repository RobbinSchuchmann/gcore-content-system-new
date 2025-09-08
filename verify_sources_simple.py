"""
Verify that the source manager properly formats sources with URLs
"""

from core.source_manager import SourceManager
import json

# Create a mock response similar to what Perplexity returns
mock_sources = [
    {
        'title': 'What is Cloud Storage? - TechTarget',
        'url': 'https://www.techtarget.com/searchstorage/definition/cloud-storage',
        'date': '2025-06-11',
        'type': 'web'
    },
    {
        'title': 'Cloud Storage Guide - AWS',
        'url': 'https://aws.amazon.com/what-is/cloud-storage/',
        'date': '2025',
        'type': 'web'
    },
    {
        'title': 'Understanding Cloud Storage - Google Cloud',
        'url': 'https://cloud.google.com/learn/what-is-cloud-storage',
        'date': '2025-07-18',
        'type': 'web'
    }
]

# Test source formatting
source_manager = SourceManager()

print("Testing Source Reference Generation with URLs")
print("=" * 60)

# Generate reference section
reference_section = source_manager.generate_source_reference_section(mock_sources)
print(reference_section)

print("\n" + "=" * 60)
print("Testing inline citation formatting:")
print("-" * 40)

# Test inline citation
fact = "Cloud storage can achieve 99.999999999% durability"
formatted = source_manager.format_inline_citation(fact, mock_sources[0])
print(f"Original: {fact}")
print(f"Formatted: {formatted}")

print("\n" + "=" * 60)
print("Testing statistic formatting:")
print("-" * 40)

# Test statistic formatting
stat = "Organizations reduce storage costs by 40%"
formatted_stat = source_manager.format_statistic_with_source(stat, mock_sources[1])
print(f"Original: {stat}")
print(f"Formatted: {formatted_stat}")