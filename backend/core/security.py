from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

security = HTTPBearer()


def verify_firebase_token(creds: HTTPAuthorizationCredentials = Security(security)):
    try:
        decoded_token = auth.verify_id_token(creds.credentials)
        return decoded_token
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )
