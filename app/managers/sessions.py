from fastapi import HTTPException, status, Response, Request
import jwt
from typing import Dict

class SessionManager:
    """Session Manager for handling user authentication sessions."""

    def __init__(self, secret_key: str, jwt_expiration: int, refresh_token_expiration: int):
        self.secret_key = secret_key
        self.jwt_expiration = jwt_expiration  # e.g., 2 hours
        self.refresh_token_expiration = refresh_token_expiration  # e.g., 30 days

    def validate_token(self, token: str) -> dict:
        """Validate and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")
        except jwt.InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    def set_tokens_in_cookies(self, response: Response, tokens: dict[str, str]):
        """Set access and refresh tokens in cookies."""
        response.set_cookie(
            key="access_token", value=tokens["access_token"], httponly=True, max_age=self.jwt_expiration, secure=True
        )
        response.set_cookie(
            key="refresh_token", value=tokens["refresh_token"], httponly=True, max_age=self.refresh_token_expiration, secure=True
        )

    def clear_tokens(self, response: Response):
        """Clear access and refresh tokens from cookies."""
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

    def get_session_from_cookies(self, request: Request) -> dict:
        """Retrieve session (user) from cookies."""
        access_token = request.cookies.get("access_token")
        if access_token:
            return self.validate_token(access_token)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Access token is missing or invalid.")
