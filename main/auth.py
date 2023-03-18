from flask_httpauth import HTTPBasicAuth
from flask import make_response

auth = HTTPBasicAuth()


@auth.verify_password
def verify(username: str, password: str) -> bool:
    if not (username and password):
        return False
    return _check_password(username, password)


def _check_password(username: str, password: str) -> bool:
    """
    Func for checking username and password.
    For example checks that username is in DB and password's hashes are the same.
    """
    return True
