"""URL HTTP 200 Status Validation Tool for Google ADK Agents.

PRD Section 36 & Quality Gate: Validates that primary source links resolve
with HTTP 200-range status codes before inclusion in briefings.
"""

from typing import Dict, Any
from backend.app.services.url_validator import URLValidatorService

async def validate_source_url(url: str) -> Dict[str, Any]:
    """Validates whether a source URL resolves with HTTP 200 OK.
    
    Args:
        url: The web URL to validate.
        
    Returns:
        Dict with is_valid, status_code, final_url, and error.
    """
    is_valid, status_code, final_url, error = await URLValidatorService.validate_url(url)
    return {
        "url": url,
        "is_valid": is_valid,
        "status_code": status_code,
        "final_url": final_url,
        "error": error,
    }
