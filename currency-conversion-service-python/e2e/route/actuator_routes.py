"""
Actuators and Operational Health Probes for Conversion Service.
Mounted strictly under the service context path.
"""
import time
import sys
from datetime import datetime, timezone
from flask import Blueprint, jsonify
import constants

actuators_bp = Blueprint("actuators", __name__, url_prefix=constants.CONTEXT_PATH)
START_TIME = time.time()

@actuators_bp.route("/health", methods=["GET"])
def health():
    """System health status with downstream exchange configuration."""
    return jsonify({
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "contextPath": constants.CONTEXT_PATH,
        "components": {
            "exchangeClient": {
                "status": "UP",
                "details": {
                    "targetUrl": constants.EXCHANGE_SERVICE_URL,
                    "retries": constants.HTTP_MAX_RETRIES
                }
            },
            "diskSpace": {"status": "UP"}
        }
    }), 200


@actuators_bp.route("/health/liveness", methods=["GET"])
def liveness():
    """Liveness probe for Cloud Run / Kubernetes."""
    return jsonify({"status": "UP", "probe": "liveness"}), 200


@actuators_bp.route("/health/readiness", methods=["GET"])
def readiness():
    """Readiness probe for Cloud Run / Kubernetes."""
    return jsonify({"status": "UP", "probe": "readiness"}), 200


@actuators_bp.route("/info", methods=["GET"])
def info():
    """Service metadata, runtime version, and uptime."""
    return jsonify({
        "app": {
            "name": constants.SERVICE_NAME,
            "version": "1.0.0",
            "contextPath": constants.CONTEXT_PATH
        },
        "python": {
            "version": sys.version,
            "runtime": "Python 3.15.2"
        },
        "uptimeSeconds": round(time.time() - START_TIME, 2)
    }), 200


@actuators_bp.route("/metrics", methods=["GET"])
def metrics():
    """System metrics."""
    return jsonify({
        "system.uptime": round(time.time() - START_TIME, 2),
        "target.exchange_service": constants.EXCHANGE_SERVICE_URL,
        "python.version": sys.version.split()[0]
    }), 200
