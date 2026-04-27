from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_BASE_URL: str
    GITHUB_CLIENT_ID: str
    GITHUB_AUTHORIZE_URL: str = "https://github.com/login/oauth/authorize"
    GITHUB_USER_URL: str = "https://api.github.com/user"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


settings = Settings()
