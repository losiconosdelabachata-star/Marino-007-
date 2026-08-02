"""
Web Search Integration
Searches the internet for content related to blog topics
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WebSearchClient:
    def __init__(self):
        """Initialize web search (using Google Search API or DuckDuckGo)"""
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')

    def search_google(self, query, num_results=3):
        """Search using Google Custom Search API"""
        if not self.api_key or not self.search_engine_id:
            print("⚠️  Google Search API not configured. Using fallback.")
            return self.search_duckduckgo(query, num_results)

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': self.api_key,
                'cx': self.search_engine_id,
                'num': num_results
            }

            response = requests.get(url, params=params)
            results = response.json()

            articles = []
            if 'items' in results:
                for item in results['items']:
                    articles.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': item.get('displayLink', '')
                    })

            return articles
        except Exception as e:
            print(f"❌ Google search error: {e}")
            return []

    def search_duckduckgo(self, query, num_results=3):
        """Fallback search using DuckDuckGo (no API key required)"""
        try:
            import json
            from urllib.parse import urlencode

            # Using DuckDuckGo instant answer API
            params = {
                'q': query,
                'format': 'json',
                'no_redirect': 1
            }

            url = f"https://api.duckduckgo.com/?{urlencode(params)}"
            response = requests.get(url, timeout=5)
            data = response.json()

            articles = []

            # Add abstract if available
            if data.get('AbstractText'):
                articles.append({
                    'title': data.get('AbstractTitle', 'Summary'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('AbstractText', ''),
                    'source': 'DuckDuckGo'
                })

            # Add related topics
            for topic in data.get('RelatedTopics', [])[:num_results]:
                if 'Text' in topic:
                    articles.append({
                        'title': topic.get('FirstURL', '').split('/')[-1],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'DuckDuckGo'
                    })

            return articles[:num_results]

        except Exception as e:
            print(f"❌ DuckDuckGo search error: {e}")
            return []

    def search_member_news(self, member_name):
        """Search for news about a specific member"""
        query = f"{member_name} Los Iconos de la Bachata news"
        return self.search_google(query, num_results=5)

    def search_topic(self, topic):
        """Search for information about a topic"""
        return self.search_google(topic, num_results=3)

if __name__ == "__main__":
    client = WebSearchClient()
    results = client.search_topic("Los Iconos de la Bachata")
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  - {result['title']}")
        print(f"    {result['snippet'][:100]}...")
