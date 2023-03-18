"""
Simple client for send big file by chunks.
Use for manual testing Flask's app view FilesLoaderView.

For starting client you can apply command 'poetry run send_file' from project root directory.
For PyCharm also available use 'Run' button.
"""

import requests
from pathlib import Path
from attrs import frozen, field
from typing import Generator
from requests.auth import HTTPBasicAuth
from requests.exceptions import BaseHTTPError, RequestException, CompatJSONDecodeError

from main.settings import Config
from main.logger import logging


TWO_Mb = 2 * 1024 * 1024
logger = logging.getLogger('file_sender_client')


@frozen(slots=True)
class FileSenderClient:
    path_to_file: Path = field(default=None)
    url: str = Config.FILE_SENDER_CLIENT.file_sender_client_socket

    def _read_by_chunks(self, chunk_size=TWO_Mb) -> Generator:
        """Generator to read a file piece by piece."""
        with open(self.path_to_file, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data

    def upload_file(self):
        try:
            res = requests.post(f'{self.url}/files', data=self._read_by_chunks(), auth=HTTPBasicAuth('user', 'password'))
            logger.debug(f'{res.status_code}, {res.json()}')
        except (BaseHTTPError, RequestException, CompatJSONDecodeError) as exc:
            logger.debug(exc)

    def download_file(self):
        try:
            with requests.get(
                    f'{self.url}/files/9a2c9f487988455f6bd918b1154b17225d6054cf43d404c199d1f5beb7f8a192',
                    auth=HTTPBasicAuth('user', 'password'),
                    stream=True
            ) as r:
                r.raise_for_status()
                path_to_file = Path.joinpath(Path(__file__).parent, 'downloaded_from_server.jpg')
                with open(path_to_file, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=TWO_Mb):
                        f.write(chunk)
        except (BaseHTTPError, RequestException, CompatJSONDecodeError) as exc:
            logger.exception(f'{exc.__class__.__name__}. {str(exc)}')

    def delete_file(self):
        try:
            res = requests.delete(
                f'{self.url}/files/9a2c9f487988455f6bd918b1154b17225d6054cf43d404c199d1f5beb7f8a192',
                auth=HTTPBasicAuth('user', 'password'),
            )
            logger.debug(f'{res.status_code}, {res.json()}')
        except (BaseHTTPError, RequestException, CompatJSONDecodeError) as exc:
            logger.exception(f'{exc.__class__.__name__}. {str(exc)}')



def upload_file():
    path_to_file = Path.joinpath(Path(__file__).parent, 'test_data.jpg')
    client = FileSenderClient(path_to_file)
    client.upload_file()


def download_file():
    path_to_file = Path.joinpath(Path(__file__).parent, 'test_data.jpg')
    client = FileSenderClient(path_to_file)
    client.download_file()


def delete_file():
    path_to_file = Path.joinpath(Path(__file__).parent, 'test_data.jpg')
    client = FileSenderClient(path_to_file)
    client.delete_file()
