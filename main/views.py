from flask import request, make_response
from flask.views import MethodView
from main.auth import auth

from flask.wrappers import Response
from pathlib import Path

from main.settings import Config
from main.utils import FileContextManager


class FilesLoaderView(MethodView):
    """View for loading file from request to folder 'store'."""
    # init_every_request = False

    @auth.login_required
    def post(self) -> Response:
        username = request.authorization.get('username')
        with FileContextManager(temp_file=f"{Path.joinpath(Config.upload_folder, 'tmp')}") as f_manager:
            chunk_size = 1024
            while True:
                chunk = request.stream.read(chunk_size)
                if not chunk:
                    break
                f_manager.temp_file.write(chunk)
                f_manager.hash_object.update(chunk)
        return make_response({'filename': f_manager.filename}, 201)
