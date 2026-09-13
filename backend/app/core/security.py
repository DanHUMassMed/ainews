from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.core.config import settings

security_bearer = HTTPBearer(auto_error=False)

async def verify_editorial_token(credentials: HTTPAuthorizationCredentials = Security(security_bearer)) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    valid_tokens = {settings.EDITORIAL_SECRET_KEY, settings.ADMIN_API_TOKEN}
    if token not in valid_tokens:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid editorial token",
        )
    return token

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security_bearer)) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid administrative credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    if token != settings.ADMIN_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Admin token",
        )
    return token

# Backward compatibility alias
verify_hermes_token = verify_editorial_token
