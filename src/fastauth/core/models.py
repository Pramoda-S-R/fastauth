from pydantic import BaseModel, ConfigDict


class SignupRequest(BaseModel):
    password: str
    model_config = ConfigDict(extra="allow")


class LoginRequest(BaseModel):
    password: str
    model_config = ConfigDict(extra="allow")
