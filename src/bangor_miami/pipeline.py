from __future__ import annotations

import json
from pathlib import Path

from .analysis import aggregate_participants, group_descriptives
from .chat import chat_inventory
from .mapping import CONFIRMED, audit_mapping
from .metadata import read_metadata
from .switches import conservative_switches
from .statistics import inferential_analysis
from .tokens import iter_tsv_tokens
from .utils import write_csv


def run_pipeline(
    chats_dir: Path, tsvs_dir: Path, metadata_path: Path, output_dir: Path
) -> dict:
    chat_rows = chat_inventory(chats_dir)
    metadata_rows = read_metadata(metadata_path)
    mapping_rows = audit_mapping(chat_rows, metadata_rows)
    confirmed = {
        (row["chat_file"], row["chat_speaker_id"]): row
        for row in mapping_rows
        if row["mapping_status"] == CONFIRMED
    }

    included_tokens = []
    for token in iter_tsv_tokens(tsvs_dir):
        mapping = confirmed.get((token["filename"], token["speaker"]))
        if mapping is None:
            continue
        included_tokens.append(
            {
                **token,
                "questionnaire_id": mapping["questionnaire_id"],
                "education_level": mapping["education_level"],
                "education_group": mapping["education_group"],
            }
        )

    events, recordings = conservative_switches(included_tokens)
    participants = aggregate_participants(recordings)
    descriptives = group_descriptives(participants)
    inference = inferential_analysis(participants) if len(participants) >= 6 else None
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "mapping_audit.csv",
        mapping_rows,
        list(mapping_rows[0]),
    )
    write_csv(
        output_dir / "switch_events.csv",
        events,
        list(events[0]) if events else [
            "filename", "speaker", "questionnaire_id", "utterance_id",
            "direction", "previous_surface", "previous_langid",
            "current_surface", "current_langid",
        ],
    )
    write_csv(output_dir / "recording_rates.csv", recordings, list(recordings[0]))
    write_csv(output_dir / "participant_rates.csv", participants, list(participants[0]))
    write_csv(
        output_dir / "group_descriptives.csv",
        descriptives,
        list(descriptives[0]),
    )
    if inference is not None:
        write_csv(
            output_dir / "inferential_tests.csv",
            inference["tests"],
            ["test", "statistic", "df1", "df2", "p_value", "role"],
        )
        regression_rows = [
            {"term": key, "value": value}
            for key, value in inference["hc3_regression"].items()
        ]
        write_csv(
            output_dir / "education_level_regression.csv",
            regression_rows,
            ["term", "value"],
        )
        (output_dir / "statistical_summary.json").write_text(
            json.dumps(inference, indent=2), encoding="utf-8"
        )
    summary = {
        "chat_speaker_file_rows": len(chat_rows),
        "confirmed_mappings": len(confirmed),
        "included_token_rows": len(included_tokens),
        "switch_events": len(events),
        "independent_participants": len(participants),
        "method": "within-utterance adjacent eng↔spa; every other label resets",
        "inferential_analysis_run": inference is not None,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary
