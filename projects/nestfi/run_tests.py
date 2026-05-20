#!/usr/bin/env python
"""Test runner script for QA verification."""
import subprocess
import sys
import json

result = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/tests/", "-v", "--tb=short",
     "--cov=app", "--cov-report=json", "--cov-report=term-missing"],
    cwd="/Users/tuan/MyGitHub/learning-vault/projects/nestfi",
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
