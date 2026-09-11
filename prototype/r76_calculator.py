"""
OIML R-76 Metrological Calculation Engine
Conforms strictly to OIML R-76-1 (Edition 2006 (E)):
- Non-automatic weighing instruments - Metrological and technical requirements - Tests
- Clause 3.2: Accuracy classes
- Clause 3.3: Verification scale interval (e) and actual scale interval (d)
- Clause 3.4: Minimum capacity (Min)
- Clause 3.5: Maximum permissible errors (MPE)
- Clause A.4.2: Zero-setting test (A.4.2.3: Accuracy of zero-setting)
- Clause A.4.4: Weighing test (A.4.4.3: Error calculation with small weights)
- Clause A.4.6: Tare test
- Clause A.4.7: Eccentricity test
- Clause A.4.10: Repeatability test
"""

from typing import Dict, List, Any, Optional, Tuple
import math

# Accuracy class identifiers conforming to OIML R-76
CLASS_I = "I"      # Special Accuracy
CLASS_II = "II"    # High Accuracy
CLASS_III = "III"  # Medium Accuracy
CLASS_IIII = "IIII"  # Ordinary Accuracy

ACCURACY_CLASSES = [CLASS_I, CLASS_II, CLASS_III, CLASS_IIII]

CLASS_NAMES = {
    CLASS_I: "Class I (Special Accuracy)",
    CLASS_II: "Class II (High Accuracy)",
    CLASS_III: "Class III (Medium Accuracy)",
    CLASS_IIII: "Class IIII (Ordinary Accuracy)",
}


def get_class_requirements(accuracy_class: str) -> Dict[str, Any]:
    """
    Returns the OIML R-76 Table 3 requirements for the given accuracy class.
    """
    reqs = {
        CLASS_I: {
            "name": CLASS_NAMES[CLASS_I],
            "min_e_g": 0.001,
            "min_n": 50000,
            "max_n": None,
            "min_capacity_factor": 100,  # Min = 100 * e
            "mpe_steps": [
                {"max_e": 50000, "mpe_e": 0.5},
                {"max_e": 200000, "mpe_e": 1.0},
                {"max_e": float("inf"), "mpe_e": 1.5},
            ],
        },
        CLASS_II: {
            "name": CLASS_NAMES[CLASS_II],
            "min_e_g": 0.001,
            "min_n": 100,
            "max_n": 100000,
            "min_capacity_factor": 20,  # 20 * e for 0.001 <= e <= 0.05, 50 * e for e >= 0.1
            "mpe_steps": [
                {"max_e": 5000, "mpe_e": 0.5},
                {"max_e": 20000, "mpe_e": 1.0},
                {"max_e": 100000, "mpe_e": 1.5},
            ],
        },
        CLASS_III: {
            "name": CLASS_NAMES[CLASS_III],
            "min_e_g": 0.1,
            "min_n": 100,
            "max_n": 10000,
            "min_capacity_factor": 20,  # Min = 20 * e
            "mpe_steps": [
                {"max_e": 500, "mpe_e": 0.5},
                {"max_e": 2000, "mpe_e": 1.0},
                {"max_e": 10000, "mpe_e": 1.5},
            ],
        },
        CLASS_IIII: {
            "name": CLASS_NAMES[CLASS_IIII],
            "min_e_g": 5.0,
            "min_n": 100,
            "max_n": 1000,
            "min_capacity_factor": 10,  # Min = 10 * e
            "mpe_steps": [
                {"max_e": 50, "mpe_e": 0.5},
                {"max_e": 200, "mpe_e": 1.0},
                {"max_e": 1000, "mpe_e": 1.5},
            ],
        },
    }
    return reqs.get(accuracy_class, reqs[CLASS_III])


def calculate_scale_divisions(max_capacity: float, e: float) -> int:
    """
    Computes number of verification scale intervals: n = Max / e
    Per OIML R-76 clause 3.2.
    """
    if e <= 0:
        return 0
    return int(round(max_capacity / e))


def calculate_min_capacity(accuracy_class: str, e: float) -> float:
    """
    Calculates mandatory Minimum Capacity (Min) per OIML R-76 Table 3.
    """
    if accuracy_class == CLASS_I:
        return 100.0 * e
    elif accuracy_class == CLASS_II:
        if e < 0.1:
            return 20.0 * e
        return 50.0 * e
    elif accuracy_class == CLASS_III:
        return 20.0 * e
    elif accuracy_class == CLASS_IIII:
        return 10.0 * e
    return 20.0 * e


def validate_instrument_parameters(
    accuracy_class: str,
    max_capacity: float,
    min_capacity: float,
    e: float,
    d: float,
) -> Dict[str, Any]:
    """
    Validates metrological parameters against OIML R-76 Table 3 rules:
    - n = Max / e within allowable range [min_n, max_n]
    - d <= e
    - min_capacity >= required Min per Table 3
    """
    warnings = []
    errors = []

    if max_capacity <= 0:
        errors.append("Maximum capacity (Max) must be greater than 0.")
    if e <= 0:
        errors.append("Verification scale interval (e) must be greater than 0.")
    if d <= 0:
        errors.append("Actual scale interval (d) must be greater than 0.")
    if d > e:
        warnings.append(f"Actual scale interval d ({d}) is greater than verification interval e ({e}). Generally d <= e per R-76.")

    if errors:
        return {
            "is_valid": False,
            "errors": errors,
            "warnings": warnings,
            "n": 0,
            "required_min": 0,
        }

    n = calculate_scale_divisions(max_capacity, e)
    reqs = get_class_requirements(accuracy_class)
    required_min = calculate_min_capacity(accuracy_class, e)

    # Check scale divisions n
    if n < reqs["min_n"]:
        errors.append(
            f"Number of verification scale intervals n = {n} is below minimum allowed ({reqs['min_n']}) for {CLASS_NAMES.get(accuracy_class, accuracy_class)}."
        )
    if reqs["max_n"] is not None and n > reqs["max_n"]:
        errors.append(
            f"Number of verification scale intervals n = {n} exceeds maximum allowed ({reqs['max_n']}) for {CLASS_NAMES.get(accuracy_class, accuracy_class)}."
        )

    # Check minimum capacity
    if min_capacity < (required_min - 1e-9):
        warnings.append(
            f"Stated Min capacity ({min_capacity}) is less than the standard OIML R-76 minimum capacity ({required_min}) for e = {e}."
        )

    return {
        "is_valid": len(errors) == 0,
        "n": n,
        "required_min": required_min,
        "errors": errors,
        "warnings": warnings,
    }


def calculate_mpe(load: float, accuracy_class: str, e: float, is_in_service: bool = False) -> float:
    """
    Calculates Maximum Permissible Error (MPE) for a given load m.
    OIML R-76 Table 6 (Initial Verification) and Table 4 (In-Service).
    For in-service verification, MPE is twice that of initial verification.
    Returns MPE expressed in the same units as 'e'.
    """
    if e <= 0 or load < 0:
        return 0.0

    # Number of verification intervals for this load: m / e
    m_in_e = load / e

    reqs = get_class_requirements(accuracy_class)
    mpe_factor = 0.5

    for step in reqs["mpe_steps"]:
        if m_in_e <= step["max_e"]:
            mpe_factor = step["mpe_e"]
            break

    mpe = mpe_factor * e

    if is_in_service:
        mpe *= 2.0

    return round(mpe, 8)


def calculate_error_turning_point(
    load: float,
    indication: float,
    delta_l: Optional[float],
    e: float,
    use_turning_point: bool = True,
) -> float:
    """
    Determines error per OIML R-76 clause A.4.4.3:
    Turning point method (small weights method):
      E = I + 0.5e - Delta_L - L
    Direct indication method (when small weights not used):
      E = I - L
    """
    if use_turning_point and delta_l is not None:
        return indication + (0.5 * e) - delta_l - load
    return indication - load


def calculate_corrected_error(error: float, zero_error: float) -> float:
    """
    Corrected error Ec = E - E0 per OIML R-76 clause A.4.4.3.
    """
    return error - zero_error


def evaluate_zero_test(
    zero_indication: float,
    delta_l_zero: Optional[float],
    e: float,
    use_turning_point: bool = True,
) -> Dict[str, Any]:
    """
    Evaluates Zero-Setting Accuracy per OIML R-76 clause A.4.2.3:
    After setting to zero, the effect of zero deviation on the result of weighing
    shall not exceed 0.25 e.
    MPE for zero-setting: +/- 0.25 e.
    """
    e0 = calculate_error_turning_point(
        load=0.0,
        indication=zero_indication,
        delta_l=delta_l_zero,
        e=e,
        use_turning_point=use_turning_point,
    )
    max_allowed_zero_error = 0.25 * e
    passed = abs(e0) <= (max_allowed_zero_error + 1e-7)

    return {
        "zero_indication": zero_indication,
        "delta_l_zero": delta_l_zero,
        "e0": round(e0, 6),
        "max_allowed_error": round(max_allowed_zero_error, 6),
        "passed": passed,
        "status": "PASS" if passed else "FAIL",
        "notes": f"Zero setting error E0 = {round(e0, 4)} (Limit: +/- {round(max_allowed_zero_error, 4)} e)",
    }


def evaluate_tare_test(
    tare_load: float,
    tare_indication: float,
    delta_l_tare: Optional[float],
    net_test_load: float,
    net_indication: float,
    delta_l_net: Optional[float],
    accuracy_class: str,
    e: float,
    is_in_service: bool = False,
    use_turning_point: bool = True,
) -> Dict[str, Any]:
    """
    Evaluates Tare Balancing / Tare Weighing Test per OIML R-76 clause A.4.6:
    - Tare balancing accuracy (E_tare)
    - Net load error (E_net) compared against MPE for that net load.
    """
    e_tare = calculate_error_turning_point(
        load=tare_load,
        indication=tare_indication,
        delta_l=delta_l_tare,
        e=e,
        use_turning_point=use_turning_point,
    )
    tare_zero_passed = abs(e_tare) <= (0.25 * e + 1e-7)

    # Net weighing error
    e_net_raw = calculate_error_turning_point(
        load=net_test_load,
        indication=net_indication,
        delta_l=delta_l_net,
        e=e,
        use_turning_point=use_turning_point,
    )
    # Net corrected error using tare error as reference
    e_net_corr = calculate_corrected_error(e_net_raw, e_tare)
    mpe_net = calculate_mpe(net_test_load, accuracy_class, e, is_in_service)
    net_passed = abs(e_net_corr) <= (mpe_net + 1e-7)

    overall_passed = tare_zero_passed and net_passed

    return {
        "tare_load": tare_load,
        "tare_indication": tare_indication,
        "delta_l_tare": delta_l_tare,
        "e_tare": round(e_tare, 6),
        "tare_zero_passed": tare_zero_passed,
        "net_test_load": net_test_load,
        "net_indication": net_indication,
        "delta_l_net": delta_l_net,
        "e_net_raw": round(e_net_raw, 6),
        "e_net_corr": round(e_net_corr, 6),
        "mpe_net": round(mpe_net, 6),
        "net_passed": net_passed,
        "passed": overall_passed,
        "status": "PASS" if overall_passed else "FAIL",
    }


def evaluate_repeatability_test(
    series: List[Dict[str, Any]],
    accuracy_class: str,
    e: float,
    is_in_service: bool = False,
) -> Dict[str, Any]:
    """
    Evaluates Repeatability Test per OIML R-76 clause A.4.10:
    Two series of weighings shall be performed: one at ~0.5 Max and one at ~Max.
    Each series should have at least 3 weighings (typically 3 to 10).
    Condition: The maximum difference between indications for the same load
               shall not exceed the absolute value of the MPE for that load.
               Delta = I_max - I_min <= |MPE|
    """
    evaluated_series = []
    all_passed = True

    for item in series:
        load = float(item.get("load", 0.0))
        readings = [float(r) for r in item.get("readings", []) if r is not None and str(r).strip() != ""]
        
        if len(readings) < 3:
            evaluated_series.append({
                "load": load,
                "readings": readings,
                "count": len(readings),
                "i_max": 0.0,
                "i_min": 0.0,
                "delta": 0.0,
                "mpe": 0.0,
                "passed": False,
                "status": "INCOMPLETE (Need >= 3 weighings)",
            })
            all_passed = False
            continue

        i_max = max(readings)
        i_min = min(readings)
        delta = round(i_max - i_min, 6)
        mpe = calculate_mpe(load, accuracy_class, e, is_in_service)
        passed = delta <= (mpe + 1e-7)

        if not passed:
            all_passed = False

        evaluated_series.append({
            "load": load,
            "readings": readings,
            "count": len(readings),
            "i_max": round(i_max, 6),
            "i_min": round(i_min, 6),
            "delta": delta,
            "mpe": round(mpe, 6),
            "passed": passed,
            "status": "PASS" if passed else "FAIL",
        })

    return {
        "series": evaluated_series,
        "passed": all_passed and len(evaluated_series) > 0,
        "status": "PASS" if (all_passed and len(evaluated_series) > 0) else "FAIL",
    }


def evaluate_eccentricity_test(
    test_load: float,
    points: List[Dict[str, Any]],
    accuracy_class: str,
    e: float,
    zero_error: float = 0.0,
    is_in_service: bool = False,
    use_turning_point: bool = True,
) -> Dict[str, Any]:
    """
    Evaluates Eccentricity Test per OIML R-76 clause A.4.7:
    Load: Typically 1/3 Max (or 1/4 Max for 4 supports).
    Applied at 5 positions:
      1: Center
      2: Front-Left (or Position 2)
      3: Back-Left (or Position 3)
      4: Back-Right (or Position 4)
      5: Front-Right (or Position 5)
    Condition: Corrected error Ec at each position shall not exceed MPE for the test load.
    """
    mpe = calculate_mpe(test_load, accuracy_class, e, is_in_service)
    evaluated_points = []
    all_passed = True
    errors_list = []

    for pt in points:
        position_id = pt.get("position_id", "Unknown")
        position_name = pt.get("position_name", f"Position {position_id}")
        indication = float(pt.get("indication", 0.0))
        delta_l = float(pt.get("delta_l")) if pt.get("delta_l") is not None and str(pt.get("delta_l")).strip() != "" else None

        raw_error = calculate_error_turning_point(
            load=test_load,
            indication=indication,
            delta_l=delta_l,
            e=e,
            use_turning_point=use_turning_point,
        )
        corrected_error = calculate_corrected_error(raw_error, zero_error)
        passed = abs(corrected_error) <= (mpe + 1e-7)

        if not passed:
            all_passed = False

        errors_list.append(corrected_error)
        evaluated_points.append({
            "position_id": position_id,
            "position_name": position_name,
            "indication": round(indication, 6),
            "delta_l": delta_l,
            "raw_error": round(raw_error, 6),
            "corrected_error": round(corrected_error, 6),
            "mpe": round(mpe, 6),
            "passed": passed,
            "status": "PASS" if passed else "FAIL",
        })

    max_diff = round(max(errors_list) - min(errors_list), 6) if errors_list else 0.0

    return {
        "test_load": test_load,
        "mpe": round(mpe, 6),
        "zero_error_applied": round(zero_error, 6),
        "points": evaluated_points,
        "max_error_diff": max_diff,
        "passed": all_passed and len(evaluated_points) > 0,
        "status": "PASS" if (all_passed and len(evaluated_points) > 0) else "FAIL",
    }


def evaluate_weighing_test(
    rows: List[Dict[str, Any]],
    accuracy_class: str,
    e: float,
    zero_error: float = 0.0,
    is_in_service: bool = False,
    use_turning_point: bool = True,
) -> Dict[str, Any]:
    """
    Evaluates Weighing Test (Increasing & Decreasing loads) per OIML R-76 clause A.4.4:
    At least 5 different load levels distributed across range.
    For each load:
      - Increasing indication I_inc, Delta_L_inc -> E_inc, Ec_inc
      - Decreasing indication I_dec, Delta_L_dec -> E_dec, Ec_dec
      - Hysteresis = |Ec_dec - Ec_inc|
      - Comparison of |Ec| <= MPE
    """
    evaluated_rows = []
    all_passed = True
    max_hysteresis = 0.0

    for r in rows:
        load = float(r.get("load", 0.0))
        mpe = calculate_mpe(load, accuracy_class, e, is_in_service)

        # Increasing
        i_inc = float(r.get("i_inc", 0.0))
        delta_l_inc = float(r.get("delta_l_inc")) if r.get("delta_l_inc") is not None and str(r.get("delta_l_inc")).strip() != "" else None
        e_inc_raw = calculate_error_turning_point(load, i_inc, delta_l_inc, e, use_turning_point)
        e_inc_corr = calculate_corrected_error(e_inc_raw, zero_error)
        passed_inc = abs(e_inc_corr) <= (mpe + 1e-7)

        # Decreasing (optional if not recorded or load is 0)
        has_dec = r.get("i_dec") is not None and str(r.get("i_dec")).strip() != ""
        i_dec = float(r.get("i_dec")) if has_dec else None
        delta_l_dec = float(r.get("delta_l_dec")) if r.get("delta_l_dec") is not None and str(r.get("delta_l_dec")).strip() != "" else None

        if has_dec and i_dec is not None:
            e_dec_raw = calculate_error_turning_point(load, i_dec, delta_l_dec, e, use_turning_point)
            e_dec_corr = calculate_corrected_error(e_dec_raw, zero_error)
            passed_dec = abs(e_dec_corr) <= (mpe + 1e-7)
            hysteresis = round(abs(e_dec_corr - e_inc_corr), 6)
            if hysteresis > max_hysteresis:
                max_hysteresis = hysteresis
        else:
            e_dec_raw = None
            e_dec_corr = None
            passed_dec = True
            hysteresis = None

        row_passed = passed_inc and passed_dec
        if not row_passed:
            all_passed = False

        evaluated_rows.append({
            "load": load,
            "mpe": round(mpe, 6),
            "i_inc": round(i_inc, 6),
            "delta_l_inc": delta_l_inc,
            "e_inc_raw": round(e_inc_raw, 6),
            "e_inc_corr": round(e_inc_corr, 6),
            "passed_inc": passed_inc,
            "i_dec": round(i_dec, 6) if i_dec is not None else None,
            "delta_l_dec": delta_l_dec,
            "e_dec_raw": round(e_dec_raw, 6) if e_dec_raw is not None else None,
            "e_dec_corr": round(e_dec_corr, 6) if e_dec_corr is not None else None,
            "passed_dec": passed_dec,
            "hysteresis": hysteresis,
            "passed": row_passed,
            "status": "PASS" if row_passed else "FAIL",
        })

    return {
        "rows": evaluated_rows,
        "max_hysteresis": round(max_hysteresis, 6),
        "zero_error_applied": round(zero_error, 6),
        "passed": all_passed and len(evaluated_rows) >= 5,
        "row_count": len(evaluated_rows),
        "status": "PASS" if (all_passed and len(evaluated_rows) >= 5) else ("FAIL" if not all_passed else "INCOMPLETE (< 5 points)"),
    }


def evaluate_full_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregates full metrological evaluation across all OIML R-76 tests:
    - Instrument parameter validation (Table 3)
    - Zero setting test (A.4.2)
    - Weighing test (A.4.4)
    - Tare test (A.4.6)
    - Eccentricity test (A.4.7)
    - Repeatability test (A.4.10)
    Returns complete structured metrological evaluation result.
    """
    instrument = report_data.get("instrument", {})
    accuracy_class = instrument.get("accuracy_class", CLASS_III)
    max_cap = float(instrument.get("max_capacity", 0.0))
    min_cap = float(instrument.get("min_capacity", 0.0))
    e = float(instrument.get("e", 0.0))
    d = float(instrument.get("d", e))
    is_in_service = bool(report_data.get("is_in_service", False))
    use_turning_point = bool(report_data.get("use_turning_point", True))

    # 1. Metrological validation
    param_eval = validate_instrument_parameters(accuracy_class, max_cap, min_cap, e, d)

    # 2. Zero test
    zero_data = report_data.get("zero_test", {})
    zero_eval = evaluate_zero_test(
        zero_indication=float(zero_data.get("indication", 0.0)),
        delta_l_zero=float(zero_data.get("delta_l")) if zero_data.get("delta_l") is not None and str(zero_data.get("delta_l")).strip() != "" else None,
        e=e,
        use_turning_point=use_turning_point,
    )
    zero_error = zero_eval["e0"]

    # 3. Tare test
    tare_data = report_data.get("tare_test", {})
    tare_eval = evaluate_tare_test(
        tare_load=float(tare_data.get("tare_load", 0.0)),
        tare_indication=float(tare_data.get("tare_indication", 0.0)),
        delta_l_tare=float(tare_data.get("delta_l_tare")) if tare_data.get("delta_l_tare") is not None and str(tare_data.get("delta_l_tare")).strip() != "" else None,
        net_test_load=float(tare_data.get("net_test_load", 0.0)),
        net_indication=float(tare_data.get("net_indication", 0.0)),
        delta_l_net=float(tare_data.get("delta_l_net")) if tare_data.get("delta_l_net") is not None and str(tare_data.get("delta_l_net")).strip() != "" else None,
        accuracy_class=accuracy_class,
        e=e,
        is_in_service=is_in_service,
        use_turning_point=use_turning_point,
    )

    # 4. Weighing test
    weighing_data = report_data.get("weighing_test", {}).get("rows", [])
    weighing_eval = evaluate_weighing_test(
        rows=weighing_data,
        accuracy_class=accuracy_class,
        e=e,
        zero_error=zero_error,
        is_in_service=is_in_service,
        use_turning_point=use_turning_point,
    )

    # 5. Repeatability test
    repeatability_series = report_data.get("repeatability_test", {}).get("series", [])
    repeatability_eval = evaluate_repeatability_test(
        series=repeatability_series,
        accuracy_class=accuracy_class,
        e=e,
        is_in_service=is_in_service,
    )

    # 6. Eccentricity test
    eccentricity_data = report_data.get("eccentricity_test", {})
    eccentricity_eval = evaluate_eccentricity_test(
        test_load=float(eccentricity_data.get("test_load", 0.0)),
        points=eccentricity_data.get("points", []),
        accuracy_class=accuracy_class,
        e=e,
        zero_error=zero_error,
        is_in_service=is_in_service,
        use_turning_point=use_turning_point,
    )

    # Overall verdict
    subtests_pass = (
        zero_eval["passed"]
        and tare_eval["passed"]
        and weighing_eval["passed"]
        and repeatability_eval["passed"]
        and eccentricity_eval["passed"]
    )
    overall_pass = param_eval["is_valid"] and subtests_pass

    summary_cards = [
        {"test": "Instrument Metrological Limits (Table 3)", "status": "PASS" if param_eval["is_valid"] else "FAIL", "mandatory": True},
        {"test": "Zero Setting Accuracy (A.4.2)", "status": zero_eval["status"], "mandatory": True},
        {"test": "Tare Balancing & Net Weighing (A.4.6)", "status": tare_eval["status"], "mandatory": True},
        {"test": "Weighing Performance & Hysteresis (A.4.4)", "status": weighing_eval["status"], "mandatory": True},
        {"test": "Repeatability (A.4.10)", "status": repeatability_eval["status"], "mandatory": True},
        {"test": "Eccentricity (A.4.7)", "status": eccentricity_eval["status"], "mandatory": True},
    ]

    return {
        "overall_status": "PASS" if overall_pass else "FAIL",
        "overall_passed": overall_pass,
        "is_in_service": is_in_service,
        "use_turning_point": use_turning_point,
        "parameters": param_eval,
        "zero_test": zero_eval,
        "tare_test": tare_eval,
        "weighing_test": weighing_eval,
        "repeatability_test": repeatability_eval,
        "eccentricity_test": eccentricity_eval,
        "summary": summary_cards,
    }
