# backend/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., description="User prompt")
    duration_seconds: int = Field(10, ge=3, le=120, description="Desired video length in seconds")
    refine_with_ai: bool = Field(True, description="Use Groq to refine prompt")

class GenerateVideoResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    video_url: Optional[str] = None
