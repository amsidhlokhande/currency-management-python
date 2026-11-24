"""
Settings Module for Currency Conversion Service.
Integrates constants and Flask configuration attributes.
"""
import constants

class Settings:
    SERVICE_NAME = constants.SERVICE_NAME
    PORT = constants.PORT
    ENV = constants.ENV
    LOG_LEVEL = constants.LOG_LEVEL
    CONTEXT_PATH = constants.CONTEXT_PATH
    EXCHANGE_SERVICE_URL = constants.EXCHANGE_SERVICE_URL
    HTTP_TIMEOUT_CONNECT = constants.HTTP_TIMEOUT_CONNECT
    HTTP_TIMEOUT_READ = constants.HTTP_TIMEOUT_READ
    HTTP_MAX_RETRIES = constants.HTTP_MAX_RETRIES
    GCP_OIDC_AUTH = constants.GCP_OIDC_AUTH
