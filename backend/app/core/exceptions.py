from fastapi import HTTPException


class AppException(HTTPException):
    def __init__(self, status_code: int = 500, detail: str = "Internal error"):
        super().__init__(status_code=status_code, detail=detail)
