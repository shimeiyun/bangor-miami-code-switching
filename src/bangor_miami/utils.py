from __future__ import annotations

import csv
import re
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


def normalize_filename(value: object) -> str:
    text = "" if value is None else str(value).strip().lower()
    return re.sub(r"\.(wav|mp3|cha|tsv)$", "", text)


def normalize_sex(value: object) -> str:
    text = "" if value is None else str(value).strip().lower()
    return {"f": "female", "m": "male"}.get(text, text)


def normalize_age(value: object) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    match = re.match(r"\s*(\d+)", str(value))
    return int(match.group(1)) if match else None


def completed_years(recording: object, dob: object) -> int | None:
    if not isinstance(recording, (date, datetime)) or not isinstance(dob, (date, datetime)):
        return None
    recording = recording.date() if isinstance(recording, datetime) else recording
    dob = dob.date() if isinstance(dob, datetime) else dob
    return recording.year - dob.year - (
        (recording.month, recording.day) < (dob.month, dob.day)
    )


def education_group(level: int | None) -> str:
    if level in (1, 2):
        return "Low (levels 1-2)"
    if level == 3:
        return "Middle (level 3)"
    if level in (4, 5):
        return "High (levels 4-5)"
    return ""


def write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

