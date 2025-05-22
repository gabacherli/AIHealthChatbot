class Constants:
    def __init__(self):
        self.ENV_PRODUCTION = "production"
        self.ENV_DEVELOPMENT = "development"
        self.DEFAULT_MODEL_NAME = "gpt-4o-mini"
        self.DEFAULT_EMBEDDING_MODEL = "multi-qa-MiniLM-L6-cos-v1" # TODO: Review model
        self.DEFAULT_CHUNK_PATH = "data/"
        # Environment-specific variables
        # Dev
        self.DEV_JWT_KEY = "DEV_JWT_KEY"
        self.DEV_OPENAI_KEY = "DEV_OPENAI_KEY"
        # Prod
        self.PROD_JWT_KEY = "PROD_JWT_KEY"
        self.PROD_OPENAI_KEY = "PROD_OPENAI_KEY"