from pydantic import BaseModel


class WelcomeResponse(BaseModel):
    message: str = "Welcome to NebulaPicker"
