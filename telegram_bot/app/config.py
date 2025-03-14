from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str

    class Config:
        env_file = ".env"


settings = Settings()  # noqa
