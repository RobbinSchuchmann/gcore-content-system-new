"""
Product Data Loader for Enhanced Gcore Products
Dynamically loads and processes enhanced product data for CTA generation
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

class ProductLoader:
    """Loads and manages enhanced Gcore product data"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data" / "gcore_products_enhanced.json"
        self._products_data = None
        self._load_products()
    
    def _load_products(self):
        """Load enhanced product data from JSON file"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self._products_data = json.load(f)
        except Exception as e:
            print(f"Error loading enhanced products data: {e}")
            self._products_data = {"products": {}}
    
    def get_all_products(self) -> Dict[str, Any]:
        """Get all product data"""
        return self._products_data.get("products", {})
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get specific product data by ID"""
        products = self.get_all_products()
        return products.get(product_id)
    
    def get_product_list(self) -> List[Dict[str, str]]:
        """Get simplified list of products for UI selection"""
        products = self.get_all_products()
        product_list = []
        
        for product_id, product_data in products.items():
            product_list.append({
                "id": product_id,
                "name": product_data.get("name", product_id.title()),
                "full_name": product_data.get("full_name", product_data.get("name", "")),
                "tagline": product_data.get("tagline", ""),
                "description": product_data.get("description", "")
            })
        
        return sorted(product_list, key=lambda x: x["name"])
    
    def get_cta_templates(self, product_id: str) -> Dict[str, str]:
        """Get all CTA templates for a specific product"""
        product = self.get_product(product_id)
        if not product:
            return {}
        
        return product.get("cta_templates", {})
    
    def get_best_cta_template(self, product_id: str, context_keywords: List[str] = None) -> str:
        """
        Get the most appropriate CTA template based on context
        
        Args:
            product_id: The product identifier
            context_keywords: Keywords from article context to help select best CTA
            
        Returns:
            The best matching CTA template text
        """
        templates = self.get_cta_templates(product_id)
        if not templates:
            return ""
        
        # If no context provided, return the first template
        if not context_keywords:
            return list(templates.values())[0]
        
        # Create keyword mappings for different CTA types
        cta_keyword_map = {
            "performance": ["speed", "fast", "latency", "performance", "optimization", "accelerate"],
            "cost": ["cost", "price", "save", "free", "budget", "affordable", "cheap"],
            "enterprise": ["enterprise", "business", "corporate", "organization", "company"],
            "security": ["security", "secure", "protection", "safe", "ddos", "attack"],
            "scalability": ["scale", "scalable", "growth", "expand", "flexible"],
            "developer": ["developer", "api", "integration", "code", "programming"],
            "compliance": ["compliance", "regulation", "gdpr", "hipaa", "pci"],
            "ai_ml": ["ai", "machine learning", "ml", "artificial intelligence", "model"],
            "global": ["global", "worldwide", "international", "regions"],
            "simplicity": ["easy", "simple", "intuitive", "user-friendly"]
        }
        
        # Score each template based on keyword matches
        template_scores = {}
        context_lower = [k.lower() for k in context_keywords]
        
        for template_name, template_text in templates.items():
            score = 0
            
            # Check if template name matches context
            if template_name in cta_keyword_map:
                matching_keywords = cta_keyword_map[template_name]
                for keyword in matching_keywords:
                    if any(keyword in context_word for context_word in context_lower):
                        score += 10
            
            # Check if template content matches context
            template_lower = template_text.lower()
            for context_word in context_lower:
                if context_word in template_lower:
                    score += 5
            
            template_scores[template_name] = score
        
        # Return the highest scoring template, or first if tied at 0
        if max(template_scores.values()) > 0:
            best_template = max(template_scores, key=template_scores.get)
            return templates[best_template]
        else:
            return list(templates.values())[0]
    
    def get_product_info_for_prompt(self, product_id: str, selected_features: List[str] = None) -> str:
        """
        Generate product information string for prompt injection
        
        Args:
            product_id: The product identifier
            selected_features: Specific features to highlight
            
        Returns:
            Formatted product information string
        """
        product = self.get_product(product_id)
        if not product:
            return f"Product: {product_id} (data not found)"
        
        info_parts = []
        info_parts.append(f"Product: {product.get('full_name', product.get('name', product_id))}")
        info_parts.append(f"URL: {product.get('url', '')}")
        info_parts.append(f"Tagline: {product.get('tagline', '')}")
        
        # Key features (limit to most relevant)
        if product.get('key_features'):
            info_parts.append("Key Features:")
            features = product['key_features']
            
            # If specific features selected, prioritize those
            if selected_features:
                relevant_features = []
                for feature in features:
                    if any(sel_feat.lower() in feature.lower() for sel_feat in selected_features):
                        relevant_features.append(feature)
                if relevant_features:
                    features = relevant_features[:5]
                else:
                    features = features[:5]
            else:
                features = features[:5]
            
            for feature in features:
                info_parts.append(f"  • {feature}")
        
        # Performance metrics (if available)
        if product.get('performance_metrics'):
            info_parts.append("Performance Metrics:")
            for metric, value in list(product['performance_metrics'].items())[:3]:
                info_parts.append(f"  • {metric}: {value}")
        
        # Competitive advantages (top 3)
        if product.get('competitive_advantages'):
            info_parts.append("Key Differentiators:")
            for advantage in product['competitive_advantages'][:3]:
                info_parts.append(f"  • {advantage}")
        
        return "\n".join(info_parts)
    
    def suggest_relevant_products(self, article_keywords: List[str]) -> List[str]:
        """
        Suggest relevant products based on article keywords
        
        Args:
            article_keywords: Keywords from the article content
            
        Returns:
            List of product IDs ranked by relevance
        """
        if not article_keywords:
            return []
        
        # Get topic mapping from enhanced data
        topic_mapping = self._products_data.get("topic_mapping", {})
        
        # Score products based on keyword matches
        product_scores = {}
        article_lower = [k.lower() for k in article_keywords]
        
        for topic, product_list in topic_mapping.items():
            if any(topic in keyword for keyword in article_lower):
                for product_id in product_list:
                    product_scores[product_id] = product_scores.get(product_id, 0) + 10
        
        # Also check direct keyword matches in product data
        for product_id, product_data in self.get_all_products().items():
            product_text = json.dumps(product_data).lower()
            for keyword in article_lower:
                if keyword in product_text:
                    product_scores[product_id] = product_scores.get(product_id, 0) + 5
        
        # Sort by score and return top products
        sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)
        return [product_id for product_id, score in sorted_products[:3]]
    
    def get_product_categories(self) -> Dict[str, List[str]]:
        """Get product categories for UI organization"""
        return self._products_data.get("product_categories", {})

# Global instance for easy access
product_loader = ProductLoader()