import json
from pathlib import Path
from types import SimpleNamespace

from app.models import ParsedRequest
from app.parser import normalize_parsed_payload, parse_request


def test_normalize_parsed_payload_defaults_unknown() -> None:
    parsed = normalize_parsed_payload({})
    assert parsed == ParsedRequest(lookup_type="unknown")


def test_parse_request_uses_eval_cases(monkeypatch) -> None:
    eval_cases = json.loads(Path("data/eval_cases.json").read_text(encoding="utf-8"))
    response_map = {
        "I need an oil filter for my Workmaster 75": {
            "lookup_type": "model",
            "model": "Workmaster 75",
            "serial_number": None,
            "requested_part": "oil filter",
            "confidence": 0.97,
        },
        "VIN ABC123456, I need an air filter": {
            "lookup_type": "serial",
            "model": None,
            "serial_number": "ABC123456",
            "requested_part": "air filter",
            "confidence": 0.99,
        },
    }

    class FakeResponsesAPI:
        def create(self, *, model, input):
            user_text = input[-1]["content"]
            return SimpleNamespace(output_text=json.dumps(response_map[user_text]))

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponsesAPI()

    monkeypatch.setattr("app.parser.get_client", lambda: FakeClient())

    for case in eval_cases:
        parsed = parse_request(case["input"])
        assert parsed.lookup_type == case["expected_lookup_type"]
        assert parsed.requested_part == case["expected_requested_part"]
