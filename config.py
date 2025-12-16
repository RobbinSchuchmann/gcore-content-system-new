import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# API Configuration - supports both local .env and Streamlit Cloud secrets
try:
    import streamlit as st
    # Try to get from Streamlit secrets first, fallback to env vars
    try:
        ANTHROPIC_API_KEY = st.secrets['ANTHROPIC_API_KEY']
    except (KeyError, FileNotFoundError):
        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    try:
        PERPLEXITY_API_KEY = st.secrets['PERPLEXITY_API_KEY']
    except (KeyError, FileNotFoundError):
        PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
except (ImportError, AttributeError):
    # Fallback to environment variables if not running in Streamlit
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

# Model Configuration
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"  # Latest Claude Sonnet 4.5 model
DEFAULT_TEMPERATURE = 0.7  # Higher temperature for more natural, human-like writing while maintaining accuracy
MAX_TOKENS = 4000

# Perplexity Configuration
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar"

# SearchAPI Configuration (for SERP analysis)
SEARCHAPI_API_KEY = "12HpcjrPS2Wj5AtqJqjzRKpR"
SEARCHAPI_URL = "https://www.searchapi.io/api/v1/search"

# Content Generation Settings
CONTENT_SETTINGS = {
    'max_heading_length': 100,
    'min_section_words': 100,
    'max_section_words': 500,
    'default_language': 'en',
    'use_contractions': True,
    'sentence_case_headings': True,
    'formal_tone': True
}

# Gcore Specific Information
GCORE_INFO = {
    'company': 'Gcore',
    'pops': '210+',
    'average_latency': '30ms',
    'services': {
        'cdn': {
            'name': 'CDN',
            'key_features': [
                '210+ Points of Presence',
                '30ms average global latency',
                'DDoS protection',
                'Real-time analytics',
                'SSL/TLS encryption'
            ]
        },
        'edge_cloud': {
            'name': 'Edge Cloud',
            'key_features': [
                'GPU instances',
                'Bare metal servers',
                'Virtual machines',
                'Kubernetes support',
                'Global infrastructure'
            ]
        },
        'ai_infrastructure': {
            'name': 'AI Infrastructure',
            'key_features': [
                'GPU clusters',
                'ML model deployment',
                'Inference optimization',
                'Distributed training',
                'AutoML capabilities'
            ]
        }
    },
    'differentiators': [
        'Global edge network with 210+ PoPs',
        'Average 30ms latency worldwide',
        'Enterprise-grade security',
        'Cost-effective pricing',
        '24/7 expert support'
    ]
}

# File Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
SAVED_CONTENT_DIR = DATA_DIR / 'saved_content'
TEMPLATES_DIR = BASE_DIR / 'templates'

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SAVED_CONTENT_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Export Settings
EXPORT_FORMATS = {
    'markdown': {
        'extension': '.md',
        'mime_type': 'text/markdown'
    },
    'html': {
        'extension': '.html',
        'mime_type': 'text/html'
    },
    'text': {
        'extension': '.txt',
        'mime_type': 'text/plain'
    },
    'json': {
        'extension': '.json',
        'mime_type': 'application/json'
    },
    'docx': {
        'extension': '.docx',
        'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
}

# Quality Check Thresholds
QUALITY_THRESHOLDS = {
    'min_gcore_compliance': 80,  # Minimum percentage for Gcore style compliance
    'max_ai_words': 3,  # Maximum allowed AI-sounding words
    'min_seo_score': 75,  # Minimum SEO optimization score
    'min_readability_score': 60,  # Minimum readability score
    'max_sentence_length': 30,  # Maximum words per sentence
    'max_paragraph_length': 150  # Maximum words per paragraph
}

# Research Settings
RESEARCH_SETTINGS = {
    'max_sources': 10,
    'search_depth': 'comprehensive',
    'include_statistics': True,
    'include_examples': True,
    'focus_on_recent': True,  # Prioritize recent information (last 2 years)
    'exclude_competitors': False  # Whether to exclude direct competitor mentions
}

# Validation Rules
VALIDATION_RULES = {
    'require_direct_answer': True,  # Each section must directly answer its heading question
    'require_keyword_density': True,  # Check for appropriate keyword usage
    'require_semantic_triples': True,  # Ensure semantic relationships are present
    'require_gcore_context': True,  # Include Gcore-specific information where relevant
}

def validate_api_keys():
    """Check if required API keys are configured"""
    missing_keys = []
    
    if not ANTHROPIC_API_KEY:
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if not PERPLEXITY_API_KEY:
        missing_keys.append("PERPLEXITY_API_KEY")
    
    if missing_keys:
        return False, f"Missing API keys: {', '.join(missing_keys)}. Please check your .env file."
    
    return True, "All API keys configured successfully."

def get_gcore_context(service=None):
    """Get Gcore-specific context for content generation"""
    context = {
        'company': GCORE_INFO['company'],
        'global_reach': f"{GCORE_INFO['pops']} Points of Presence",
        'performance': f"{GCORE_INFO['average_latency']} average latency",
        'differentiators': GCORE_INFO['differentiators']
    }
    
    if service and service in GCORE_INFO['services']:
        context['service'] = GCORE_INFO['services'][service]
    
    return context