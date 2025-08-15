import os
from dotenv import load_dotenv
from utils.custom_exception import ConfigError

# Load environment variables
load_dotenv()

class Config:
    """
    Secure configuration manager with validation
    """
    # Model Constants
    GROQ_MODEL = "mixtral-8x7b-32768"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    @staticmethod
    def get_groq_key() -> str:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ConfigError("GROQ_API_KEY not found in environment variables")
        if key.startswith(("---", "xxx", "your_")):
            raise ConfigError("GROQ_API_KEY appears to be a placeholder value")
        return key

    @staticmethod
    def get_huggingface_key() -> str:
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not token:
            raise ConfigError("HUGGINGFACEHUB_API_TOKEN not found in environment variables")
        if token.startswith(("---", "xxx", "your_")):
            raise ConfigError("HUGGINGFACEHUB_API_TOKEN appears to be a placeholder value")
        return token

    @staticmethod
    def validate() -> bool:
        try:
            return all([
                Config.get_groq_key(),
                Config.get_huggingface_key()
            ])
        except ConfigError:
            return False

# Legacy variables for backward compatibility
GROQ_API_KEY = Config.get_groq_key()
HUGGINGFACEHUB_API_TOKEN = Config.get_huggingface_key()
HUGGINGFACE_MODEL = Config.EMBEDDING_MODEL
MODEL_NAME = Config.GROQ_MODEL
