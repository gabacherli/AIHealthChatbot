import os
from dotenv import load_dotenv
from .constants import Constants

load_dotenv()

class DevConfig:
    def __init__(self):
        constants = Constants()
        self.JWT_SECRET_KEY = os.getenv(constants.DEV_JWT_KEY)
        self.OPENAI_API_KEY = os.getenv(constants.DEV_OPENAI_KEY)
