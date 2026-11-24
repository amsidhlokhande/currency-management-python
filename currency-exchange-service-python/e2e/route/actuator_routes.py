"""
Actuators and Operational Health Probes.
Mounted strictly under the service context path.
"""
import time
import sys
from datetime import datetime, timezone
from flask import Blueprint, jsonify
import constants
from e2e.service.rate_service import rate_service

actuators_bp = Blueprint("actuators", __name__, url_prefix=constants.CONTEXT_PATH)
START_TIME = time.time()

@actuators_bp.route("/health", methods=["GET"])
def health():
    """System health status with component readiness."""
    rate_count = len(rate_service.get_all_rates())
    is_ready = rate_count > 0
    return jsonify({
        "status": "UP" if is_ready else "DEGRADED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "contextPath": constants.CONTEXT_PATH,
        "components": {
            "rateRepository": {
                "status": "UP" if is_ready else "DOWN",
                "details": {
                    "totalRatesLoaded": rate_count,
                    "dataSource": rate_service.data_source
                }
            },
            "diskSpace": {"status": "UP"}
        }
    }), (200 if is_ready else 503)


@actuators_bp.route("/health/liveness", methods=["GET"])
def liveness():
    """Liveness probe for Cloud Run / Kubernetes."""
    return jsonify({"status": "UP", "probe": "liveness"}), 200


@actuators_bp.route("/health/readiness", methods=["GET"])
def readiness():
    """Readiness probe checking rate store availability."""
    is_ready = len(rate_service.get_all_rates()) > 0
    if is_ready:
        return jsonify({"status": "UP", "probe": "readiness"}), 200
    return jsonify({"status": "OUT_OF_SERVICE", "probe": "readiness", "reason": "Rate repository is empty"}), 503


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
        "rates.total_loaded": len(rate_service.get_all_rates()),
        "python.version": sys.version.split()[0]
    }), 200
