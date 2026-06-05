"""
Google OAuth Authentication — EFB Underwriter
=============================================
Verifies Google ID tokens sent as Authorization: Bearer <token> headers.
No database required — Google is the source of truth.

Setup (one-time):
  1. Go to https://console.cloud.google.com/apis/credentials
  2. Create OAuth 2.0 Client ID → Web application
  3. Add authorized origins: http://localhost:5173, https://your-vercel-url.vercel.app
  4. Add GOOGLE_CLIENT_ID to .env (backend) and VITE_GOOGLE_CLIENT_ID (.env in frontend)
"""

import os
import logging
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)

# Google OAuth Client ID — set in .env
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

# Allowed email domains / addresses (optional — leave empty to allow any Google account)
# To restrict to Shieldstone team only, set ALLOWED_EMAILS in .env as comma-separated list
# e.g. ALLOWED_EMAILS=evan@shieldstone.co,fahd@shieldstone.co,alton@shieldstone.co
ALLOWED_EMAILS_RAW = os.environ.get("ALLOWED_EMAILS", "")
ALLOWED_EMAILS: set[str] = {
    e.strip().lower() for e in ALLOWED_EMAILS_RAW.split(",") if e.strip()
}

security = HTTPBearer(auto_error=False)


def verify_google_token(token: str) -> dict:
    """
    Verify a Google ID token and return the decoded payload.
    Raises HTTPException 401 if invalid.
    """
    # Read at call time (not import time) so env set after import — e.g. at migration / in tests —
    # is honored. Production sets GOOGLE_CLIENT_ID before launch, so behavior is unchanged there.
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "") or GOOGLE_CLIENT_ID
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GOOGLE_CLIENT_ID not configured on server",
        )
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            client_id,
        )
        return idinfo
    except ValueError as e:
        logger.warning(f"Invalid Google token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> dict:
    """
    FastAPI dependency — verifies the Bearer token and returns the user payload.
    Use as: `user: dict = Depends(get_current_user)`

    Returns a dict with keys: sub, email, name, picture, email_verified
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = verify_google_token(credentials.credentials)

    # Optional email allowlist check
    if ALLOWED_EMAILS:
        email = user.get("email", "").lower()
        if email not in ALLOWED_EMAILS:
            logger.warning(f"Unauthorized access attempt from: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not authorized to access this tool",
            )

    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Optional[dict]:
    """
    Same as get_current_user but returns None instead of raising if no token.
    Used for endpoints where auth is checked but not strictly required.
    """
    if not credentials:
        return None
    try:
        return verify_google_token(credentials.credentials)
    except HTTPException:
        return None
