from __future__ import annotations

import re
from pathlib import Path

from .utils import normalize_age, normalize_sex


def parse_chat_header(path: Path) -> list[dict]:
    """Extract speaker metadata from one CHAT header without parsing dialogue."""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    participants: dict[str, dict[str, str]] = {}
    match = re.search(r"^@Participants:\s*(.+)$", text, flags=re.MULTILINE)
    if match:
        for segment in match.group(1).split(","):
            parts = segment.strip().split()
            if not parts:
                continue
            participants[parts[0]] = {
                "speaker_name": " ".join(parts[1:-1]) if len(parts) >= 3 else "",
                "participant_role": parts[-1] if len(parts) >= 2 else "",
            }

    ids: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        if not line.startswith("@ID:"):
            continue
        fields = line.split(":", 1)[1].strip().split("|")
        code = fields[2].strip() if len(fields) > 2 else ""
        ids[code] = {
            "chat_age_raw": fields[3].strip() if len(fields) > 3 else "",
            "chat_gender_raw": fields[4].strip() if len(fields) > 4 else "",
        }

    rows = []
    for code in dict.fromkeys([*participants, *ids]):
        participant = participants.get(code, {})
        identity = ids.get(code, {})
        rows.append(
            {
                "chat_file": path.stem,
                "chat_speaker_id": code,
                "speaker_name": participant.get("speaker_name", ""),
                "participant_role": participant.get("participant_role", ""),
                "chat_age_raw": identity.get("chat_age_raw", ""),
                "chat_age_years": normalize_age(identity.get("chat_age_raw")),
                "chat_gender_raw": identity.get("chat_gender_raw", ""),
                "chat_gender_normalized": normalize_sex(
                    identity.get("chat_gender_raw")
                ),
            }
        )
    return rows


def chat_inventory(directory: Path) -> list[dict]:
    return [
        row
        for path in sorted(directory.glob("*.cha"))
        for row in parse_chat_header(path)
    ]

