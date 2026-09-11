import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Vercel serverless functions have a read-only filesystem except /tmp
IS_VERCEL = os.environ.get("VERCEL", False)

if IS_VERCEL:
    DATA_DIR = "/tmp/data"
    DB_PATH = os.path.join(DATA_DIR, "nawi_reports.db")
    PDF_DIR = os.path.join(DATA_DIR, "generated_reports")
else:
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DB_PATH = os.path.join(DATA_DIR, "nawi_reports.db")
    PDF_DIR = os.path.join(DATA_DIR, "generated_reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

SECRET_KEY = os.environ.get("SECRET_KEY", "nawi-oiml-r76-sih-metrology-key-2026")
DEBUG = not IS_VERCEL
