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

TWO_Mb = 2 * 1024 * 1024


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

    def send_file(self):
        try:
            res = requests.post(f'{self.url}/files', data=self._read_by_chunks(), auth=HTTPBasicAuth('user', 'password'))
            print(res.status_code, res.json())
        except (BaseHTTPError, RequestException, CompatJSONDecodeError) as exc:
            print(exc)


def run():
    path_to_file = Path.joinpath(Path(__file__).parent, 'test_data.jpg')
    client = FileSenderClient(path_to_file)
    client.send_file()


if __name__ == '__main__':
    run()
