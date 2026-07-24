from __future__ import annotations

import statistics
from collections import defaultdict


def aggregate_participants(recording_rows: list[dict]) -> list[dict]:
    accumulators: dict[str, dict] = {}
    for row in recording_rows:
        qid = row["questionnaire_id"]
        acc = accumulators.setdefault(
            qid,
            {
                "questionnaire_id": qid,
                "recording_count": 0,
                "education_level": row["education_level"],
                "education_group": row["education_group"],
                "valid_eng_spa_tokens": 0,
                "intra_switch_count": 0,
            },
        )
        acc["recording_count"] += 1
        acc["valid_eng_spa_tokens"] += row["valid_eng_spa_tokens"]
        acc["intra_switch_count"] += row["intra_switch_count"]
    output = []
    for row in accumulators.values():
        row["switch_rate_per_1000_valid_tokens"] = (
            row["intra_switch_count"] / row["valid_eng_spa_tokens"] * 1000
            if row["valid_eng_spa_tokens"]
            else 0.0
        )
        output.append(row)
    return sorted(output, key=lambda row: row["questionnaire_id"])


def group_descriptives(participants: list[dict]) -> list[dict]:
    groups: dict[str, list[float]] = defaultdict(list)
    for row in participants:
        groups[row["education_group"]].append(
            row["switch_rate_per_1000_valid_tokens"]
        )
    output = []
    for group, rates in sorted(groups.items()):
        output.append(
            {
                "education_group": group,
                "participant_n": len(rates),
                "mean_rate": statistics.mean(rates),
                "sd_rate": statistics.stdev(rates) if len(rates) > 1 else 0.0,
                "median_rate": statistics.median(rates),
            }
        )
    return output

