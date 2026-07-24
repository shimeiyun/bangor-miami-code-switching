from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from .utils import normalize_filename


def iter_tsv_tokens(directory: Path) -> Iterator[dict]:
    """Yield token rows by column name and skip '(N rows)' footer records."""
    for path in sorted(directory.glob("*.tsv")):
        with path.open(
            "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                speaker = (row.get("speaker") or "").strip()
                filename = normalize_filename(row.get("filename"))
                if not speaker or not filename:
                    continue
                yield {
                    "source_tsv": path.name,
                    "filename": filename,
                    "speaker": speaker,
                    "word_id": (row.get("word_id") or "").strip(),
                    "utterance_id": (row.get("utterance_id") or "").strip(),
                    "location": (row.get("location") or "").strip(),
                    "surface": (row.get("surface") or "").strip(),
                    "langid": (row.get("langid") or "").strip(),
                    "clause": (row.get("clause") or "").strip(),
                    "clauseno": (row.get("clauseno") or "").strip(),
                }

