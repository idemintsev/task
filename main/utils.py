from attrs import define, field
import os
import tempfile
import hashlib
from typing import TYPE_CHECKING
from pathlib import Path
import shutil

if TYPE_CHECKING:
    from hashlib import _Hash
    from tempfile import _TemporaryFileWrapper

from main.settings import Config
from main.logger import logging

logger = logging.getLogger('flask_app')


@define(auto_attribs=True, slots=True)
class FileContextManager:
    path: Path = Config.upload_folder
    mode: str = 'ab'
    username: str = field(default=None)  # type: ignore
    temp_file: '_TemporaryFileWrapper' = field(default=None)  # type: ignore
    filename: str = field(default=None)  # type: ignore
    hash_object: '_Hash' = field(default=None)  # type: ignore

    def __attrs_post_init__(self):
        self.hash_object = hashlib.new('sha256')

    @property
    def full_path_to_creating_file(self) -> str | None:
        if self.filename:
            return f'{Path.joinpath(Path(self.path), self.filename[0:2], self.filename)}'

    def __enter__(self) -> 'FileContextManager':
        self.temp_file = tempfile.NamedTemporaryFile(mode=self.mode, delete=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temp_file.close()
        if exc_type is None:
            self.filename = self.hash_object.hexdigest()
            path = Path.joinpath(Config.upload_folder, self.filename[0:2])
            path.mkdir(parents=True, exist_ok=True)
            os.replace(self.temp_file.name, f'{self.full_path_to_creating_file}.{self.username}')
        else:
            os.unlink(self.temp_file.name)


def upload_file_to_server(request, username: str) -> str:
    try:
        with FileContextManager(
                temp_file=f"{Path.joinpath(Config.upload_folder, 'tmp')}", username=username
        ) as f_manager:
            while True:
                chunk = request.stream.read(Config.CHUNK_SIZE)
                if not chunk:
                    break
                f_manager.temp_file.write(chunk)
                f_manager.hash_object.update(chunk)
        return f_manager.filename
    except Exception as exc:
        logger.exception(f'Uploading file: {exc.__class__.__name__, str(exc)}')
        return ''


def download_file_from_server(filename: str) -> str:
    path_to_file = Path.joinpath(Config.upload_folder, filename[0:2], filename)
    logger.debug(f'Path to downloading file: {path_to_file}')
    if path_to_file.parent.is_dir():
        files = [f for f in path_to_file.parent.iterdir() if f.is_file()]
        file = [f for f in files if f.name.startswith(filename)]
        if file:
            return file[0]
    return ''


def delete_file_from_server(filename: str, username: str) -> str:
    path_to_file = Path.joinpath(Config.upload_folder, filename[0:2], f'{filename}.{username}')
    logger.debug(f'Path to deleting file: {path_to_file}')
    if path_to_file.is_file():
        try:
            files_quantity = sum(1 for f in path_to_file.parent.iterdir() if f.is_file())
            if files_quantity > 1:
                path_to_file.unlink()
            else:
                shutil.rmtree(path_to_file.parent)
            return filename
        except FileNotFoundError as exc:
            logger.exception(f'Deleting file: {exc.__class__.__name__}. {str(exc)}')
    return ''
