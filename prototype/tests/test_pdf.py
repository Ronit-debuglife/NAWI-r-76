import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pdf_generator import build_pdf_report
from r76_calculator import evaluate_full_report, CLASS_III


class TestPDFGeneration(unittest.TestCase):

    def test_generate_pdf_report(self):
        sample_payload = {
            "report_id": "R76-2026-TEST01",
            "certificate_no": "CERT-2026-8889",
            "test_date": "2026-09-07",
            "inspector_name": "R. Sharma (Metrology Eng.)",
            "customer_name": "Apex Food Logistics Ltd",
            "location": "Central Testing Lab - Bay 4",
            "is_in_service": False,
            "use_turning_point": True,
            "instrument": {
                "manufacturer": "Avery Weigh-Tronix",
                "model": "ZK830-15K",
                "serial_no": "AW-2026-99124",
                "accuracy_class": CLASS_III,
                "max_capacity": 15.0,
                "min_capacity": 0.1,
                "e": 0.005,
                "d": 0.005,
                "unit": "kg",
                "tare_max": 5.0,
                "device_type": "Retail Counter NAWI Scale",
            },
            "environment": {
                "temp_c": 21.5,
                "humidity_pct": 48.0,
                "pressure_hpa": 1012.0,
            },
            "standards": {
                "standards_id": "OIML Class M1 Standard Weights Set (1g - 20kg)",
                "standards_cert": "NABL-CAL-2026-00441",
            },
            "zero_test": {
                "indication": 0.0,
                "delta_l": 0.0025,
            },
            "tare_test": {
                "tare_load": 2.0,
                "tare_indication": 2.0,
                "delta_l_tare": 0.0025,
                "net_test_load": 5.0,
                "net_indication": 5.0,
                "delta_l_net": 0.0025,
            },
            "eccentricity_test": {
                "test_load": 5.0,
                "points": [
                    {"position_id": 1, "position_name": "Center (1)", "indication": 5.0, "delta_l": 0.0025},
                    {"position_id": 2, "position_name": "Front-Left (2)", "indication": 5.0, "delta_l": 0.0020},
                    {"position_id": 3, "position_name": "Back-Left (3)", "indication": 5.0, "delta_l": 0.0030},
                    {"position_id": 4, "position_name": "Back-Right (4)", "indication": 5.0, "delta_l": 0.0025},
                    {"position_id": 5, "position_name": "Front-Right (5)", "indication": 5.0, "delta_l": 0.0025},
                ],
            },
            "repeatability_test": {
                "series": [
                    {"load": 7.5, "readings": [7.500, 7.500, 7.505]},
                    {"load": 15.0, "readings": [15.000, 15.005, 15.000]},
                ],
            },
            "weighing_test": {
                "rows": [
                    {"load": 0.1, "i_inc": 0.100, "delta_l_inc": 0.0025, "i_dec": 0.100, "delta_l_dec": 0.0025},
                    {"load": 2.5, "i_inc": 2.500, "delta_l_inc": 0.0025, "i_dec": 2.500, "delta_l_dec": 0.0025},
                    {"load": 5.0, "i_inc": 5.000, "delta_l_inc": 0.0025, "i_dec": 5.000, "delta_l_dec": 0.0025},
                    {"load": 10.0, "i_inc": 10.000, "delta_l_inc": 0.0025, "i_dec": 10.000, "delta_l_dec": 0.0025},
                    {"load": 15.0, "i_inc": 15.000, "delta_l_inc": 0.0025, "i_dec": 15.000, "delta_l_dec": 0.0025},
                ],
            },
        }

        eval_result = evaluate_full_report(sample_payload)
        self.assertEqual(eval_result["overall_status"], "PASS")

        pdf_path = build_pdf_report(sample_payload, eval_result)
        self.assertTrue(os.path.exists(pdf_path))
        file_size = os.path.getsize(pdf_path)
        self.assertGreater(file_size, 5000)  # Verify non-trivial PDF generated


if __name__ == "__main__":
    unittest.main()
