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
                "eligible_adjacent_pairs": 0,
                "intra_switch_count": 0,
                "eng_to_spa_count": 0,
                "spa_to_eng_count": 0,
            },
        )
        acc["recording_count"] += 1
        acc["valid_eng_spa_tokens"] += row["valid_eng_spa_tokens"]
        acc["eligible_adjacent_pairs"] += row["eligible_adjacent_pairs"]
        acc["intra_switch_count"] += row["intra_switch_count"]
        acc["eng_to_spa_count"] += row["eng_to_spa_count"]
        acc["spa_to_eng_count"] += row["spa_to_eng_count"]
    output = []
    for row in accumulators.values():
        row["switch_rate_per_1000_valid_tokens"] = (
            row["intra_switch_count"] / row["valid_eng_spa_tokens"] * 1000
            if row["valid_eng_spa_tokens"]
            else 0.0
        )
        row["switch_rate_per_1000_eligible_pairs"] = (
            row["intra_switch_count"] / row["eligible_adjacent_pairs"] * 1000
            if row["eligible_adjacent_pairs"]
            else 0.0
        )
        output.append(row)
    return sorted(output, key=lambda row: row["questionnaire_id"])


def group_descriptives(participants: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in participants:
        groups[row["education_group"]].append(row)
    output = []
    for group, rows in sorted(groups.items()):
        token_rates = [row["switch_rate_per_1000_valid_tokens"] for row in rows]
        pair_rates = [row["switch_rate_per_1000_eligible_pairs"] for row in rows]
        output.append(
            {
                "education_group": group,
                "participant_n": len(rows),
                "mean_rate": statistics.mean(token_rates),
                "sd_rate": (
                    statistics.stdev(token_rates) if len(rows) > 1 else 0.0
                ),
                "median_rate": statistics.median(token_rates),
                "mean_rate_per_1000_valid_tokens": statistics.mean(token_rates),
                "sd_rate_per_1000_valid_tokens": (
                    statistics.stdev(token_rates) if len(rows) > 1 else 0.0
                ),
                "median_rate_per_1000_valid_tokens": statistics.median(
                    token_rates
                ),
                "mean_rate_per_1000_eligible_pairs": statistics.mean(pair_rates),
                "sd_rate_per_1000_eligible_pairs": (
                    statistics.stdev(pair_rates) if len(rows) > 1 else 0.0
                ),
                "median_rate_per_1000_eligible_pairs": statistics.median(
                    pair_rates
                ),
            }
        )
    return output

