"""
Application Bootstrap and Factory for Currency Exchange Service.
Layered e2e Architecture with Context Path Configuration.
"""
import os
import logging
from flask import Flask
import constants
from e2e.utils.logging import configure_logging
from e2e.exception.error_handler import register_error_handlers
from e2e.utils.interceptors import register_interceptors
from e2e.route.exchange_routes import exchange_bp
from e2e.route.actuator_routes import actuators_bp
from e2e.route.swagger_routes import swagger_bp
from e2e.service.rate_service import rate_service

logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Application factory for Currency Exchange Microservice."""
    configure_logging(constants.LOG_LEVEL)

    app = Flask(__name__)
    app.config["SERVICE_NAME"] = constants.SERVICE_NAME
    app.config["CONTEXT_PATH"] = constants.CONTEXT_PATH

    # 1. Register Centralized Error Handling (Single point of exception handling)
    register_error_handlers(app)

    # 2. Register Request/Response Latency Interceptor
    register_interceptors(app)

    # 3. Register Blueprints (all mounted under CONTEXT_PATH: /currency-exchange-service-python)
    app.register_blueprint(exchange_bp)
    app.register_blueprint(actuators_bp)
    app.register_blueprint(swagger_bp)

    # 4. Ingest Initial Rates Dataset (S3 / Local Windows CSV)
    with app.app_context():
        try:
            rate_service.load_rates()
            logger.info(f"Currency Exchange Service successfully mounted at context path '{constants.CONTEXT_PATH}'")
        except Exception as e:
            logger.error(f"Failed to load rates on startup: {str(e)}", exc_info=True)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", constants.PORT))
    print(f"Starting Currency Exchange Service on port {port} at context path '{constants.CONTEXT_PATH}'...")
    app.run(host="0.0.0.0", port=port, debug=False)
