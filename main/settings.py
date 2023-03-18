import os
from pathlib import Path

from attr import define, field


Bytes = int
TWO_Mb = 2 * 1024 * 1024


@define(auto_attribs=True, slots=True)
class FileSenderClientConfig:
    host: str = os.getenv('APP_HOST', '127.0.0.1')
    port: int = int(os.getenv('APP_PORT', 5000))
    secure: bool = field(default=None)

    def __attrs_post_init__(self):
        self.secure = self.port == 443

    @property
    def file_sender_client_socket(self) -> str:
        if self.secure:
            return f'https://{self.host}:{self.port}'
        return f'http://{self.host}:{self.port}'


@define(auto_attribs=True, slots=True)
class AppConfig:
    HOST: str = os.getenv('APP_HOST', '127.0.0.1')
    PORT: int = int(os.getenv('APP_PORT', 5000))
    DEBUG: bool = bool(int(os.getenv('DEBUG_MODE', 0)))
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'ERROR').upper()
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'secret_key')
    BASEDIR: Path = Path(__file__).absolute().parent
    STORE_FOLDER_NAME: str = os.getenv('STORE_FOLDER_NAME', 'store')
    FILE_SENDER_CLIENT: FileSenderClientConfig = FileSenderClientConfig()
    SERVER_NAME: str = field(default=None)
    CHUNK_SIZE: Bytes = int(os.getenv('CHUNK_SIZE', TWO_Mb))

    def __attrs_post_init__(self):
        self.SERVER_NAME = f'{self.HOST}:{self.PORT}'

    @property
    def upload_folder(self) -> Path:
        return Path.joinpath(self.BASEDIR.parent, self.STORE_FOLDER_NAME)


Config = AppConfig()
