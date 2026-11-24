"""
Request and Response Filters/Interceptors for Latency Tracking and Traceability.
Delegates to the shared enterprise_core interceptor engine.
"""
from flask import Flask
from enterprise_core import register_latency_interceptors

def register_interceptors(app: Flask):
    """Registers enterprise latency tracking and correlation ID interceptors."""
    register_latency_interceptors(app)

__all__ = ["register_interceptors"]
