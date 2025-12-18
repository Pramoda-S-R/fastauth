# api/router.py
from typing import TYPE_CHECKING
from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

if TYPE_CHECKING:
    from ..auth.manager import AuthManager

def build_auth_router(auth: "AuthManager") -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["Auth"])

    @router.post("/signup")
    async def signup():
        pass

    @router.post("/login")
    async def login():
        pass

    @router.post("/logout")
    async def logout(response: Response):
        pass

    if auth.oauth:
        @router.get("/oauth/{provider}")
        async def oauth_login(provider: str):
            return RedirectResponse(
                auth.oauth.get_authorization_url()
            )

    return router
