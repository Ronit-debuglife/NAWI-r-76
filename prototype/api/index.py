"""
Vercel Serverless Function Entry Point
Routes all requests through the Flask application.
"""

import sys
import os

# Add the parent directory to the Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects the WSGI app to be named 'app'
# This file is the entry point for all serverless requests
