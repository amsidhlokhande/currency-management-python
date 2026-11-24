"""
Swagger and OpenAPI 3.0 Documentation Routes for Conversion Service.
Mounted strictly under the service context path.
"""
from flask import Blueprint, jsonify
import constants

swagger_bp = Blueprint("swagger", __name__, url_prefix=constants.CONTEXT_PATH)

@swagger_bp.route("/swagger", methods=["GET"])
def swagger_ui():
    """Interactive Swagger/OpenAPI Documentation UI mounted under context path."""
    openapi_url = f"{constants.CONTEXT_PATH}/openapi.json"
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Currency Conversion Service - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5/favicon-32x32.png" sizes="32x32" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = function() {{
        SwaggerUIBundle({{
          url: "{openapi_url}",
          dom_id: '#swagger-ui',
          presets: [SwaggerUIBundle.presets.apis]
        }});
      }};
    </script>
</body>
</html>"""
    return html, 200, {"Content-Type": "text/html"}


@swagger_bp.route("/openapi.json", methods=["GET"])
def openapi_spec():
    """Declarative OpenAPI 3.0.3 specification JSON."""
    spec = {
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
                    "summary": "Calculate converted currency amount",
                    "parameters": [
                        {"name": "from", "in": "path", "required": True, "schema": {"type": "string", "example": "USD"}},
                        {"name": "to", "in": "path", "required": True, "schema": {"type": "string", "example": "INR"}},
                        {"name": "quantity", "in": "path", "required": True, "schema": {"type": "number", "example": 100}}
                    ],
                    "responses": {
                        "200": {"description": "Calculation successful"},
                        "400": {"description": "Validation error (CCSP_002 or CCSP_003)"},
                        "404": {"description": "Rate not found in exchange service (CCSP_001)"},
                        "503": {"description": "Exchange service unavailable / circuit breaker OPEN (CCSP_004)"}
                    }
                }
            },
            "/health": {
                "get": {"summary": "Health actuator endpoint"}
            },
            "/health/liveness": {
                "get": {"summary": "Liveness probe"}
            },
            "/health/readiness": {
                "get": {"summary": "Readiness probe"}
            },
            "/info": {
                "get": {"summary": "Service build metadata & runtime"}
            },
            "/metrics": {
                "get": {"summary": "Service metrics"}
            }
        }
    }
    return jsonify(spec), 200
