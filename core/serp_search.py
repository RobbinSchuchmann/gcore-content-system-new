"""
SERP Search Service using SearchAPI.io
Fetches top 10 Google search results for competitor analysis
"""

import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse


class SERPSearchService:
    """Service for fetching Google SERP results via SearchAPI.io"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.searchapi.io/api/v1/search"

    def search(
        self,
        query: str,
        num_results: int = 10,
        location: str = "United States",
        language: str = "en",
        country: str = "us"
    ) -> Dict:
        """
        Perform a Google search and return organic results.

        Args:
            query: Search query string
            num_results: Number of results to fetch (default 10)
            location: Geographic location for search
            language: Interface language code
            country: Country code for search

        Returns:
            Dict with 'success', 'results', and optional 'error' keys
        """
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "location": location,
                "hl": language,
                "gl": country
            }

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Extract organic results
            organic_results = data.get("organic_results", [])

            # Format results for display
            formatted_results = []
            for result in organic_results[:num_results]:
                formatted_results.append({
                    "position": result.get("position", 0),
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "domain": self._extract_domain(result.get("link", "")),
                    "snippet": result.get("snippet", ""),
                    "displayed_link": result.get("displayed_link", "")
                })

            return {
                "success": True,
                "results": formatted_results,
                "total_results": data.get("search_information", {}).get("total_results", 0),
                "query": query
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timed out. Please try again.",
                "results": []
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "results": []
            }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "")
        except:
            return url

    def filter_results(
        self,
        results: List[Dict],
        exclude_domains: Optional[List[str]] = None,
        include_only_domains: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Filter search results by domain.

        Args:
            results: List of search results
            exclude_domains: Domains to exclude (e.g., ['gcore.com'])
            include_only_domains: Only include these domains

        Returns:
            Filtered list of results
        """
        if not exclude_domains:
            exclude_domains = []

        # Normalize domains
        exclude_domains = [d.lower().replace("www.", "") for d in exclude_domains]

        filtered = []
        for result in results:
            domain = result.get("domain", "").lower()

            # Skip excluded domains
            if any(excl in domain for excl in exclude_domains):
                continue

            # If include_only is specified, check that
            if include_only_domains:
                include_only_domains = [d.lower().replace("www.", "") for d in include_only_domains]
                if not any(incl in domain for incl in include_only_domains):
                    continue

            filtered.append(result)

        return filtered
