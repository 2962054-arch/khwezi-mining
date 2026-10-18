"""Tests for Section G (risk_assessment) and Section H (alerts). Run: python test_sections_g_h.py"""
import unittest
from datetime import date

import risk_assessment as ra
import alerts as al


class TestRisk(unittest.TestCase):
    def test_score(self):
        self.assertEqual(ra.calculate_risk_score(3, 4), 12)
        self.assertEqual(ra.calculate_risk_score(5, 5), 25)
        self.assertEqual(ra.calculate_risk_score(1, 1), 1)

    def test_class_boundaries(self):
        cases = {1: "Low", 4: "Low", 5: "Medium", 9: "Medium",
                 10: "High", 16: "High", 17: "Critical", 25: "Critical"}
        for score, expected in cases.items():
            self.assertEqual(ra.classify_risk(score), expected, score)

    def test_every_matrix_cell(self):
        for row in ra.risk_matrix():
            for l, c, s, cls in row:
                self.assertEqual(s, l * c)
                self.assertEqual(cls, ra.classify_risk(s))

    def test_invalid_inputs(self):
        for bad in [0, 6, -1, "abc", None, 2.5, True, ""]:
            with self.assertRaises(ValueError, msg=repr(bad)):
                ra.calculate_risk_score(bad, 3)
        with self.assertRaises(ValueError):
            ra.classify_risk(0)
        with self.assertRaises(ValueError):
            ra.classify_risk(26)

    def test_string_numbers_accepted(self):
        self.assertEqual(ra.calculate_risk_score("3", "4"), 12)

    def test_warnings(self):
        self.assertIsNone(ra.assess_risk(2, 2)["warning"])
        self.assertIsNone(ra.assess_risk(3, 3)["warning"])
        self.assertIn("HIGH RISK", ra.assess_risk(4, 3)["warning"])
        self.assertIn("CRITICAL RISK", ra.assess_risk(5, 4)["warning"])
        self.assertTrue(ra.assess_risk(5, 5)["is_high_or_critical"])
        self.assertFalse(ra.assess_risk(1, 5)["is_high_or_critical"])

    def test_dataframe(self):
        import pandas as pd
        df = pd.DataFrame({"Likelihood": [1, 5, 9], "Consequence": [1, 5, 2]})
        out = ra.assess_dataframe(df)
        self.assertEqual(list(out["Risk Class"]), ["Low", "Critical", "Invalid"])


class TestEquipmentAlerts(unittest.TestCase):
    def test_temperature(self):
        self.assertIsNone(al.check_temperature("T1", 79.9))
        self.assertEqual(al.check_temperature("T1", 80)["level"], "WARNING")
        self.assertEqual(al.check_temperature("T1", 100)["level"], "WARNING")
        self.assertEqual(al.check_temperature("T1", 100.1)["level"], "CRITICAL")
        self.assertIsNone(al.check_temperature("T1", None))
        self.assertIsNone(al.check_temperature("T1", "bad"))

    def test_vibration(self):
        self.assertIsNone(al.check_vibration("T1", 4.9))
        self.assertEqual(al.check_vibration("T1", 5)["level"], "WARNING")
        self.assertEqual(al.check_vibration("T1", 8)["level"], "WARNING")
        self.assertEqual(al.check_vibration("TRK-012", 9.2)["level"], "CRITICAL")

    def test_figure_1_format(self):
        text = al.format_alert(al.check_vibration("TRK-012", 9.2))
        for piece in ["MINING MONITORING ALERT", "[CRITICAL]", "TRK-012",
                      "Vibration", "9.2 mm/s", "Above Critical Threshold", "Recommended Action"]:
            self.assertIn(piece, text)

    def test_downtime(self):
        self.assertIsNone(al.check_downtime("E", 900, 100))             # 10 %
        self.assertEqual(al.check_downtime("E", 800, 200)["level"], "WARNING")   # 20 %
        self.assertEqual(al.check_downtime("E", 700, 300)["level"], "CRITICAL")  # 30 %
        self.assertIsNone(al.check_downtime("E", 0, 0))                 # no divide by zero
        self.assertIsNone(al.check_downtime("E", -5, 10))

    def test_maintenance(self):
        today = date(2026, 10, 3)
        self.assertEqual(al.check_maintenance("E", "2026-10-01", today)["level"], "CRITICAL")
        self.assertEqual(al.check_maintenance("E", "2026-10-05", today)["level"], "WARNING")
        self.assertEqual(al.check_maintenance("E", "2026-10-10", today)["level"], "WARNING")
        self.assertIsNone(al.check_maintenance("E", "2026-10-11", today))
        self.assertIsNone(al.check_maintenance("E", "not a date", today))
        self.assertIn("Overdue", al.check_maintenance("E", "2026-10-01", today)["type"])


class TestSafetyAlerts(unittest.TestCase):
    def test_ppe(self):
        self.assertIsNone(al.check_ppe("W", 95))
        self.assertIsNone(al.check_ppe("W", 90))
        self.assertEqual(al.check_ppe("W", 89.9)["level"], "WARNING")
        self.assertEqual(al.check_ppe("W", 74)["level"], "CRITICAL")

    def test_fatigue(self):
        self.assertIsNone(al.check_fatigue("W", 5))
        self.assertEqual(al.check_fatigue("W", 6)["level"], "WARNING")
        self.assertEqual(al.check_fatigue("W", 8)["level"], "CRITICAL")

    def test_incident(self):
        self.assertEqual(al.check_incident("I1", "critical")["level"], "CRITICAL")
        self.assertEqual(al.check_incident("I1", "High")["level"], "WARNING")
        self.assertIsNone(al.check_incident("I1", "Low"))
        self.assertIsNone(al.check_incident("I1", None))

    def test_risk_observation_uses_section_g(self):
        for l, c, expected in [(4, 4, "CRITICAL" if False else "WARNING"), (5, 5, "CRITICAL"), (2, 2, None)]:
            cls = ra.assess_risk(l, c)["classification"]
            result = al.check_risk_observation("O1", cls)
            self.assertEqual(result["level"] if result else None, expected)


class TestRunAll(unittest.TestCase):
    def test_generate_and_sort(self):
        eq = [{"Equipment ID": "TRK-001", "Temperature": 70, "Vibration": 3,
               "Operating Hours": 900, "Downtime": 50, "Next Maintenance": "2026-12-01"},
              {"Equipment ID": "TRK-012", "Temperature": 105, "Vibration": 9.2,
               "Operating Hours": 600, "Downtime": 400, "Next Maintenance": "2026-09-01"}]
        wk = [{"Worker ID": "W1", "PPE Compliance": 60, "Fatigue Level": 9, "Risk Class": "High"}]
        inc = [{"Incident ID": "INC-1", "Severity": "Critical"}]
        alerts = al.generate_all_alerts(eq, wk, inc, today=date(2026, 10, 3))
        counts = al.count_by_level(alerts)
        self.assertEqual(alerts[0]["level"], "CRITICAL")           # critical first
        self.assertEqual(counts["total"], len(alerts))
        self.assertTrue(all(a["subject_id"] != "TRK-001" for a in alerts))  # healthy truck: no alerts
        # TRK-012: temp, vibration, downtime, overdue maintenance = 4 critical
        # W1: PPE + fatigue = 2 critical, High risk = 1 warning; INC-1 = 1 critical
        self.assertEqual(counts["critical"], 7)
        self.assertEqual(counts["warning"], 1)

    def test_missing_values_do_not_crash(self):
        self.assertEqual(al.generate_all_alerts([{}], [{}], [{}]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
