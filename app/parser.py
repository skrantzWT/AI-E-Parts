import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from .models import ParsedRequest
from .prompts import PARSER_SYSTEM_PROMPT

load_dotenv()


def get_client() -> OpenAI:
    return OpenAI()


def get_parser_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5")


def normalize_parsed_payload(payload: dict[str, Any]) -> ParsedRequest:
    return ParsedRequest(
        lookup_type=payload.get("lookup_type", "unknown"),
        model=payload.get("model"),
        serial_number=payload.get("serial_number"),
        requested_part=payload.get("requested_part"),
        confidence=payload.get("confidence", 0.0) or 0.0,
    )


def parse_request(user_text: str) -> ParsedRequest:
    client = get_client()
    response = client.responses.create(
        model=get_parser_model(),
        input=[
            {"role": "developer", "content": PARSER_SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
    )

    payload = json.loads(response.output_text)
    return normalize_parsed_payload(payload)
