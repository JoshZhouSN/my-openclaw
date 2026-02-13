"""
Pytest configuration for OpenClaw Config Manager tests.
"""
import os
import tempfile
from pathlib import Path


def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_runtest_setup(item):
    """Setup for individual tests."""
    # Create a temporary directory for each test to avoid conflicts
    pass