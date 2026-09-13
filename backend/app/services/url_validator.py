import asyncio
import logging
from typing import Tuple, Optional, Dict, Any, List
import httpx

logger = logging.getLogger("ainews.url_validator")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 "
        "AI-Industry-News-Validator/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class URLValidatorService:
    @staticmethod
    async def validate_url(url: str, timeout: float = 8.0) -> Tuple[bool, int, str, Optional[str]]:
        """
        Validates whether a URL resolves with an HTTP 200-range status code.
        Returns: (is_valid, status_code, final_url, error_message)
        """
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            return False, 0, url, "Invalid URL scheme (must be http or https)"

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers=DEFAULT_HEADERS,
                verify=False, # Avoid strict TLS failures on custom tech blogs
            ) as client:
                # Try HEAD first for efficiency
                try:
                    head_resp = await client.head(url)
                    if 200 <= head_resp.status_code < 300:
                        return True, head_resp.status_code, str(head_resp.url), None
                    elif head_resp.status_code == 404:
                        return False, 404, str(head_resp.url), "HTTP 404 Not Found"
                except Exception:
                    pass # Fall back to GET if HEAD method is disallowed or drops connection

                # Fallback to GET with stream to avoid downloading large payload
                async with client.stream("GET", url) as get_resp:
                    status_code = get_resp.status_code
                    final_url = str(get_resp.url)
                    if 200 <= status_code < 300:
                        return True, status_code, final_url, None
                    else:
                        return False, status_code, final_url, f"HTTP {status_code}"

        except httpx.ConnectTimeout:
            return False, 0, url, "Connection timed out"
        except httpx.ConnectError:
            return False, 0, url, "Failed to connect to host"
        except Exception as e:
            return False, 0, url, str(e)

    @classmethod
    async def validate_urls_batch(cls, urls: List[str], timeout: float = 8.0) -> Dict[str, Dict[str, Any]]:
        """Validates a list of URLs concurrently."""
        tasks = [cls.validate_url(u, timeout=timeout) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        outcome = {}
        for url, res in zip(urls, results):
            if isinstance(res, Exception):
                outcome[url] = {"is_valid": False, "status_code": 0, "final_url": url, "error": str(res)}
            else:
                is_valid, code, final_url, err = res
                outcome[url] = {"is_valid": is_valid, "status_code": code, "final_url": final_url, "error": err}
        return outcome
