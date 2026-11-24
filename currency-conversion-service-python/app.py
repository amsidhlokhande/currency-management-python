"""
Application Bootstrap and Factory for Currency Conversion Service.
Layered e2e Architecture with Context Path Configuration.
"""
import os
import logging
from flask import Flask
import constants
from e2e.utils.logging import configure_logging
from e2e.exception.error_handler import register_error_handlers
from e2e.utils.interceptors import register_interceptors
from e2e.route.conversion_routes import conversion_bp
from e2e.route.actuator_routes import actuators_bp
from e2e.route.swagger_routes import swagger_bp

logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """Application factory for Currency Conversion Microservice."""
    configure_logging(constants.LOG_LEVEL)

    app = Flask(__name__)
    app.config["SERVICE_NAME"] = constants.SERVICE_NAME
    app.config["CONTEXT_PATH"] = constants.CONTEXT_PATH

    # 1. Register Centralized Error Handling (Single point of error handling)
    register_error_handlers(app)

    # 2. Register Request/Response Latency Interceptor
    register_interceptors(app)

    # 3. Register Blueprints (all mounted under CONTEXT_PATH: /currency-conversion-service-python)
    app.register_blueprint(conversion_bp)
    app.register_blueprint(actuators_bp)
    app.register_blueprint(swagger_bp)

    logger.info(f"Currency Conversion Service successfully mounted at context path '{constants.CONTEXT_PATH}'")
    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", constants.PORT))
    print(f"Starting Currency Conversion Service on port {port} at context path '{constants.CONTEXT_PATH}'...")
    app.run(host="0.0.0.0", port=port, debug=False)
