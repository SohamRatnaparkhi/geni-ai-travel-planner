import concurrent
import concurrent.futures
import httpx
import asyncio
import functools
from typing import Any, Optional
import logging
import requests
from urllib.parse import quote, urlparse, urlunparse


logger = logging.getLogger("cortex_logger")

default_threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=10)

async def forcefully_async(fn: Any, *args: Any, threadpool=default_threadpool, **kwargs: Any) -> Any:
    """
    If fn is already a coroutine function, call it and await the result.
    If the caller passes an actual coroutine object, await it directly.
    Otherwise run fn in the shared thread-pool so it won't block the event loop.
    """

    if asyncio.iscoroutine(fn):
        return await fn

    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)

    loop = asyncio.get_running_loop()
    logger.debug("run %s in executor %s", fn.__name__, threadpool)

    if kwargs:
        func_with_kwargs = functools.partial(fn, **kwargs)
        return await loop.run_in_executor(threadpool, func_with_kwargs, *args)
    else:
        return await loop.run_in_executor(threadpool, fn, *args)

class AsyncRequests:
    """
    Drop in async replacement for requests library.
    """
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        """Get or create the singleton httpx.AsyncClient instance."""
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(timeout=30.0, connect=10.0),
                http2=True,
                follow_redirects=True,
            )
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Close the client connection"""
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None

    @classmethod
    def _encode_url(cls, url: str) -> str:
        """
        Encode URL to handle spaces and special characters.
        Only encodes the path component, preserving the scheme, netloc, and query parameters.
        """
        try:
            parsed = urlparse(url)
            
            encoded_path = quote(parsed.path, safe='/')
            
            encoded_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                encoded_path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return encoded_url
        except Exception as e:
            logger.warning(f"Failed to encode URL {url}: {e}. Using original URL.")
            return url

    @classmethod
    async def get(cls, url: str, **kwargs) -> httpx.Response:
        """Async GET request."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().get(encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"Async GET request failed for {encoded_url}: {e}. Forcefully retrying...")
            try:
                return await forcefully_async(requests.get, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"Sync GET request failed for {encoded_url}: {e}. Forcefully retrying...")
                raise

    @classmethod
    async def post(cls, url: str, **kwargs) -> httpx.Response:
        """Async POST request."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().post(encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"Async POST request failed for {encoded_url}: {e}. Forcefully retrying...")
            try:
                return await forcefully_async(requests.post, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"Sync POST request failed for {encoded_url}: {e}. Forcefully retrying...")
                raise

    @classmethod
    async def put(cls, url: str, **kwargs) -> httpx.Response:
        """Async PUT request."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().put(encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"Async PUT request failed for {encoded_url}: {e}. Forcefully retrying...")
            try:
                return await forcefully_async(requests.put, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"Sync PUT request failed for {encoded_url}: {e}. Forcefully retrying...")
                raise

    @classmethod
    async def patch(cls, url: str, **kwargs) -> httpx.Response:
        """Async PATCH request."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().patch(encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"Async PATCH request failed for {encoded_url}: {e}. Forcefully retrying...")
            try:
                return await forcefully_async(requests.patch, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"Sync PATCH request failed for {encoded_url}: {e}. Forcefully retrying...")
                raise

    @classmethod
    async def delete(cls, url: str, **kwargs) -> httpx.Response:
        """Async DELETE request."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().delete(encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"Async DELETE request failed for {encoded_url}: {e}. Forcefully retrying...")
            try:
                return await forcefully_async(requests.delete, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"Sync DELETE request failed for {encoded_url}: {e}. Forcefully retrying...")
                raise

    @classmethod
    async def head(cls, url: str, **kwargs) -> httpx.Response:
        """Async HEAD request."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().head(encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"Async HEAD request failed for {encoded_url}: {e}. Forcefully retrying...")
            try:
                return await forcefully_async(requests.head, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"Sync HEAD request failed for {encoded_url}: {e}. Forcefully retrying...")
                raise

    @classmethod
    async def options(cls, url: str, **kwargs) -> httpx.Response:
        """Async OPTIONS request."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().options(encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"Async OPTIONS request failed for {encoded_url}: {e}. Forcefully retrying...")
            try:
                return await forcefully_async(requests.options, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"Sync OPTIONS request failed for {encoded_url}: {e}. Forcefully retrying...")
                raise

    @classmethod
    async def request(cls, method: str, url: str, **kwargs) -> httpx.Response:
        """Generic async request method."""
        encoded_url = cls._encode_url(url)
        try:
            return await cls.get_client().request(method, encoded_url, **kwargs)
        except Exception as e:
            logger.error(f"{method.upper()} request failed for {encoded_url}: {e}")
            try:
                return await forcefully_async(requests.request, method, encoded_url, threadpool=default_threadpool, **kwargs)
            except Exception as e:
                logger.error(f"{method.upper()} request failed for {encoded_url}: {e}")
                raise

async def async_batch_requests(requests_data: list, max_concurrent: int = 10) -> list:
    """
    Execute multiple HTTP requests concurrently with a limit on concurrent requests.
    
    Args:
        requests_data: List of dictionaries with 'method', 'url', and optional 'kwargs'
        max_concurrent: Maximum number of concurrent requests
        
    Returns:
        List of httpx.Response objects in the same order as requests_data
        
    Example:
        requests_data = [
            {'method': 'GET', 'url': 'https://api.example.com/1'},
            {'method': 'POST', 'url': 'https://api.example.com/2', 'kwargs': {'json': {'key': 'value'}}},
        ]
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def make_request(request_data):
        async with semaphore:
            method = request_data['method'].upper()
            url = request_data['url']
            kwargs = request_data.get('kwargs', {})
            
            return await AsyncRequests.request(method, url, **kwargs)
    
    tasks = [make_request(req_data) for req_data in requests_data]
    return await asyncio.gather(*tasks, return_exceptions=True)



class AsyncResultWrapper:
    def __init__(self, result):
        self._result = result

    def result(self):
        return self._result
