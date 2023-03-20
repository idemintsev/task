from flask import request, make_response, stream_with_context
from flask.views import MethodView
from main.auth import auth
from typing import Generator
import shutil
from flask.wrappers import Response
from pathlib import Path

from main.settings import Config
from main.utils import upload_file_to_server, download_file_from_server, delete_file_from_server

from main.logger import logging

logger = logging.getLogger('flask_app')


class FileUploadView(MethodView):
    """View for upload file from client to server by chunks."""
    init_every_request = False

    @auth.login_required
    def post(self) -> Response:
        username = request.authorization.get('username')
        logger.debug(f'FileDownloadView. Username: {username}')
        filename = upload_file_to_server(request, username)
        if filename:
            return make_response({'filename': filename}, 201)
        return make_response({'status': 'error'}, 400)


class FileManagerView(MethodView):
    """View for send files from server to client by chunks and delete files."""
    init_every_request = False

    @auth.login_required
    def get(self, id: str) -> Response:
        """"""
        username = request.authorization.get('username')
        logger.debug(f'FileManagerView, downloading by {username}')
        file = download_file_from_server(id)
        if file:
            return Response(
                stream_with_context(self._read_file_by_chunks(file)),
                content_type='application/octet-stream',
            )
        return make_response({'filename': 'notfound'}, 404)

    def delete(self, id: str) -> Response:
        username = request.authorization.get('username')
        logger.debug(f'FileManagerView, deleting by {username}')
        result = delete_file_from_server(id, username)
        if result:
            return make_response({'Deleted filename': result}, 200)
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
