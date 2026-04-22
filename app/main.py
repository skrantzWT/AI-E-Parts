from fastapi import FastAPI

from .automation import lookup_part
from .logging_utils import write_log
from .models import LookupRequest, LookupResponse
from .parser import parse_request

app = FastAPI(title="AI E-Parts", version="0.1.0")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/lookup", response_model=LookupResponse)
def lookup(payload: LookupRequest) -> LookupResponse:
    parsed = parse_request(payload.user_text)
    result = lookup_part(parsed)
    write_log(
        {
            "user_text": payload.user_text,
            "parsed": parsed.model_dump(),
            "result": result.model_dump(),
        }
    )
    return LookupResponse(parsed=parsed, result=result)

