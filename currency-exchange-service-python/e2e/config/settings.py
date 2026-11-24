"""
Settings Module for Currency Exchange Service.
Integrates constants and Flask configuration attributes.
"""
import constants

class Settings:
    SERVICE_NAME = constants.SERVICE_NAME
    PORT = constants.PORT
    ENV = constants.ENV
    LOG_LEVEL = constants.LOG_LEVEL
    CONTEXT_PATH = constants.CONTEXT_PATH
    RATES_CSV_PATH = constants.RATES_CSV_PATH
    AWS_REGION = constants.AWS_REGION
    AWS_ACCESS_KEY_ID = constants.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = constants.AWS_SECRET_ACCESS_KEY
