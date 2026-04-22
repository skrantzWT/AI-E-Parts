import json
from datetime import datetime
from pathlib import Path
from typing import Any


LOG_DIR = Path("data/logs")


def write_log(record: dict[str, Any]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_path = LOG_DIR / f"{timestamp}.json"
    log_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return log_path

