"""
Actuators and Operational Health Probes for Currency Conversion Service.
Mounted strictly under the service context path using enterprise_core factory.
"""
from enterprise_core import create_actuators_blueprint
import constants

def _check_health():
    return True, {
        "exchangeClient": {
            "status": "UP",
            "details": {
                "targetUrl": constants.EXCHANGE_SERVICE_URL,
                "retries": constants.HTTP_MAX_RETRIES
            }
        }
    }

actuators_bp = create_actuators_blueprint(
    context_path=constants.CONTEXT_PATH,
    service_name=constants.SERVICE_NAME,
    version="1.0.0",
    health_callback=_check_health,
    readiness_callback=lambda: (True, None)
)
