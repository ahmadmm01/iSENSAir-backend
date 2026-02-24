import paramiko
from app.config import settings


class SFTPClient:

    def connect(self):
        transport = paramiko.Transport((settings.SFTP_HOST, settings.SFTP_PORT))
        transport.connect(
            username=settings.SFTP_USERNAME, password=settings.SFTP_PASSWORD
        )

        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp, transport

    def list_files(self, location: str):

        if location not in settings.LOCATIONS:
            raise ValueError("Invalid location")

        path = settings.LOCATIONS[location]["path"]

        sftp, transport = self.connect()
        files = sftp.listdir_attr(path)
        sftp.close()
        transport.close()

        return files

    def download_file(self, location: str, filename: str, local_path: str):

        if location not in settings.LOCATIONS:
            raise ValueError("Invalid location")

        path = settings.LOCATIONS[location]["path"]
        remote_file = f"{path}/{filename}"

        sftp, transport = self.connect()
        sftp.get(remote_file, local_path)
        sftp.close()
        transport.close()
