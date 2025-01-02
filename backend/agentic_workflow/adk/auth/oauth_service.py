from typing import Dict
import httpx
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime


class OAuthResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None


class OAuthService:
    def __init__(
        self, token_url: str, client_id: str, client_secret: str, redirect_uri: str
    ):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def exchange_code_for_token(self, code: str) -> OAuthResponse:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                    },
                )
                response.raise_for_status()
                return OAuthResponse(**response.json())
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to exchange code: {str(e)}"
            )

    async def refresh_token(self, refresh_token: str) -> OAuthResponse:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
                response.raise_for_status()
                return OAuthResponse(**response.json())
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to refresh token: {str(e)}"
            )
