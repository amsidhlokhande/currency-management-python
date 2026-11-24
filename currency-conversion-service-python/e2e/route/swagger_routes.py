"""
Swagger and OpenAPI 3.0 Documentation Routes for Conversion Service.
Mounted strictly under the service context path using enterprise_core factory.
"""
from enterprise_core import create_swagger_blueprint
import constants

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Currency Conversion Service API",
        "version": "1.0.0",
        "description": f"Production Python 3.15.2 / Flask Microservice. Base Context Path: {constants.CONTEXT_PATH}"
    },
    "servers": [
        {"url": f"http://localhost:{constants.PORT}{constants.CONTEXT_PATH}", "description": "Local Development Server"}
    ],
    "paths": {
        "/currency-conversion/from/{from}/to/{to}/quantity/{quantity}": {
            "get": {
                "summary": "Calculate converted currency amount based on live exchange rates",
                "parameters": [
                    {"name": "from", "in": "path", "required": True, "schema": {"type": "string", "example": "USD"}},
                    {"name": "to", "in": "path", "required": True, "schema": {"type": "string", "example": "INR"}},
                    {"name": "quantity", "in": "path", "required": True, "schema": {"type": "number", "example": 100}}
                ],
                "responses": {
                    "200": {"description": "Conversion result successfully calculated"},
                    "400": {"description": "Invalid input quantity or currency code (CCSP_002, CCSP_003)"},
                    "404": {"description": "Exchange rate not available (CCSP_001)"},
                    "503": {"description": "Downstream exchange service unavailable (CCSP_004)"}
                }
            }
        }
    }
}

swagger_bp = create_swagger_blueprint(
    context_path=constants.CONTEXT_PATH,
    openapi_spec=OPENAPI_SPEC,
    title="Currency Conversion Service - Swagger UI"
)
