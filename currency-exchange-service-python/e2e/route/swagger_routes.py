"""
Swagger and OpenAPI 3.0 Documentation Routes.
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
    <title>Currency Exchange Service - Swagger UI</title>
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
                        "404": {"description": "Exchange rate not found (CESP_001)"}
                    }
                }
            },
            "/currency-exchange/rates": {
                "get": {
                    "summary": "List all exchange rates in catalog",
                    "responses": {
                        "200": {"description": "Array of exchange rates"}
                    }
                }
            },
            "/currency-exchange/reload": {
                "post": {
                    "summary": "Hot-reload rate dataset from S3 or local CSV",
                    "responses": {
                        "200": {"description": "Reload status"}
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
