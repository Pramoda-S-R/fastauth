# api/router.py
from pydantic import create_model
from typing import TYPE_CHECKING
from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

if TYPE_CHECKING:
    from ..auth.manager import AuthManager


def build_auth_router(auth: "AuthManager") -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["Auth"])

    # Create a SignupRequest model dynamically from the user schema, excluding 'id'
    signup_fields = {}
    for name, field in auth.schema.model_fields.items():
        if name == "id":
            continue
        default = ... if field.is_required() else field.default
        signup_fields[name] = (field.annotation, default)

    SignupRequest = create_model("SignupRequest", **signup_fields)

    # Create a LoginRequest model dynamically
    # All login fields are optional, but at least one should be provided
    login_fields_dict = {
        name: (auth.schema.model_fields[name].annotation, None)
        for name in auth.config.login_fields
        if name in auth.schema.model_fields
    }
    
    # Ensure password is always required for login
    login_fields_dict["password"] = (str, ...)

    LoginRequest = create_model("LoginRequest", **login_fields_dict)

    @router.post("/signup")
    async def signup(req: SignupRequest, response: Response): # type: ignore
        user = await auth.user.create(req.model_dump())
        await auth.session.create(user_id=user.id, data={})
        
        # Let the strategy set cookies/headers on the response object
        await auth.strategy.issue(response, user_id=user.id)
        
        # Return the body data as a dict. 
        # FastAPI will merge this with headers/cookies from the 'response' parameter.
        return {"user_id": user.id}

    @router.post("/login")
    async def login(req: LoginRequest): # type: ignore
        # Implementation will follow based on searching for user with provided login_fields
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
