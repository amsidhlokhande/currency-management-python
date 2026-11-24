"""
Currency Exchange API Business Routes.
Mounted strictly under the service context path.
"""
from flask import Blueprint, jsonify
import constants
from e2e.service.rate_service import rate_service

# Define Blueprint with context path prefix
exchange_bp = Blueprint("currency_exchange", __name__, url_prefix=constants.CONTEXT_PATH)

@exchange_bp.route("/currency-exchange/from/<from_curr>/to/<to_curr>", methods=["GET"])
def get_exchange_rate(from_curr: str, to_curr: str):
    """
    Retrieve live currency conversion rate for a given currency pair.
    Mounted under context path: /currency-exchange-service-python/currency-exchange/from/{from}/to/{to}
    """
    rate = rate_service.get_rate(from_curr, to_curr)
    return jsonify(rate.to_dict()), 200


@exchange_bp.route("/currency-exchange/rates", methods=["GET"])
def get_all_rates():
    """
    Retrieve all supported currency exchange rates in the catalog.
    Mounted under context path: /currency-exchange-service-python/currency-exchange/rates
    """
    rates = rate_service.get_all_rates()
    return jsonify([r.to_dict() for r in rates]), 200


@exchange_bp.route("/currency-exchange/reload", methods=["POST"])
def reload_rates():
    """
    Hot reload exchange rates from configured S3 bucket or local Windows CSV.
    Mounted under context path: /currency-exchange-service-python/currency-exchange/reload
    """
    count = rate_service.reload()
    return jsonify({
        "message": "Exchange rates reloaded successfully",
        "totalPairs": count,
        "source": rate_service.data_source
    }), 200
