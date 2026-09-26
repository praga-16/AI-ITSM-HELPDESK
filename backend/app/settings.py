from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root:
# D:\AI-ITSM-HELPDESK\AI-ITSM-HELPDESK
BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):

    # MongoDB
    mongodb_uri: str = ""
    mongodb_db: str = "itsm_helpdesk"

    # ServiceNow
    servicenow_enabled: bool = False
    servicenow_instance: str = ""
    servicenow_username: str = ""
    servicenow_password: str = ""

    # Hugging Face Open-Source LLM
    hf_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    hf_token: str = ""

    # AI confidence
    confidence_threshold: float = 0.75

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()


print("=" * 60)
print("SETTINGS LOADED")
print(f"ENV FILE: {ENV_FILE}")
print(f"HF MODEL: {settings.hf_model}")
print(f"HF TOKEN: {'configured' if settings.hf_token else 'not configured'}")
print("=" * 60)