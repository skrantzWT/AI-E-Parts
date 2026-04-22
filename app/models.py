from typing import Literal

from pydantic import BaseModel, Field


class LookupRequest(BaseModel):
    user_text: str = Field(..., min_length=1, description="Raw user request text.")


class ParsedRequest(BaseModel):
    lookup_type: Literal["model", "serial", "unknown"]
    model: str | None = None
    serial_number: str | None = None
    requested_part: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class LookupResult(BaseModel):
    status: Literal["stub", "success", "not_found", "error"] = "stub"
    part_number: str | None = None
    description: str | None = None
    source_path: str | None = None
    warnings: list[str] = Field(default_factory=list)
    screenshot_path: str | None = None


class LookupResponse(BaseModel):
    parsed: ParsedRequest
    result: LookupResult

