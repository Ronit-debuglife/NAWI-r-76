"""
API Blueprint for NAWI Test Report Generation System
Handles OIML R-76 calculations, database persistence, PDF requests, and demo datasets.
"""

from flask import Blueprint, request, jsonify, send_file, current_app
import os
import copy
from r76_calculator import evaluate_full_report, CLASS_I, CLASS_II, CLASS_III, CLASS_IIII
import database
import pdf_generator
from config import PDF_DIR

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Pre-configured demo datasets for college / SIH project demonstrations
DEMO_DATASETS = {
    "retail_class3": {
        "report_title": "Class III Retail Counter Scale (15 kg / 5 g)",
        "certificate_no": "CERT-2026-RET-0192",
        "test_date": "2026-09-07",
        "inspector_name": "Er. R. Sharma (Senior Metrologist)",
        "customer_name": "Fresh Mart Hypermarket Ltd",
        "location": "Central Inspection Bay #2, Mumbai",
        "is_in_service": False,
        "use_turning_point": True,
        "instrument": {
            "manufacturer": "Mettler Toledo / Avery",
            "model": "bRite Standard Retail NAWI",
            "serial_no": "BR-2026-88341",
            "accuracy_class": CLASS_III,
            "max_capacity": 15.0,
            "min_capacity": 0.1,
            "e": 0.005,
            "d": 0.005,
            "unit": "kg",
            "tare_max": 5.0,
            "device_type": "Electronic Counter-Top Scale",
        },
        "environment": {
            "temp_c": 22.0,
            "humidity_pct": 52.0,
            "pressure_hpa": 1012.5,
        },
        "standards": {
            "standards_id": "OIML Class M1 Standard Weights (1g - 20kg)",
            "standards_cert": "NABL-CAL-2026-00912",
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
                {"position_id": 1, "position_name": "Center (1)", "indication": 5.000, "delta_l": 0.0025},
                {"position_id": 2, "position_name": "Front-Left (2)", "indication": 5.000, "delta_l": 0.0020},
                {"position_id": 3, "position_name": "Back-Left (3)", "indication": 5.000, "delta_l": 0.0030},
                {"position_id": 4, "position_name": "Back-Right (4)", "indication": 5.000, "delta_l": 0.0025},
                {"position_id": 5, "position_name": "Front-Right (5)", "indication": 5.000, "delta_l": 0.0025},
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
    },
    "lab_balance_class2": {
        "report_title": "Class II High-Precision Analytical Balance (220 g / 0.001 g)",
        "certificate_no": "CERT-2026-LAB-0431",
        "test_date": "2026-09-07",
        "inspector_name": "Dr. Ananya Sen (Principal Metrologist)",
        "customer_name": "Advanced Pharma Analytics R&D",
        "location": "Cleanroom Lab Alpha, Bengaluru",
        "is_in_service": False,
        "use_turning_point": True,
        "instrument": {
            "manufacturer": "Sartorius / Shimadzu",
            "model": "Secura 225D High Precision Balance",
            "serial_no": "SEC-992014-K",
            "accuracy_class": CLASS_II,
            "max_capacity": 220.0,
            "min_capacity": 0.02,
            "e": 0.001,
            "d": 0.0001,
            "unit": "g",
            "tare_max": 220.0,
            "device_type": "Precision Laboratory Balance",
        },
        "environment": {
            "temp_c": 20.2,
            "humidity_pct": 45.0,
            "pressure_hpa": 1013.0,
        },
        "standards": {
            "standards_id": "OIML Class E2 Reference Weights Set (1mg - 500g)",
            "standards_cert": "NPLI-CAL-2026-1188",
        },
        "zero_test": {
            "indication": 0.0,
            "delta_l": 0.0005,
        },
        "tare_test": {
            "tare_load": 50.0,
            "tare_indication": 50.0,
            "delta_l_tare": 0.0005,
            "net_test_load": 100.0,
            "net_indication": 100.0,
            "delta_l_net": 0.0005,
        },
        "eccentricity_test": {
            "test_load": 70.0,
            "points": [
                {"position_id": 1, "position_name": "Center (1)", "indication": 70.000, "delta_l": 0.0005},
                {"position_id": 2, "position_name": "Front-Left (2)", "indication": 70.000, "delta_l": 0.0004},
                {"position_id": 3, "position_name": "Back-Left (3)", "indication": 70.000, "delta_l": 0.0006},
                {"position_id": 4, "position_name": "Back-Right (4)", "indication": 70.000, "delta_l": 0.0005},
                {"position_id": 5, "position_name": "Front-Right (5)", "indication": 70.000, "delta_l": 0.0005},
            ],
        },
        "repeatability_test": {
            "series": [
                {"load": 100.0, "readings": [100.000, 100.001, 100.000, 100.000]},
                {"load": 200.0, "readings": [200.000, 200.001, 200.001, 200.000]},
            ],
        },
        "weighing_test": {
            "rows": [
                {"load": 0.02, "i_inc": 0.020, "delta_l_inc": 0.0005, "i_dec": 0.020, "delta_l_dec": 0.0005},
                {"load": 5.0, "i_inc": 5.000, "delta_l_inc": 0.0005, "i_dec": 5.000, "delta_l_dec": 0.0005},
                {"load": 20.0, "i_inc": 20.000, "delta_l_inc": 0.0005, "i_dec": 20.000, "delta_l_dec": 0.0005},
                {"load": 100.0, "i_inc": 100.000, "delta_l_inc": 0.0005, "i_dec": 100.000, "delta_l_dec": 0.0005},
                {"load": 220.0, "i_inc": 220.000, "delta_l_inc": 0.0005, "i_dec": 220.000, "delta_l_dec": 0.0005},
            ],
        },
    },
    "industrial_class3": {
        "report_title": "Class III Heavy Industrial Platform Scale (60 kg / 20 g)",
        "certificate_no": "CERT-2026-IND-7719",
        "test_date": "2026-09-07",
        "inspector_name": "K. Patel (Legal Metrology Officer)",
        "customer_name": "National Cargo & Freight Hub",
        "location": "Warehouse Terminal 4, Gujarat",
        "is_in_service": False,
        "use_turning_point": True,
        "instrument": {
            "manufacturer": "Essae / Sansui",
            "model": "DS-215 Heavy Industrial Floor NAWI",
            "serial_no": "IND-60K-004481",
            "accuracy_class": CLASS_III,
            "max_capacity": 60.0,
            "min_capacity": 0.4,
            "e": 0.02,
            "d": 0.02,
            "unit": "kg",
            "tare_max": 20.0,
            "device_type": "Industrial Floor/Platform Scale",
        },
        "environment": {
            "temp_c": 24.5,
            "humidity_pct": 58.0,
            "pressure_hpa": 1009.0,
        },
        "standards": {
            "standards_id": "OIML Class M1 Cast Iron Weights (5kg, 10kg, 20kg)",
            "standards_cert": "W&M-IND-2026-9011",
        },
        "zero_test": {
            "indication": 0.0,
            "delta_l": 0.010,
        },
        "tare_test": {
            "tare_load": 10.0,
            "tare_indication": 10.0,
            "delta_l_tare": 0.010,
            "net_test_load": 20.0,
            "net_indication": 20.0,
            "delta_l_net": 0.010,
        },
        "eccentricity_test": {
            "test_load": 20.0,
            "points": [
                {"position_id": 1, "position_name": "Center (1)", "indication": 20.00, "delta_l": 0.010},
                {"position_id": 2, "position_name": "Front-Left (2)", "indication": 20.00, "delta_l": 0.008},
                {"position_id": 3, "position_name": "Back-Left (3)", "indication": 20.00, "delta_l": 0.012},
                {"position_id": 4, "position_name": "Back-Right (4)", "indication": 20.00, "delta_l": 0.010},
                {"position_id": 5, "position_name": "Front-Right (5)", "indication": 20.00, "delta_l": 0.010},
            ],
        },
        "repeatability_test": {
            "series": [
                {"load": 30.0, "readings": [30.00, 30.02, 30.00]},
                {"load": 60.0, "readings": [60.00, 60.02, 60.00]},
            ],
        },
        "weighing_test": {
            "rows": [
                {"load": 0.4, "i_inc": 0.40, "delta_l_inc": 0.010, "i_dec": 0.40, "delta_l_dec": 0.010},
                {"load": 10.0, "i_inc": 10.00, "delta_l_inc": 0.010, "i_dec": 10.00, "delta_l_dec": 0.010},
                {"load": 20.0, "i_inc": 20.00, "delta_l_inc": 0.010, "i_dec": 20.00, "delta_l_dec": 0.010},
                {"load": 40.0, "i_inc": 40.00, "delta_l_inc": 0.010, "i_dec": 40.00, "delta_l_dec": 0.010},
                {"load": 60.0, "i_inc": 60.00, "delta_l_inc": 0.010, "i_dec": 60.00, "delta_l_dec": 0.010},
            ],
        },
    },
    "failing_scale": {
        "report_title": "Defective / Out-of-Tolerance NAWI Scale (Class III Demo)",
        "certificate_no": "REJECT-2026-FAIL-0012",
        "test_date": "2026-09-07",
        "inspector_name": "Er. R. Sharma (Metrology Inspector)",
        "customer_name": "Quality Audit Demo Agency",
        "location": "Fault Testing Workbench",
        "is_in_service": False,
        "use_turning_point": True,
        "instrument": {
            "manufacturer": "Unbranded Mechanical-Electronic Hybrid",
            "model": "Old 30K Industrial",
            "serial_no": "DEFECT-9092-X",
            "accuracy_class": CLASS_III,
            "max_capacity": 30.0,
            "min_capacity": 0.2,
            "e": 0.01,
            "d": 0.01,
            "unit": "kg",
            "tare_max": 10.0,
            "device_type": "Worn Platform Scale",
        },
        "environment": {
            "temp_c": 28.0,
            "humidity_pct": 70.0,
            "pressure_hpa": 1010.0,
        },
        "standards": {
            "standards_id": "OIML Class M1 Standard Weights",
            "standards_cert": "NABL-CAL-2026-00912",
        },
        "zero_test": {
            "indication": 0.0,
            "delta_l": 0.005,  # E0 = 0 + 0.005 - 0.005 = 0
        },
        "tare_test": {
            "tare_load": 5.0,
            "tare_indication": 5.0,
            "delta_l_tare": 0.005,
            "net_test_load": 10.0,
            "net_indication": 10.0,
            "delta_l_net": 0.005,
        },
        "eccentricity_test": {
            "test_load": 10.0,
            "points": [
                {"position_id": 1, "position_name": "Center (1)", "indication": 10.00, "delta_l": 0.005},
                # Position 2 has large corner error exceeding MPE (MPE at 10kg is 0.010kg, this error is 0.035kg)
                {"position_id": 2, "position_name": "Front-Left (2 - Corner Binding)", "indication": 10.04, "delta_l": 0.005},
                {"position_id": 3, "position_name": "Back-Left (3)", "indication": 10.00, "delta_l": 0.005},
                {"position_id": 4, "position_name": "Back-Right (4)", "indication": 10.00, "delta_l": 0.005},
                {"position_id": 5, "position_name": "Front-Right (5)", "indication": 10.00, "delta_l": 0.005},
            ],
        },
        "repeatability_test": {
            "series": [
                {"load": 15.0, "readings": [15.00, 15.01, 15.00]},
                # High friction causing repeatability failure at Max (spread > MPE 0.015kg)
                {"load": 30.0, "readings": [30.00, 30.03, 29.98]},
            ],
        },
        "weighing_test": {
            "rows": [
                {"load": 0.2, "i_inc": 0.20, "delta_l_inc": 0.005, "i_dec": 0.20, "delta_l_dec": 0.005},
                {"load": 5.0, "i_inc": 5.00, "delta_l_inc": 0.005, "i_dec": 5.00, "delta_l_dec": 0.005},
                {"load": 10.0, "i_inc": 10.00, "delta_l_inc": 0.005, "i_dec": 10.00, "delta_l_dec": 0.005},
                {"load": 20.0, "i_inc": 20.02, "delta_l_inc": 0.005, "i_dec": 20.02, "delta_l_dec": 0.005},
                # Exceeds MPE at 30kg
                {"load": 30.0, "i_inc": 30.04, "delta_l_inc": 0.005, "i_dec": 30.05, "delta_l_dec": 0.005},
            ],
        },
    },
}


@api_bp.route("/demo/<preset_key>", methods=["GET"])
def get_demo_dataset(preset_key: str):
    """Returns a pre-configured demo test case."""
    preset = DEMO_DATASETS.get(preset_key)
    if not preset:
        return jsonify({"error": f"Unknown preset '{preset_key}'. Available: {list(DEMO_DATASETS.keys())}"}), 404
    return jsonify(copy.deepcopy(preset))


@api_bp.route("/calculate", methods=["POST"])
def calculate_r76():
    """
    Performs full OIML R-76 calculations without saving to database.
    Used for instant real-time feedback as the user edits test fields.
    """
    payload = request.get_json() or {}
    evaluation = evaluate_full_report(payload)
    return jsonify(evaluation)


@api_bp.route("/reports", methods=["POST"])
def create_or_update_report():
    """
    Saves or updates a test report in SQLite and automatically compiles the ReportLab PDF.
    """
    payload = request.get_json() or {}
    evaluation = evaluate_full_report(payload)

    # Save to SQLite
    saved_meta = database.save_report(payload, evaluation)
    payload["report_id"] = saved_meta["report_id"]
    payload["certificate_no"] = saved_meta["certificate_no"]

    # Generate ReportLab PDF report
    pdf_path = pdf_generator.build_pdf_report(payload, evaluation)

    return jsonify({
        "success": True,
        "report_id": saved_meta["report_id"],
        "certificate_no": saved_meta["certificate_no"],
        "overall_status": saved_meta["overall_status"],
        "pdf_url": f"/api/reports/{saved_meta['report_id']}/pdf",
        "report_url": f"/report/{saved_meta['report_id']}",
        "evaluation": evaluation,
    })


@api_bp.route("/reports", methods=["GET"])
def get_reports_list():
    """Lists saved test reports with optional search."""
    search = request.args.get("q", "")
    limit = int(request.args.get("limit", 50))
    reports = database.list_reports(limit=limit, search=search)
    return jsonify(reports)


@api_bp.route("/reports/<report_id>", methods=["GET"])
def get_report_detail(report_id: str):
    """Retrieves full details of a saved report."""
    rep = database.get_report(report_id)
    if not rep:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(rep)


@api_bp.route("/reports/<report_id>", methods=["DELETE"])
def remove_report(report_id: str):
    """Deletes a saved report and associated PDF."""
    success = database.delete_report(report_id)
    if not success:
        return jsonify({"error": "Report not found or could not be deleted"}), 404

    # Remove PDF file if exists
    pdf_path = os.path.join(PDF_DIR, f"NAWI_Report_{report_id}.pdf")
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except OSError:
            pass

    return jsonify({"success": True, "message": f"Report {report_id} deleted."})


@api_bp.route("/reports/<report_id>/pdf", methods=["GET"])
def download_pdf(report_id: str):
    """Streams or regenerates the ReportLab PDF test report."""
    rep = database.get_report(report_id)
    if not rep:
        return jsonify({"error": "Report not found"}), 404

    pdf_name = f"NAWI_Report_{report_id}.pdf"
    pdf_path = os.path.join(PDF_DIR, pdf_name)

    # If PDF file does not exist on disk, regenerate it from saved database record
    if not os.path.exists(pdf_path):
        payload = rep.get("raw_input", {})
        payload["report_id"] = report_id
        evaluation = rep.get("evaluation") or evaluate_full_report(payload)
        pdf_path = pdf_generator.build_pdf_report(payload, evaluation)

    as_attachment = request.args.get("download", "0") == "1"
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=as_attachment,
        download_name=f"NAWI_Verification_Report_{report_id}.pdf",
    )


@api_bp.route("/stats", methods=["GET"])
def get_statistics():
    """Returns database report count statistics."""
    stats = database.get_stats()
    return jsonify(stats)
