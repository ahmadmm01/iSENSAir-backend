import os
from dotenv import load_dotenv

load_dotenv(".env.local")


class Settings:
    SFTP_HOST = os.getenv("SFTP_HOST")
    SFTP_PORT = int(os.getenv("SFTP_PORT", 22))
    SFTP_USERNAME = os.getenv("SFTP_USERNAME")
    SFTP_PASSWORD = os.getenv("SFTP_PASSWORD")

    # Konfigurasi lokasi
    LOCATIONS = {
        "semantan": {
            "path": "/root/BKSA_Semantan/Data Logger",
            "prefix": "SemantanDataLogger_",
        },
        "kechau": {
            "path": "/root/BKSA_Kechau/Data Logger",
            "prefix": "KechauDataLogger_"},
        "bilut": {
            "path": "/root/BKSA_Bilut/Data Logger",
            "prefix": "BilutDataLogger_"
        }

    }


settings = Settings()
