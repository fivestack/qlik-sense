import logging
import sys
import os.path

import urllib3

from qlik_sense.clients import base

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))


class SSLClient(base.Client):
    """
    An interface over the QlikSense QRS API that uses SSL authentication. You can obtain a certificate using the QS Hub
    and save it on the local machine. By default, this certificate grants you sysadmin on the server. If you want to
    restrict privileges, use `directory` and `user` to execute calls as that user.

    Args:
        host: hostname to connect to
        port: port number, defaults to 4242
        scheme: http/https, defaults to https
        certificate: path to .pem client certificate
        verify: false to trust in self-signed certificates
        directory: directory for the user
        user: user, in lieu of admin, whose permissions should be used to execute the request
    """
    _qlik_user = None

    def __init__(self, host: str, port: int = 4242, scheme: str = 'https',
                 certificate: str = None, verify: bool = False,
                 directory: str = None, user: str = None):
        super().__init__(host=host, port=port, scheme=scheme)

        _logger.debug('__SET SSL AUTH')
        path, ext = os.path.splitext(certificate)
        self._cert = f'{path}{ext}', f'{path}_key{ext}'
        self._verify = verify
        if not verify:
            urllib3.disable_warnings()

        _logger.debug(f'__SET USER directory={directory} user={user}')
        if not directory and not user:
            directory = 'internal'
            user = 'sa_repository'
        self._qlik_user = f'UserDirectory={directory};UserId={user}'

    def _get_headers(self, xrf_key: str) -> dict:
        """
        Gets the default headers that all requests need (including Xrfkey) and adds in headers that SSL
        authentication uses, such as a user to run as.

        Args:
            xrf_key: the csrf key

        Returns: the headers for the request as a dictionary
        """
        headers = super()._get_headers(xrf_key=xrf_key)
        headers.update({'X-Qlik-User': self._qlik_user})
        return headers
