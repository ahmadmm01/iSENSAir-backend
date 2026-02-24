import paramiko
from app.config import settings


class SFTPClient:

    def connect(self):
        transport = paramiko.Transport(
            (settings.SFTP_HOST, settings.SFTP_PORT)
        )
        transport.connect(
            username=settings.SFTP_USERNAME,
            password=settings.SFTP_PASSWORD
        )

        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp, transport

    def list_files(self):
        sftp, transport = self.connect()
        files = sftp.listdir_attr(settings.SFTP_PATH)
        sftp.close()
        transport.close()
        return files

    def download_file(self, filename: str, local_path: str):
        sftp, transport = self.connect()
        remote_file = f"{settings.SFTP_PATH}/{filename}"
        sftp.get(remote_file, local_path)
        sftp.close()
        transport.close()