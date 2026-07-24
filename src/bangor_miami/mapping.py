from __future__ import annotations

from collections import defaultdict


CONFIRMED = "confirmed_unique_file_age_sex"


def audit_mapping(chat_rows: list[dict], metadata_rows: list[dict]) -> list[dict]:
    """Confirm only unique filename + age + sex matches."""
    by_file: dict[str, list[dict]] = defaultdict(list)
    for row in metadata_rows:
        by_file[row["soundfile"]].append(row)

    output = []
    for chat in chat_rows:
        candidates = by_file.get(chat["chat_file"].lower(), [])
        exact = [
            row
            for row in candidates
            if chat["chat_age_years"] is not None
            and chat["chat_age_years"] == row["matching_age_years"]
            and chat["chat_gender_normalized"]
            and chat["chat_gender_normalized"] == row["sex_normalized"]
        ]
        if len(exact) == 1:
            status, chosen = CONFIRMED, exact[0]
        elif len(exact) > 1:
            status, chosen = "ambiguous_multiple_exact_candidates", None
        elif not candidates:
            status, chosen = "unresolved_no_questionnaire_row_for_file", None
        else:
            status, chosen = "unresolved_no_unique_exact_age_sex_match", None
        output.append(
            {
                **chat,
                "same_file_candidate_count": len(candidates),
                "exact_candidate_count": len(exact),
                "candidate_questionnaire_ids": "|".join(
                    row["questionnaire_id"] for row in (exact or candidates)
                ),
                "mapping_status": status,
                "questionnaire_id": chosen["questionnaire_id"] if chosen else "",
                "education_level": chosen["education_level"] if chosen else "",
                "education_group": chosen["education_group"] if chosen else "",
            }
        )
    return output

