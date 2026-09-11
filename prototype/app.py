"""
NAWI Test Report Generation System (OIML R-76)
Flask Server Entry Point
"""

# pyrefly: ignore [missing-import]
from flask import Flask, render_template
import os
import config
from routes.api import api_bp
from routes.views import views_bp
import database


def create_app():
    # Explicit paths so Flask resolves correctly both locally and on Vercel
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, "static"),
        template_folder=os.path.join(base_dir, "templates"),
    )
    app.config.from_object("config")

    # Ensure database is initialized
    database.init_db()

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("base.html", content="<div class='container' style='padding: 60px 20px; text-align: center;'><h2>404 - Page Not Found</h2><p>The requested metrological report or page could not be found.</p><a href='/' class='btn btn-primary'>Return to Dashboard</a></div>"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("base.html", content="<div class='container' style='padding: 60px 20px; text-align: center;'><h2>500 - Server Error</h2><p>An internal error occurred during calculation or PDF generation.</p><a href='/' class='btn btn-primary'>Return to Dashboard</a></div>"), 500

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 70)
    print(" NAWI Test Report Generation System (OIML R-76)")
    print(" Metrological Verification Engine & PDF Generator")
    print(" Server running on: http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host="0.0.0.0", port=5000, debug=True)
