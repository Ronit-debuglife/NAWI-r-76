"""
SQLite Database Layer for NAWI Test Report Generation System
Manages persistence of instrument details, test observations, and evaluation results.
"""

import sqlite3
import json
import uuid
import datetime
from typing import Dict, List, Any, Optional
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT UNIQUE NOT NULL,
            certificate_no TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            
            -- Instrument Details
            manufacturer TEXT,
            model TEXT,
            serial_no TEXT,
            accuracy_class TEXT,
            max_capacity REAL,
            min_capacity REAL,
            e_interval REAL,
            d_interval REAL,
            unit TEXT,
            tare_max REAL,
            device_type TEXT,
            
            -- Test Environment & Personnel
            inspector_name TEXT,
            customer_name TEXT,
            location TEXT,
            test_date TEXT,
            temp_c REAL,
            humidity_pct REAL,
            pressure_hpa REAL,
            standards_id TEXT,
            standards_cert TEXT,
            
            -- Test Options
            is_in_service INTEGER DEFAULT 0,
            use_turning_point INTEGER DEFAULT 1,
            
            -- Evaluation Results
            overall_status TEXT NOT NULL,
            
            -- Serialized Data
            raw_input_json TEXT NOT NULL,
            evaluation_json TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reports_report_id ON reports(report_id);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at DESC);
    """)

    conn.commit()
    conn.close()


def generate_report_id() -> str:
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"R76-{today_str}-{unique_suffix}"


def save_report(payload: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves or updates a test report in the SQLite database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    instrument = payload.get("instrument", {})
    environment = payload.get("environment", {})
    standards = payload.get("standards", {})

    report_id = payload.get("report_id")
    now_iso = datetime.datetime.now().isoformat()

    if not report_id:
        report_id = generate_report_id()
        is_update = False
    else:
        cursor.execute("SELECT id FROM reports WHERE report_id = ?", (report_id,))
        is_update = cursor.fetchone() is not None

    cert_no = payload.get("certificate_no") or f"CERT-{report_id}"
    test_date = payload.get("test_date") or datetime.date.today().isoformat()
    overall_status = evaluation.get("overall_status", "FAIL")

    raw_json = json.dumps(payload)
    eval_json = json.dumps(evaluation)

    if is_update:
        cursor.execute("""
            UPDATE reports SET
                certificate_no = ?,
                updated_at = ?,
                manufacturer = ?,
                model = ?,
                serial_no = ?,
                accuracy_class = ?,
                max_capacity = ?,
                min_capacity = ?,
                e_interval = ?,
                d_interval = ?,
                unit = ?,
                tare_max = ?,
                device_type = ?,
                inspector_name = ?,
                customer_name = ?,
                location = ?,
                test_date = ?,
                temp_c = ?,
                humidity_pct = ?,
                pressure_hpa = ?,
                standards_id = ?,
                standards_cert = ?,
                is_in_service = ?,
                use_turning_point = ?,
                overall_status = ?,
                raw_input_json = ?,
                evaluation_json = ?
            WHERE report_id = ?
        """, (
            cert_no,
            now_iso,
            instrument.get("manufacturer", ""),
            instrument.get("model", ""),
            instrument.get("serial_no", ""),
            instrument.get("accuracy_class", "III"),
            float(instrument.get("max_capacity", 0.0)),
            float(instrument.get("min_capacity", 0.0)),
            float(instrument.get("e", 0.0)),
            float(instrument.get("d", 0.0)),
            instrument.get("unit", "kg"),
            float(instrument.get("tare_max", 0.0) or 0.0),
            instrument.get("device_type", "Standard Electronic Platform"),
            payload.get("inspector_name", ""),
            payload.get("customer_name", ""),
            payload.get("location", ""),
            test_date,
            float(environment.get("temp_c", 20.0) or 20.0),
            float(environment.get("humidity_pct", 50.0) or 50.0),
            float(environment.get("pressure_hpa", 1013.25) or 1013.25),
            standards.get("standards_id", "F1/F2 Working Standards"),
            standards.get("standards_cert", ""),
            1 if payload.get("is_in_service") else 0,
            1 if payload.get("use_turning_point", True) else 0,
            overall_status,
            raw_json,
            eval_json,
            report_id,
        ))
    else:
        cursor.execute("""
            INSERT INTO reports (
                report_id, certificate_no, created_at, updated_at,
                manufacturer, model, serial_no, accuracy_class,
                max_capacity, min_capacity, e_interval, d_interval, unit, tare_max, device_type,
                inspector_name, customer_name, location, test_date,
                temp_c, humidity_pct, pressure_hpa, standards_id, standards_cert,
                is_in_service, use_turning_point, overall_status,
                raw_input_json, evaluation_json
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?
            )
        """, (
            report_id,
            cert_no,
            now_iso,
            now_iso,
            instrument.get("manufacturer", ""),
            instrument.get("model", ""),
            instrument.get("serial_no", ""),
            instrument.get("accuracy_class", "III"),
            float(instrument.get("max_capacity", 0.0)),
            float(instrument.get("min_capacity", 0.0)),
            float(instrument.get("e", 0.0)),
            float(instrument.get("d", 0.0)),
            instrument.get("unit", "kg"),
            float(instrument.get("tare_max", 0.0) or 0.0),
            instrument.get("device_type", "Standard Electronic Platform"),
            payload.get("inspector_name", ""),
            payload.get("customer_name", ""),
            payload.get("location", ""),
            test_date,
            float(environment.get("temp_c", 20.0) or 20.0),
            float(environment.get("humidity_pct", 50.0) or 50.0),
            float(environment.get("pressure_hpa", 1013.25) or 1013.25),
            standards.get("standards_id", "F1/F2 Working Standards"),
            standards.get("standards_cert", ""),
            1 if payload.get("is_in_service") else 0,
            1 if payload.get("use_turning_point", True) else 0,
            overall_status,
            raw_json,
            eval_json,
        ))

    conn.commit()
    conn.close()

    return {
        "report_id": report_id,
        "certificate_no": cert_no,
        "overall_status": overall_status,
        "created_at": now_iso,
    }


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single test report by report_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    data = dict(row)
    data["raw_input"] = json.loads(data["raw_input_json"]) if data.get("raw_input_json") else {}
    data["evaluation"] = json.loads(data["evaluation_json"]) if data.get("evaluation_json") else {}
    return data


def list_reports(limit: int = 50, search: str = "") -> List[Dict[str, Any]]:
    """Lists saved test reports with optional search filtering."""
    conn = get_connection()
    cursor = conn.cursor()

    if search:
        search_param = f"%{search}%"
        cursor.execute("""
            SELECT id, report_id, certificate_no, created_at, manufacturer, model,
                   serial_no, accuracy_class, max_capacity, unit, inspector_name,
                   overall_status
            FROM reports
            WHERE report_id LIKE ? OR certificate_no LIKE ? OR manufacturer LIKE ? OR model LIKE ? OR serial_no LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """, (search_param, search_param, search_param, search_param, search_param, limit))
    else:
        cursor.execute("""
            SELECT id, report_id, certificate_no, created_at, manufacturer, model,
                   serial_no, accuracy_class, max_capacity, unit, inspector_name,
                   overall_status
            FROM reports
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_report(report_id: str) -> bool:
    """Deletes a test report by report_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reports WHERE report_id = ?", (report_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_stats() -> Dict[str, int]:
    """Returns aggregated stats on reports."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM reports")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as passed FROM reports WHERE overall_status = 'PASS'")
    passed = cursor.fetchone()["passed"]
    cursor.execute("SELECT COUNT(*) as failed FROM reports WHERE overall_status = 'FAIL'")
    failed = cursor.fetchone()["failed"]
    conn.close()
    return {"total": total, "passed": passed, "failed": failed}


# Initialize DB automatically on import
init_db()
