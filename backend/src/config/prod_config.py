import os
from dotenv import load_dotenv
from .constants import Constants

load_dotenv()

class ProdConfig:
    def __init__(self):
        constants = Constants()
        self.JWT_SECRET_KEY = os.getenv(constants.PROD_JWT_KEY)
        self.OPENAI_API_KEY = os.getenv(constants.PROD_OPENAI_KEY)
