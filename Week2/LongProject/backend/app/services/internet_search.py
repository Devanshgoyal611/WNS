import requests
from ddgs import DDGS 
import arxiv
from typing import List, Dict

class InternetSearchService:
    def __init__(self):
        pass
    
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        try:
            search_results = []
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=5)
                for r in results:
                    title = r.get("title")
                    url = r.get("href")
                    snippet = r.get("body")
                    search_results.append({
                        "title": title,
                        "link": url,
                        "description": snippet
                    })
                    
            return search_results
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    async def search_arxiv(self, query: str, max_results: int = 3) -> List[Dict]:
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            results = []
            for result in client.results(search):
                results.append({
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "pdf_url": result.pdf_url,
                    "published": result.published.strftime("%Y-%m-%d")
                })
            return results
        except Exception as e:
            print(f"Arxiv search error: {e}")
            return []

internet_search_service = InternetSearchService()