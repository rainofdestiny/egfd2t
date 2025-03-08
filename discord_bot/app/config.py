from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    discord_bot_token: str
    discord_channel_id: int
    discord_server_id: int
    telegram_bot_service_url: str

    class Config:
        env_file = ".env"


settings = Settings()  # noqa
