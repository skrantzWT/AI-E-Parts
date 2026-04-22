import json
from pathlib import Path

from app.parser import parse_request


def main() -> None:
    eval_path = Path("data/eval_cases.json")
    cases = json.loads(eval_path.read_text(encoding="utf-8"))

    for case in cases:
        parsed = parse_request(case["input"])
        print(f"INPUT: {case['input']}")
        print(json.dumps(parsed.model_dump(), indent=2))
        print("-" * 40)


if __name__ == "__main__":
    main()

