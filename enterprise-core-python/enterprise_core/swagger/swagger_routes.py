"""
Enterprise Swagger and OpenAPI 3.0 Documentation Routes Blueprint Factory.
Mounted strictly under the service context path.
"""
from typing import Dict, Any
from flask import Blueprint, jsonify

def create_swagger_blueprint(
    context_path: str,
    openapi_spec: Dict[str, Any],
    title: str = "Enterprise Microservice - Swagger UI"
) -> Blueprint:
    """
    Factory function creating an enterprise Swagger UI & OpenAPI Blueprint mounted under context_path.
    
    Endpoints provided:
    - GET {context_path}/swagger     -> Interactive Swagger UI HTML
    - GET {context_path}/openapi.json -> OpenAPI 3.0.3 specification JSON
    """
    bp = Blueprint("enterprise_swagger", __name__, url_prefix=context_path)
    openapi_url = f"{context_path}/openapi.json"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
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

    @bp.route("/swagger", methods=["GET"])
    def swagger_ui():
        """Interactive Swagger UI HTML page."""
        return html, 200, {"Content-Type": "text/html"}

    @bp.route("/openapi.json", methods=["GET"])
    def serve_openapi_spec():
        """OpenAPI 3.0 specification JSON."""
        return jsonify(openapi_spec), 200

    return bp
