from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from backend.utils.security import SECRET_KEY, ALGORITHM

security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT bearer token and return simple user payload.
    Raises 401 on failure.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # payload should contain 'sub' or 'username'
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
