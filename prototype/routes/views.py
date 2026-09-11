"""
Views Blueprint for NAWI Test Report Generation System
Renders dashboard, records log, and web-based certificate/report view.
"""

# pyrefly: ignore [missing-import]
from flask import Blueprint, render_template, abort
import database

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def dashboard():
    """Main verification & test suite dashboard."""
    stats = database.get_stats()
    return render_template("index.html", stats=stats)


@views_bp.route("/records")
def records_view():
    """Historical records list of all saved test reports."""
    reports = database.list_reports(limit=100)
    stats = database.get_stats()
    return render_template("records.html", reports=reports, stats=stats)


@views_bp.route("/report/<report_id>")
def report_detail_view(report_id: str):
    """Detailed web preview of a specific test report."""
    report = database.get_report(report_id)
    if not report:
        abort(404, description="Report not found.")
    return render_template("report_view.html", report=report)


@views_bp.route("/login")
@views_bp.route("/auth")
@views_bp.route("/signup")
def auth_view():
    """Authentication portal: Sign In, Sign Up, and Google Sign-In."""
    return render_template("auth.html")

