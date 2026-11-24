"""
Centralized Error Handler for Currency Conversion Service.
Delegates to the shared enterprise_core centralized error handling engine.
"""
from flask import Flask
from enterprise_core import register_centralized_error_handlers
import constants

def register_error_handlers(app: Flask):
    """
    Registers the enterprise centralized error handler configured with
    CCSP default error taxonomy.
    """
    register_centralized_error_handlers(
        app=app,
        default_internal_error_code=constants.CCSP_ERR_INTERNAL_SERVER_CODE,
        default_internal_error_msg=constants.CCSP_ERR_INTERNAL_SERVER_MSG
    )
