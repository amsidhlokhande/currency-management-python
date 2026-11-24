"""
Setup script for enterprise-core-python.
Enables standard pip install -e . and wheel packaging.
"""
from setuptools import setup, find_packages

setup(
    name="enterprise-core-python",
    version="1.0.0",
    packages=find_packages(include=["enterprise_core", "enterprise_core.*"]),
    install_requires=[
        "Flask>=3.0.0",
        "werkzeug>=3.0.0",
        "python-json-logger>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0", "requests>=2.30.0"],
    },
    python_requires=">=3.10",
)
