from fastapi import HTTPException


class MissingLoginFieldsException(HTTPException):
    def __init__(self, e: Exception = Exception("One or more login fields are missing")):
        super().__init__(status_code=400, detail=f"Missing login fields: {str(e)}")

class InvalidPasswordException(HTTPException):
    def __init__(self, e: Exception = Exception("There was an error validating the password")):
        super().__init__(status_code=400, detail=f"Invalid password: {str(e)}")

class UserNotFoundException(HTTPException):
    def __init__(self, e: Exception = Exception("Requested user was not found")):
        super().__init__(status_code=404, detail=f"User not found: {str(e)}")

class FailedToCreateUserException(HTTPException):
    def __init__(self, e: Exception = Exception("Could not create user")):
        super().__init__(status_code=500, detail=f"Failed to create user: {str(e)}")

class FailedToCreateSessionException(HTTPException):
    def __init__(self, e: Exception = Exception("Could not create session")):
        super().__init__(status_code=500, detail=f"Failed to create session: {str(e)}")

class FailedToIssueTokenException(HTTPException):
    def __init__(self, e: Exception = Exception("Could not issue token")):
        super().__init__(status_code=500, detail=f"Failed to issue token: {str(e)}")

class FailedToSignUpException(HTTPException):
    def __init__(self, e: Exception = Exception("There was an unexpected error signing up")):
        super().__init__(status_code=500, detail=f"Failed to sign up: {str(e)}")