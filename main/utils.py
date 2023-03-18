from attrs import define, field
import os
import tempfile
import hashlib
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from hashlib import _Hash
    from tempfile import _TemporaryFileWrapper

from main.settings import Config


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
