import os
from dotenv import load_dotenv

load_dotenv(".env.local")

class Settings:
    SFTP_HOST = os.getenv("SFTP_HOST")
    SFTP_PORT = int(os.getenv("SFTP_PORT", 22))
    SFTP_USERNAME = os.getenv("SFTP_USERNAME")
    SFTP_PASSWORD = os.getenv("SFTP_PASSWORD")
    SFTP_PATH = os.getenv("SFTP_PATH")

settings = Settings()