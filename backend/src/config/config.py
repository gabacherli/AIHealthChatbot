import os

from dotenv import load_dotenv
from .constants import Constants
from .dev_config import DevConfig
from .prod_config import ProdConfig

load_dotenv()

class Config:
    def __init__(self):
        constants = Constants()
        
        env = os.getenv("ENV")
        if env == constants.ENV_PRODUCTION:
            envConfig = ProdConfig()
        else:
            envConfig = DevConfig()
        
        self.ENV = env
        self.JWT_SECRET_KEY = envConfig.JWT_SECRET_KEY
        self.OPENAI_API_KEY = envConfig.OPENAI_API_KEY
        self.MODEL_NAME = constants.DEFAULT_MODEL_NAME
        self.EMBEDDING_MODEL =  constants.DEFAULT_EMBEDDING_MODEL
        self.CHUNK_DATA_PATH =  constants.DEFAULT_CHUNK_PATH
