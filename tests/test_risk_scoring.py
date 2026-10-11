import unittest
from datetime import datetime, timezone

from Agent1.event_analyzer import get_severity
from Agent1.risk_analyzer import analyze_articles
from Agent2.main import calculate_scenario


class RiskScoringTests(unittest.TestCase):
    def test_severity_bands(self):
        expected = {
            0: "NO SIGNAL",
            1: "LOW",
            49: "LOW",
            50: "MEDIUM",
            64: "MEDIUM",
            65: "HIGH",
            79: "HIGH",
            80: "CRITICAL",
            100: "CRITICAL",
        }

        for score, level in expected.items():
            with self.subTest(score=score):
                self.assertEqual(get_severity(score), level)

    def test_agent2_uses_same_severity_bands_and_marks_assumptions(self):
        for score, level in (
            (0, "NO SIGNAL"),
            (49, "LOW"),
            (50, "MEDIUM"),
            (65, "HIGH"),
            (80, "CRITICAL"),
        ):
            with self.subTest(score=score):
                scenario = calculate_scenario(
                    {
                        "overall_risk": {"score": score},
                        "compound_risk": {"detected": False},
                        "corridors": {},
                    }
                )
                self.assertEqual(scenario["risk_level"], level)
                self.assertEqual(scenario["disruption_severity"], level)
                self.assertTrue(scenario["estimates_are_heuristic"])
                self.assertEqual(
                    scenario["model_assumptions"]["required_volume_unit"],
                    "barrels/day",
                )

    def test_scenario_maps_known_corridor_aliases_to_refineries(self):
        scenario = calculate_scenario(
            {
                "overall_risk": {"score": 85},
                "compound_risk": {"detected": False},
                "corridors": {
                    "Gulf of Oman": {"risk_score": 90},
                    "Middle East": {"risk_score": 85},
                },
            }
        )

        self.assertEqual(scenario["affected_route"], "Gulf of Oman")
        self.assertEqual(
            scenario["affected_refineries"],
            ["Jamnagar Refinery", "Vadinar Refinery"],
        )

    def test_ai_severity_is_capped_by_reported_energy_impact(self):
        published_at = datetime.now(timezone.utc).isoformat()
        article = {
            "source": "BBC",
            "title": "A reported regional event",
            "summary": "No further details.",
            "published_at": published_at,
            "ai_event": {
                "event_type": "geopolitical_tension",
                "severity": "CRITICAL",
                "supply_impact": "LOW",
                "transport_impact": "NONE",
                "price_impact": "NONE",
                "affected_corridors": [],
            },
        }

        result = analyze_articles([article])

        self.assertLessEqual(
            result["events"][0]["severity_score"],
            30,
        )
        self.assertEqual(result["events"][0]["severity"], "LOW")

    def test_irrelevant_ai_event_does_not_raise_energy_risk(self):
        article = {
            "source": "BBC",
            "title": "A general political story",
            "summary": "No energy impact is described.",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "ai_event": {
                "event_type": "general_signal",
                "severity": "CRITICAL",
                "supply_impact": "NONE",
                "transport_impact": "NONE",
                "price_impact": "NONE",
                "affected_corridors": [],
            },
        }

        result = analyze_articles([article])

        self.assertLessEqual(
            result["events"][0]["severity_score"],
            10,
        )
        self.assertEqual(result["overall_risk"]["score"], 6)

    def test_scenario_rejects_invalid_risk_score(self):
        for invalid_score in (-1, 101, float("nan"), float("inf"), True):
            with self.subTest(score=invalid_score):
                with self.assertRaises(ValueError):
                    calculate_scenario(
                        {
                            "overall_risk": {"score": invalid_score},
                            "compound_risk": {"detected": False},
                            "corridors": {},
                        }
                    )


if __name__ == "__main__":
    unittest.main()
