import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")

    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))

    USER_AGENT = os.getenv("USER_AGENT")

    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

    DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

    MAX_CONSECUTIVE_FAILURES = int(os.getenv("MAX_CONSECUTIVE_FAILURES", 5))

config = Config()