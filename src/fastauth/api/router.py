# api/router.py
from fastauth.auth.manager import AuthManager
from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

def build_auth_router(auth: AuthManager) -> APIRouter:
    router = APIRouter(prefix="/auth")

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
