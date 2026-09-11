import unittest
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from r76_calculator import (
    CLASS_I,
    CLASS_II,
    CLASS_III,
    CLASS_IIII,
    calculate_scale_divisions,
    calculate_min_capacity,
    calculate_mpe,
    calculate_error_turning_point,
    calculate_corrected_error,
    validate_instrument_parameters,
    evaluate_zero_test,
    evaluate_tare_test,
    evaluate_weighing_test,
    evaluate_repeatability_test,
    evaluate_eccentricity_test,
    evaluate_full_report,
)


class TestOIMLR76Calculator(unittest.TestCase):

    def test_scale_divisions_and_min(self):
        # Class III retail scale: Max = 15 kg, e = 5 g (0.005 kg)
        # n = 15 / 0.005 = 3000 divisions (Allowed 100 <= n <= 10000)
        n = calculate_scale_divisions(15.0, 0.005)
        self.assertEqual(n, 3000)

        # Min capacity for Class III: 20 * e = 20 * 0.005 = 0.1 kg (100 g)
        min_cap = calculate_min_capacity(CLASS_III, 0.005)
        self.assertAlmostEqual(min_cap, 0.1, places=4)

        # Validation
        val = validate_instrument_parameters(CLASS_III, 15.0, 0.1, 0.005, 0.005)
        self.assertTrue(val["is_valid"])
        self.assertEqual(len(val["errors"]), 0)

    def test_class_limits_rejection(self):
        # Class III with n = 50 (below min 100)
        val = validate_instrument_parameters(CLASS_III, 0.5, 0.02, 0.01, 0.01)
        self.assertFalse(val["is_valid"])
        self.assertTrue(any("below minimum" in e for e in val["errors"]))

    def test_mpe_calculation_class_iii(self):
        # Class III scale: e = 5 g
        # m <= 500e (0 to 2500g): MPE = +/- 0.5e = 2.5g
        # 500e < m <= 2000e (2500g to 10000g): MPE = +/- 1.0e = 5.0g
        # 2000e < m <= 10000e (10000g to 15000g): MPE = +/- 1.5e = 7.5g
        e = 5.0
        # 1000g is 200e -> MPE 0.5e = 2.5g
        self.assertAlmostEqual(calculate_mpe(1000.0, CLASS_III, e), 2.5)
        # 2500g is 500e -> MPE 0.5e = 2.5g
        self.assertAlmostEqual(calculate_mpe(2500.0, CLASS_III, e), 2.5)
        # 5000g is 1000e -> MPE 1.0e = 5.0g
        self.assertAlmostEqual(calculate_mpe(5000.0, CLASS_III, e), 5.0)
        # 15000g is 3000e -> MPE 1.5e = 7.5g
        self.assertAlmostEqual(calculate_mpe(15000.0, CLASS_III, e), 7.5)

        # In-service verification is 2x MPE
        self.assertAlmostEqual(calculate_mpe(5000.0, CLASS_III, e, is_in_service=True), 10.0)

    def test_turning_point_error_determination(self):
        # Load L = 5000 g, Indication I = 5000 g, e = 5 g
        # Additional weights Delta_L = 2 g (0.4 e) added until reading changes to 5005 g
        # E = I + 0.5e - Delta_L - L = 5000 + 2.5 - 2 - 5000 = +0.5 g
        e = 5.0
        err = calculate_error_turning_point(load=5000.0, indication=5000.0, delta_l=2.0, e=e, use_turning_point=True)
        self.assertAlmostEqual(err, 0.5)

        # Corrected error: if zero error E0 = +0.5 g, Ec = 0.5 - 0.5 = 0.0 g
        ec = calculate_corrected_error(err, zero_error=0.5)
        self.assertAlmostEqual(ec, 0.0)

    def test_zero_test_evaluation(self):
        e = 5.0
        # Zero indication = 0, delta_l = 2.5 g -> E0 = 0 + 2.5 - 2.5 - 0 = 0 (perfect zero)
        res = evaluate_zero_test(zero_indication=0.0, delta_l_zero=2.5, e=e)
        self.assertTrue(res["passed"])
        self.assertAlmostEqual(res["e0"], 0.0)

        # Error > 0.25 e (0.25 * 5 = 1.25)
        # delta_l = 0.5 -> E0 = 0 + 2.5 - 0.5 = 2.0 g > 1.25 -> FAIL
        res_fail = evaluate_zero_test(zero_indication=0.0, delta_l_zero=0.5, e=e)
        self.assertFalse(res_fail["passed"])

    def test_repeatability_evaluation(self):
        e = 5.0
        # Repeatability at 7500g: MPE = 5.0g
        # Readings: 7500, 7502, 7501 -> delta = 2 <= 5.0 -> PASS
        series = [
            {"load": 7500.0, "readings": [7500.0, 7502.0, 7501.0]},
            {"load": 15000.0, "readings": [15000.0, 15003.0, 15002.0]},  # MPE = 7.5g, delta = 3 -> PASS
        ]
        res = evaluate_repeatability_test(series, CLASS_III, e)
        self.assertTrue(res["passed"])
        self.assertEqual(res["status"], "PASS")

        # Repeatability fail: difference > MPE
        series_fail = [
            {"load": 15000.0, "readings": [15000.0, 15010.0, 15000.0]},  # delta = 10 > 7.5g MPE
        ]
        res_fail = evaluate_repeatability_test(series_fail, CLASS_III, e)
        self.assertFalse(res_fail["passed"])

    def test_eccentricity_evaluation(self):
        e = 5.0
        test_load = 5000.0  # Max / 3
        # MPE at 5000g (1000e) is 5.0g
        points = [
            {"position_id": "1", "position_name": "Center", "indication": 5000.0, "delta_l": 2.5},
            {"position_id": "2", "position_name": "Front-Left", "indication": 5002.0, "delta_l": 2.5},
            {"position_id": "3", "position_name": "Back-Left", "indication": 4998.0, "delta_l": 2.5},
            {"position_id": "4", "position_name": "Back-Right", "indication": 5001.0, "delta_l": 2.5},
            {"position_id": "5", "position_name": "Front-Right", "indication": 4999.0, "delta_l": 2.5},
        ]
        res = evaluate_eccentricity_test(test_load, points, CLASS_III, e, zero_error=0.0)
        self.assertTrue(res["passed"])
        self.assertEqual(len(res["points"]), 5)


if __name__ == "__main__":
    unittest.main()
