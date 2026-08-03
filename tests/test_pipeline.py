from __future__ import annotations

import csv
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from bangor_miami.chat import parse_chat_header
from bangor_miami.mapping import CONFIRMED, audit_mapping
from bangor_miami.pipeline import run_pipeline
from bangor_miami.switches import conservative_switches
from bangor_miami.statistics import (
    count_regression_models,
    inferential_analysis,
    ordinary_anova,
    welch_anova,
)
from bangor_miami.tokens import iter_tsv_tokens


class ChatTests(unittest.TestCase):
    def test_parse_chat_header(self):
        rows = parse_chat_header(PROJECT / "data/sample/chats/demo1.cha")
        self.assertEqual([row["chat_speaker_id"] for row in rows], ["ALI", "BOB"])
        self.assertEqual(rows[0]["chat_age_years"], 25)
        self.assertEqual(rows[0]["chat_gender_normalized"], "female")


class MappingTests(unittest.TestCase):
    def test_unique_mapping_is_confirmed(self):
        chat = [{
            "chat_file": "demo1", "chat_speaker_id": "ALI",
            "chat_age_years": 25, "chat_gender_normalized": "female",
        }]
        metadata = [{
            "soundfile": "demo1", "questionnaire_id": "Q1",
            "matching_age_years": 25, "sex_normalized": "female",
            "education_level": 3, "education_group": "Middle (level 3)",
        }]
        result = audit_mapping(chat, metadata)[0]
        self.assertEqual(result["mapping_status"], CONFIRMED)
        self.assertEqual(result["questionnaire_id"], "Q1")

    def test_duplicate_exact_candidates_remain_ambiguous(self):
        chat = [{
            "chat_file": "demo1", "chat_speaker_id": "ALI",
            "chat_age_years": 25, "chat_gender_normalized": "female",
        }]
        candidate = {
            "soundfile": "demo1", "matching_age_years": 25,
            "sex_normalized": "female", "education_level": 3,
            "education_group": "Middle (level 3)",
        }
        metadata = [
            {**candidate, "questionnaire_id": "Q1"},
            {**candidate, "questionnaire_id": "Q2"},
        ]
        result = audit_mapping(chat, metadata)[0]
        self.assertEqual(result["mapping_status"], "ambiguous_multiple_exact_candidates")
        self.assertEqual(result["questionnaire_id"], "")


class TokenAndSwitchTests(unittest.TestCase):
    def test_tsv_footer_is_removed(self):
        rows = list(iter_tsv_tokens(PROJECT / "data/sample/tsvs"))
        self.assertEqual(len(rows), 9)
        self.assertNotIn("(9 rows)", {row["word_id"] for row in rows})

    def test_boundary_and_utterance_rules(self):
        base = {
            "filename": "f", "speaker": "S", "questionnaire_id": "Q",
            "education_level": 3, "education_group": "Middle (level 3)",
        }
        tokens = [
            {**base, "utterance_id": "1", "surface": "hello", "langid": "eng"},
            {**base, "utterance_id": "1", "surface": "hola", "langid": "spa"},
            {**base, "utterance_id": "1", "surface": ".", "langid": "999"},
            {**base, "utterance_id": "1", "surface": "friend", "langid": "eng"},
            {**base, "utterance_id": "2", "surface": "amigo", "langid": "spa"},
        ]
        events, rates = conservative_switches(tokens)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["direction"], "eng_to_spa")
        self.assertEqual(rates[0]["valid_eng_spa_tokens"], 4)
        self.assertEqual(rates[0]["eligible_adjacent_pairs"], 1)
        self.assertEqual(rates[0]["switch_rate_per_1000_eligible_pairs"], 1000.0)

    def test_all_valid_within_utterance_pairs_are_exposure(self):
        base = {
            "filename": "f", "speaker": "S", "questionnaire_id": "Q",
            "education_level": 3, "education_group": "Middle (level 3)",
            "utterance_id": "1",
        }
        tokens = [
            {**base, "surface": surface, "langid": langid}
            for surface, langid in (
                ("one", "eng"), ("two", "eng"),
                ("tres", "spa"), ("four", "eng"),
            )
        ]
        events, rates = conservative_switches(tokens)
        self.assertEqual(len(events), 2)
        self.assertEqual(rates[0]["eligible_adjacent_pairs"], 3)
        self.assertAlmostEqual(
            rates[0]["switch_rate_per_1000_eligible_pairs"], 2000 / 3
        )


class EndToEndTests(unittest.TestCase):
    def test_demo_pipeline(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            summary = run_pipeline(
                PROJECT / "data/sample/chats",
                PROJECT / "data/sample/tsvs",
                PROJECT / "data/sample/sample_metadata.csv",
                output,
            )
            self.assertEqual(summary["confirmed_mappings"], 2)
            self.assertEqual(summary["included_token_rows"], 9)
            self.assertEqual(summary["switch_events"], 3)
            self.assertEqual(summary["independent_participants"], 2)
            self.assertTrue((output / "participant_rates.csv").exists())
            with (output / "participant_rates.csv").open(newline="") as handle:
                participant_rows = list(csv.DictReader(handle))
            self.assertIn("eligible_adjacent_pairs", participant_rows[0])
            saved = json.loads((output / "summary.json").read_text())
            self.assertEqual(saved, summary)


class StatisticalTests(unittest.TestCase):
    def test_anova_functions_return_valid_probabilities(self):
        groups = {
            "Low": [1.0, 2.0, 3.0, 4.0],
            "Middle": [2.0, 3.0, 4.0, 5.0],
            "High": [3.0, 4.0, 5.0, 6.0],
        }
        for result in (ordinary_anova(groups), welch_anova(groups)):
            self.assertGreaterEqual(result["p_value"], 0.0)
            self.assertLessEqual(result["p_value"], 1.0)
            self.assertGreater(result["statistic"], 0.0)

    def test_full_inference_schema(self):
        participants = []
        for level, group in ((1, "Low"), (3, "Middle"), (5, "High")):
            for index, rate in enumerate((2.0, 4.0, 6.0, 8.0)):
                participants.append({
                    "questionnaire_id": f"{group}{index}",
                    "education_level": level,
                    "education_group": group,
                    "switch_rate_per_1000_valid_tokens": rate + level,
                    "switch_rate_per_1000_eligible_pairs": rate + level + 0.5,
                    "eligible_adjacent_pairs": 1000 + 50 * index,
                    "intra_switch_count": round(
                        (1000 + 50 * index) * 0.01 * (1.15 ** level)
                    ),
                })
        result = inferential_analysis(participants)
        self.assertEqual(len(result["tests"]), 6)
        self.assertEqual(result["hc3_regression"]["n"], 12)
        self.assertEqual(len(result["count_regression_models"]), 2)

    def test_count_model_recovers_positive_education_effect(self):
        participants = []
        multipliers = (0.90, 1.00, 1.08, 0.96)
        for level in range(1, 6):
            for index, multiplier in enumerate(multipliers):
                exposure = 800 + 100 * index
                expected = exposure * 0.01 * math.exp(0.20 * level) * multiplier
                participants.append({
                    "questionnaire_id": f"L{level}_{index}",
                    "education_level": level,
                    "eligible_adjacent_pairs": exposure,
                    "intra_switch_count": round(expected),
                })
        models = count_regression_models(participants)
        self.assertEqual([row["model"] for row in models], [
            "Poisson", "NB2 quasi-likelihood (moment alpha)"
        ])
        self.assertAlmostEqual(
            models[0]["education_level_coefficient"], 0.20, delta=0.03
        )
        self.assertGreater(models[0]["education_level_irr"], 1.0)
        self.assertTrue(models[0]["converged"])


if __name__ == "__main__":
    unittest.main()
