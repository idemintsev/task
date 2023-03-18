from flask import request, make_response, stream_with_context
from flask.views import MethodView
from main.auth import auth
from typing import Generator
import shutil
from flask.wrappers import Response
from pathlib import Path

from main.settings import Config
from main.utils import FileContextManager

from main.logger import logging

logger = logging.getLogger('flask_app')


class FileUploadView(MethodView):
    """View for upload file from client to server by chunks."""
    init_every_request = False

    @auth.login_required
    def post(self) -> Response:
        username = request.authorization.get('username')
        logger.debug(f'FileDownloadView. Username: {username}')
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
            return make_response({'filename': f_manager.filename}, 201)
        except Exception as exc:
            logger.exception(f'FileDownloadView. {exc.__class__.__name__, str(exc)}')
            return make_response({'status': 'error'}, 400)


class FileDownloadView(MethodView):
    """View for send files from server to client by chunks and delete files."""
    init_every_request = False

    @auth.login_required
    def get(self, id: str) -> Response:
        """"""
        username = request.authorization.get('username')
        path_to_file = Path.joinpath(Config.upload_folder, id[0:2], f'{id}')
        logger.debug(f'FileUploadView. Username: {username}')
        logger.debug(f'FileUploadView. Path_to_file: {path_to_file}')

        if path_to_file.parent.is_dir():
            files = [f for f in path_to_file.parent.iterdir() if f.is_file()]
            file = [f for f in files if f.name.startswith(id)]
            if file:
                return Response(
                    stream_with_context(self._read_file_by_chunks(*file)),
                    content_type='application/octet-stream',
                )
        return make_response({'filename': 'notfound'}, 404)

    def delete(self, id: str) -> Response:
        username = request.authorization.get('username')
        path_to_file = Path.joinpath(Config.upload_folder, id[0:2], f'{id}.{username}')
        logger.debug(f'FileUploadView. Username: {username}')
        logger.debug(f'FileUploadView. Path_to_file: {path_to_file}')
        if not path_to_file.is_file():
            return make_response({'filename': 'file not found'}, 404)
        try:
            files_quantity = sum(1 for f in path_to_file.parent.iterdir() if f.is_file())
            if files_quantity > 1:
                path_to_file.unlink(path_to_file)
            else:
                shutil.rmtree(path_to_file.parent)
            return make_response({'deleted': id}, 200)
        except FileNotFoundError as exc:
            logger.exception(f'{exc.__class__.__name__}. {str(exc)}')
            return make_response({'filename': 'file not found'}, 404)

    @staticmethod
    def _read_file_by_chunks(path: Path) -> Generator:
        """Generator to read a file piece by piece."""
        with open(str(path), 'rb') as f:
            while True:
                data = f.read(Config.CHUNK_SIZE)
                if not data:
                    break
                yield data
