# src/api/models.py
# Cortex — API Request and Response Models
# Defines the shape of data going in and out of the API

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Format(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"


class Tone(str, Enum):
    educational = "educational"
    motivational = "motivational"
    funny = "funny"
    storytelling = "storytelling"
    informative = "informative"


class ScriptRequest(BaseModel):
    """Request body for generating a script."""
    topic: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="The topic or subject of the video",
        example="How to build healthy habits"
    )
    format: Format = Field(
        default=Format.short,
        description="Output format: short (60s), medium (8-10min), long (20-30min)"
    )
    tone: Tone = Field(
        default=Tone.educational,
        description="Tone of the script"
    )
    apply_formatter: bool = Field(
        default=True,
        description="Whether to apply the production formatter to the output"
    )


class ScriptResponse(BaseModel):
    """Response body containing the generated script."""
    success: bool
    topic: str
    format: str
    tone: str
    model_used: str
    formatted: bool
    script: dict
    cortex_version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
