from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    include_context: bool = True

class ChatResponse(BaseModel):
    answer: str
    question: str
    has_ai: bool
