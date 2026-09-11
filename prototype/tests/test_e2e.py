import unittest
import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000"

class TestNAWIE2E(unittest.TestCase):

    def test_01_dashboard_and_pages(self):
        # Test main dashboard
        r = requests.get(f"{BASE_URL}/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("NAWI Metrology Suite", r.text)
        self.assertIn("OIML R-76-1:2006", r.text)

        # Test records view
        r_rec = requests.get(f"{BASE_URL}/records")
        self.assertEqual(r_rec.status_code, 200)
        self.assertIn("NAWI Verification Database & History", r_rec.text)

    def test_02_demo_presets(self):
        for preset in ["retail_class3", "lab_balance_class2", "industrial_class3", "failing_scale"]:
            r = requests.get(f"{BASE_URL}/api/demo/{preset}")
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertIn("instrument", data)
            self.assertIn("weighing_test", data)

    def test_03_calculate_api(self):
        # Fetch demo preset
        r_demo = requests.get(f"{BASE_URL}/api/demo/retail_class3")
        payload = r_demo.json()

        # Run real-time calculation
        r_calc = requests.post(f"{BASE_URL}/api/calculate", json=payload)
        self.assertEqual(r_calc.status_code, 200)
        eval_res = r_calc.json()
        self.assertEqual(eval_res["overall_status"], "PASS")
        self.assertTrue(eval_res["zero_test"]["passed"])
        self.assertTrue(eval_res["weighing_test"]["passed"])

    def test_04_create_and_save_report(self):
        r_demo = requests.get(f"{BASE_URL}/api/demo/retail_class3")
        payload = r_demo.json()
        payload["customer_name"] = "Automated E2E Test Client"

        r_save = requests.post(f"{BASE_URL}/api/reports", json=payload)
        self.assertEqual(r_save.status_code, 200)
        res = r_save.json()
        self.assertTrue(res["success"])
        report_id = res["report_id"]
        self.assertTrue(report_id.startswith("R76-"))

        # Check detail web view
        r_view = requests.get(f"{BASE_URL}/report/{report_id}")
        self.assertEqual(r_view.status_code, 200)
        self.assertIn(report_id, r_view.text)
        self.assertIn("Automated E2E Test Client", r_view.text)

        # Check PDF download
        r_pdf = requests.get(f"{BASE_URL}/api/reports/{report_id}/pdf")
        self.assertEqual(r_pdf.status_code, 200)
        self.assertEqual(r_pdf.headers["Content-Type"], "application/pdf")
        self.assertGreater(len(r_pdf.content), 5000)

        # Check listing in reports API
        r_list = requests.get(f"{BASE_URL}/api/reports?q={report_id}")
        self.assertEqual(r_list.status_code, 200)
        items = r_list.json()
        self.assertTrue(any(x["report_id"] == report_id for x in items))

    def test_05_failing_scale_detection(self):
        r_demo = requests.get(f"{BASE_URL}/api/demo/failing_scale")
        payload = r_demo.json()

        r_calc = requests.post(f"{BASE_URL}/api/calculate", json=payload)
        self.assertEqual(r_calc.status_code, 200)
        eval_res = r_calc.json()
        self.assertEqual(eval_res["overall_status"], "FAIL")
        self.assertFalse(eval_res["eccentricity_test"]["passed"])
        self.assertFalse(eval_res["repeatability_test"]["passed"])


if __name__ == "__main__":
    unittest.main()
