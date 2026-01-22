import uuid
from typing import List, Optional

from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastauth.auth.config import AuthConfig
from fastauth.auth.manager import AuthManager
from fastauth.sessions.memory import MemorySessionStore
from fastauth.strategy.jwt import JWTStrategy

origins = ["*"]


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middleware


class AppUser(BaseModel):
    id: str
    email: str
    username: str
    phone: Optional[str] = None
    password: str


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class User:
    def __init__(self):
        self.store = {}

    async def create(self, **kwargs) -> AppUser:
        user_id = str(uuid.uuid4())
        user = AppUser(id=user_id, **kwargs)
        self.store[user_id] = kwargs
        return user

    async def delete(self, user_id: str):
        del self.store[user_id]

    async def get(self, user_id: str) -> AppUser | None:
        return AppUser(id=user_id, **self.store.get(user_id))

    async def find(self, **kwargs) -> AppUser | None:
        if "email" in kwargs:
            user_id = next(
                (u for u, v in self.store.items() if v.get("email") == kwargs["email"]),
                None,
            )
        elif "username" in kwargs:
            user_id = next(
                (
                    u
                    for u, v in self.store.items()
                    if v.get("username") == kwargs["username"]
                ),
                None,
            )
        return AppUser(id=user_id, **self.store.get(user_id)) if user_id else None


auth_manager = AuthManager(
    config=AuthConfig(
        slug="auth_example",
        auth_mode="token",
        login_fields=["username", "email"],
        signup_request=SignupRequest,
        login_request=LoginRequest,
        login_after_signup=False,
    ),
    user_store=User(),
    session_store=MemorySessionStore(),
    strategy=JWTStrategy(secret="opensrc4lyf", algorithm="HS256", use_cookie=False),
    schema=AppUser,
)

auth_route = auth_manager.router


@auth_route.post("/test")
async def test(req: Request):
    return JSONResponse(content={"cookies": req.cookies, "headers": dict(req.headers)})


@auth_route.get("/verify")
async def verify(user: AppUser = Depends(auth_manager.current_user)):
    return user


def init_routers(app_: FastAPI) -> None:
    app_.include_router(auth_route)


def create_app() -> FastAPI:
    app_ = FastAPI(
        middleware=make_middleware(),
        title="Template FastAPI",
        description="Template FastAPI",
        version="V1.0",
    )

    init_routers(app_=app_)
    return app_


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
