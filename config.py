import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    # LLM Settings - Support both Groq and OpenAI
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # API Keys
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

    # Application Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

    # API Endpoints
    WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
    GITHUB_API_URL = "https://api.github.com"

    # LLM Temperature
    PLANNER_TEMPERATURE = 0.1
    VERIFIER_TEMPERATURE = 0.1

    @classmethod
    def get_llm_provider(cls):
        """Determine which LLM provider to use"""
        if cls.GROQ_API_KEY:
            return "groq", cls.GROQ_MODEL
        else:
            return None, None

    @classmethod
    def validate(cls):
        """Validate that all required keys are present"""
        errors = []

        # Check for at least one LLM provider
        if not cls.GROQ_API_KEY:
            errors.append("Either GROQ_API_KEY or OPENAI_API_KEY must be set")

        if cls.GROQ_API_KEY:
            print(f"Groq API key found (model: {cls.GROQ_MODEL})")

        # Check other required APIs
        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN is missing")
        else:
            print(" GitHub token found")

        if not cls.WEATHER_API_KEY:
            errors.append("WEATHER_API_KEY is missing")
        else:
            print(" Weather API key found")

        if errors:
            print("\n Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            return False

        print(" All configurations validated successfully!")
        return True


# Validate on import
Config.validate()