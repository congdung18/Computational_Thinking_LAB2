from pydantic import BaseModel


class SuggestionRequest(BaseModel):
    weather: str
    preferences: str


class SuggestionResponse(BaseModel):
    suggestion: str
