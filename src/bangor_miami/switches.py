from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def conservative_switches(tokens: Iterable[dict]) -> tuple[list[dict], list[dict]]:
    """Identify eng/spa transitions without crossing utterances or other labels."""
    previous: dict[tuple[str, str, str], dict | None] = {}
    stats: dict[tuple[str, str, str], dict] = {}
    events = []
    for token in tokens:
        key = (token["filename"], token["speaker"], token["utterance_id"])
        participant = token["questionnaire_id"]
        record_key = (token["filename"], token["speaker"], participant)
        if record_key not in stats:
            stats[record_key] = {
                "filename": token["filename"],
                "speaker": token["speaker"],
                "questionnaire_id": participant,
                "education_level": token["education_level"],
                "education_group": token["education_group"],
                "valid_eng_spa_tokens": 0,
                "eligible_adjacent_pairs": 0,
                "intra_switch_count": 0,
                "eng_to_spa_count": 0,
                "spa_to_eng_count": 0,
            }
        label = token["langid"]
        if label not in {"eng", "spa"}:
            previous[key] = None
            continue
        stats[record_key]["valid_eng_spa_tokens"] += 1
        prior = previous.get(key)
        if prior is not None:
            stats[record_key]["eligible_adjacent_pairs"] += 1
            if prior["langid"] != label:
                direction = f"{prior['langid']}_to_{label}"
                stats[record_key]["intra_switch_count"] += 1
                stats[record_key][f"{direction}_count"] += 1
                events.append(
                    {
                        "filename": token["filename"],
                        "speaker": token["speaker"],
                        "questionnaire_id": participant,
                        "utterance_id": token["utterance_id"],
                        "direction": direction,
                        "previous_surface": prior["surface"],
                        "previous_langid": prior["langid"],
                        "current_surface": token["surface"],
                        "current_langid": label,
                    }
                )
        previous[key] = token

    rows = []
    for row in stats.values():
        row = dict(row)
        denominator = row["valid_eng_spa_tokens"]
        row["switch_rate_per_1000_valid_tokens"] = (
            row["intra_switch_count"] / denominator * 1000 if denominator else 0.0
        )
        pair_denominator = row["eligible_adjacent_pairs"]
        row["switch_rate_per_1000_eligible_pairs"] = (
            row["intra_switch_count"] / pair_denominator * 1000
            if pair_denominator else 0.0
        )
        rows.append(row)
    return events, sorted(rows, key=lambda row: (row["filename"], row["speaker"]))

