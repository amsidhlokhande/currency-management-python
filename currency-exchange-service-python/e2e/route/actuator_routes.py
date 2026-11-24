"""
Actuators and Operational Health Probes for Currency Exchange Service.
Mounted strictly under the service context path using enterprise_core factory.
"""
from enterprise_core import create_actuators_blueprint
import constants
from e2e.service.rate_service import rate_service

def _check_health():
    rate_count = len(rate_service.get_all_rates())
    is_ready = rate_count > 0
    return is_ready, {
        "rateRepository": {
            "status": "UP" if is_ready else "DOWN",
            "details": {
                "totalRatesLoaded": rate_count,
                "dataSource": rate_service.data_source
            }
        }
    }

def _check_readiness():
    is_ready = len(rate_service.get_all_rates()) > 0
    return is_ready, (None if is_ready else "Rate repository is empty")

actuators_bp = create_actuators_blueprint(
    context_path=constants.CONTEXT_PATH,
    service_name=constants.SERVICE_NAME,
    version="1.0.0",
    health_callback=_check_health,
    readiness_callback=_check_readiness
)
