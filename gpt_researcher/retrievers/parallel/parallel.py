"""Parallel Search API retriever for GPT Researcher.

Adapts Parallel's Search API (objective + keyword queries -> LLM-optimized
excerpts) into the retriever contract GPT Researcher expects:
    search() -> list[{"href": str, "body": str, "title": str}]

Docs: https://docs.parallel.ai/api-reference/search/search
"""

import os

from parallel import Parallel


class ParallelSearch:
    """GPT Researcher retriever backed by Parallel's Search API."""

    def __init__(self, query, headers=None, query_domains=None, **kwargs):
        self.query = query
        self.headers = headers or {}
        self.query_domains = query_domains or None

        api_key = self.headers.get("parallel_api_key") or os.environ.get("PARALLEL_API_KEY")
        if not api_key:
            print(
                "Parallel API key not found. Set the PARALLEL_API_KEY environment "
                "variable or pass 'parallel_api_key' in headers."
            )
            self.client = None
            return
        self.client = Parallel(api_key=api_key)

    def search(self, max_results=10):
        """Run the search and return GPT Researcher-shaped results."""
        if self.client is None:
            return []

        try:
            response = self.client.search(
                objective=self.query,
                search_queries=[self.query],
                mode="basic",
            )
        except Exception as e:
            print(f"Error: {e}. Failed fetching sources from Parallel. Resulting in empty response.")
            return []

        results = getattr(response, "results", None) or []
        search_response = []
        for item in results[:max_results]:
            excerpts = getattr(item, "excerpts", None) or []
            body = "\n".join(excerpts)
            search_response.append({
                "href": getattr(item, "url", "") or "",
                "body": body,
                "title": getattr(item, "title", "") or "",
            })
        return search_response
