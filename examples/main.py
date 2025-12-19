from fastauth.sessions.memory import MemorySessionStore
from pydantic import BaseModel
from fastauth.auth.config import AuthConfig
from fastapi import FastAPI, Response, Request 

from typing import List, Optional

from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from fastauth.auth.manager import AuthManager

origins = ["*"]

def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
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

class User():
    def __init__(self):
        self.store = {}
    async def create(self, data: dict) -> AppUser:
        user_id = "user_id"
        user = AppUser(id=user_id, **data)
        self.store[user_id] = data
        return user
    async def delete(self, user_id: str):
        del self.store[user_id]
    async def get(self, user_id: str) -> AppUser | None:
        return self.store.get(user_id)

class Strategy():
    async def issue(self, response: Response, user_id: str) -> None:
        # Strategies should set headers or cookies
        response.headers["X-Session-Id"] = "session_id"
        response.set_cookie(key="fastauth_token", value="dummy_token")
    async def extract(self, request: Request) -> str | None: 
        pass
    async def revoke(self, response: Response) -> None: 
        pass

auth_manager = AuthManager(
    config=AuthConfig(
        auth_mode="token",
        login_fields=["username", "email"],
    ),
    user_store=User(),
    session_store=MemorySessionStore(),
    strategy=Strategy(),
    schema=AppUser,
)

auth_route = auth_manager.router

@auth_route.post("/test")
async def test(id: str):
    return await auth_manager.session.get(id)

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
