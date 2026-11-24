"""
Swagger and OpenAPI 3.0 Documentation Routes for Currency Exchange Service.
Mounted strictly under the service context path using enterprise_core factory.
"""
from enterprise_core import create_swagger_blueprint
import constants

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Currency Exchange Service API",
        "version": "1.0.0",
        "description": f"Production Python 3.15.2 / Flask Microservice. Base Context Path: {constants.CONTEXT_PATH}"
    },
    "servers": [
        {"url": f"http://localhost:{constants.PORT}{constants.CONTEXT_PATH}", "description": "Local Development Server"}
    ],
    "paths": {
        "/currency-exchange/from/{from}/to/{to}": {
            "get": {
                "summary": "Get currency conversion rate",
                "parameters": [
                    {"name": "from", "in": "path", "required": True, "schema": {"type": "string", "example": "USD"}},
                    {"name": "to", "in": "path", "required": True, "schema": {"type": "string", "example": "INR"}}
                ],
                "responses": {
                    "200": {"description": "Exchange rate entity retrieved"},
                    "400": {"description": "Invalid currency code (CESP_002)"},
                    "404": {"description": "Rate not available (CESP_001)"}
                }
            }
        },
        "/currency-exchange/rates": {
            "get": {
                "summary": "Get all currency rates",
                "responses": {
                    "200": {"description": "Array of exchange rates"}
                }
            }
        },
        "/currency-exchange/reload": {
            "post": {
                "summary": "Reload exchange rates",
                "responses": {
                    "200": {"description": "Rate store reloaded"}
                }
            }
        }
    }
}

swagger_bp = create_swagger_blueprint(
    context_path=constants.CONTEXT_PATH,
    openapi_spec=OPENAPI_SPEC,
    title="Currency Exchange Service - Swagger UI"
)
