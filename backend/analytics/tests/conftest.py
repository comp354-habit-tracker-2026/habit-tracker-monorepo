"""Pytest configuration for analytics tests.

Inserts the analytics/business directory onto sys.path so that
baseline_forecaster.py (and future standalone modules) can be imported
directly without triggering analytics/business/__init__.py, which
depends on Django and other backend services.
"""
import os
import sys

# Allow direct imports like `from baseline_forecaster import ...`
_business_dir = os.path.join(os.path.dirname(__file__), "..", "business")
sys.path.insert(0, os.path.abspath(_business_dir))
