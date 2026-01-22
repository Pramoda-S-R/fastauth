from fastapi import HTTPException


class SignUpException(HTTPException):
    def __init__(
        self, e: Exception = Exception("There was an unexpected error signing up")
    ):
        super().__init__(
            status_code=500, detail=f"FastAuth | Failed to sign up: {str(e)}"
        )


class LoginException(HTTPException):
    def __init__(
        self, e: Exception = Exception("There was an unexpected error logging in")
    ):
        super().__init__(
            status_code=500, detail=f"FastAuth | Failed to login: {str(e)}"
        )


class LogoutException(HTTPException):
    def __init__(
        self, e: Exception = Exception("There was an unexpected error logging out")
    ):
        super().__init__(
            status_code=500, detail=f"FastAuth | Failed to logout: {str(e)}"
        )


class TokenException(HTTPException):
    def __init__(
        self, e: Exception = Exception("There was an unexpected error with the token")
    ):
        super().__init__(
            status_code=500, detail=f"FastAuth | Failed to issue token: {str(e)}"
        )


class SessionException(HTTPException):
    def __init__(
        self, e: Exception = Exception("There was an unexpected error with the session")
    ):
        super().__init__(
            status_code=500, detail=f"FastAuth | Failed to create session: {str(e)}"
        )


class UserException(HTTPException):
    def __init__(
        self, e: Exception = Exception("There was an unexpected error with the user")
    ):
        super().__init__(
            status_code=500, detail=f"FastAuth | Failed User Operation: {str(e)}"
        )


class CredentialsException(HTTPException):
    def __init__(
        self,
        e: Exception = Exception("There was an unexpected error with the credentials"),
    ):
        super().__init__(
            status_code=500, detail=f"FastAuth | Failed to verify credentials: {str(e)}"
        )
