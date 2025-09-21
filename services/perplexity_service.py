import os
from typing import Any, Dict, List, Optional

from utils.async_query import AsyncRequests


PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
PERPLEXITY_BASE_URL = "https://api.perplexity.ai"


class PerplexityService:
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or PERPLEXITY_API_KEY
        if not self.api_key:
            raise RuntimeError("PERPLEXITY_API_KEY is not set in the environment")

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "sonar-pro",
        temperature: float = 0.2,
        top_p: float = 0.9,
        max_tokens: int = 1200,
        reasoning_effort: Optional[str] = None,
        web_search_options: Optional[Dict[str, Any]] = None,
        search_domain_filter: Optional[List[str]] = None,
        recency_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        request_body: Dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "search_mode": "web",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
            "return_images": False,
            "return_related_questions": False,
        }

        if reasoning_effort:
            request_body["reasoning_effort"] = reasoning_effort
        if web_search_options:
            request_body["web_search_options"] = web_search_options
        if search_domain_filter:
            request_body["search_domain_filter"] = search_domain_filter
        if recency_filter:
            request_body["search_recency_filter"] = recency_filter

        url = f"{PERPLEXITY_BASE_URL}/chat/completions"
        response = await AsyncRequests.post(url, headers=self._headers(), json=request_body)
        response.raise_for_status()
        return response.json()


