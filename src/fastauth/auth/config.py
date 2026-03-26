# auth/config.py
from enum import Enum
from typing import Annotated, Callable, Type

from pydantic import (BaseModel, StringConstraints, create_model,
                      model_validator)

from .models import LoginRequest, SignupRequest

LowerSnakeStr = Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]+$")]
LoginFieldStr = Annotated[str, StringConstraints(min_length=1)]


class AuthConfig(BaseModel):
    slug: LowerSnakeStr
    session_ttl_seconds: int = 3600
    secure_cookies: bool = True
    login_fields: list[str] = ["email"]
    login_after_signup: bool = True
    password_validator: Callable[[str], bool] = lambda x: True
    roles: type[Enum] | None = None

    signup_request: Type[BaseModel] | None = None
    login_request: Type[BaseModel] | None = None

    # -------------------------
    # SIGNUP REQUEST
    # -------------------------
    @model_validator(mode="after")
    def handle_signup_request(self):
        if self.signup_request is None:
            self.signup_request = self._build_model(
                base=SignupRequest,
                name=f"{self.slug.title()}SignupRequest",
            )
        else:
            self._validate_model(self.signup_request, is_signup=True)

        return self

    # -------------------------
    # LOGIN REQUEST
    # -------------------------
    @model_validator(mode="after")
    def handle_login_request(self):
        if self.login_request is None:
            self.login_request = self._build_model(
                base=LoginRequest,
                name=f"{self.slug.title()}LoginRequest",
            )
        else:
            self._validate_model(self.login_request, is_signup=False)

        return self

    # -------------------------
    # BUILD MODEL
    # -------------------------
    def _build_model(self, base: Type[BaseModel], name: str) -> Type[BaseModel]:
        base_fields = base.model_fields

        fields = {
            field: (LoginFieldStr, ...)
            for field in self.login_fields
            if field not in base_fields
        }

        return create_model(
            name,
            __base__=base,
            **fields,
        )

    # -------------------------
    # VALIDATE USER MODEL
    # -------------------------
    def _validate_model(self, model: Type[BaseModel], is_signup: bool):
        if not issubclass(model, BaseModel):
            raise TypeError("Request model must be a Pydantic BaseModel")

        model_fields = model.model_fields

        # --- password required ---
        if "password" not in model_fields:
            raise ValueError("Model must include 'password' field")

        # --- at least one login field ---
        available = set(self.login_fields) & model_fields.keys()
        if not available:
            raise ValueError(
                f"Model must include at least one of the login fields: {self.login_fields}"
            )

        # --- optional: enforce type safety ---
        for field in available:
            field_info = model_fields[field]
            if field_info.annotation is not str:
                raise TypeError(f"Field '{field}' must be of type str")

        # --- optional: stricter signup rules ---
        if is_signup:
            # e.g. enforce password confirmation if needed
            pass
