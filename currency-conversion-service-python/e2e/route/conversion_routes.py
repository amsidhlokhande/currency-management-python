"""
Currency Conversion API Business Routes.
Mounted strictly under the service context path.
"""
from flask import Blueprint, jsonify
import constants
from e2e.service.conversion_service import conversion_service

conversion_bp = Blueprint("currency_conversion", __name__, url_prefix=constants.CONTEXT_PATH)

@conversion_bp.route("/currency-conversion/from/<from_curr>/to/<to_curr>/quantity/<quantity_str>", methods=["GET"])
def convert_currency(from_curr: str, to_curr: str, quantity_str: str):
    """
    Calculate converted currency amount based on live rate from currency-exchange-service-python.
    Mounted under context path: /currency-conversion-service-python/currency-conversion/from/{from}/to/{to}/quantity/{quantity}
    """
    result = conversion_service.calculate_conversion(from_curr, to_curr, quantity_str)
    return jsonify(result.to_dict()), 200
