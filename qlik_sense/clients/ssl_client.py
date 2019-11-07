"""
The Client class is an interface over the QlikSense APIs. The client sets up authentication, logging, and base
settings for interacting with the Qlik Sense APIs. All calls are configured by appropriate lower level services and
then passed up to this class to execute.
"""
import logging
import sys
import os.path

import urllib3

from qlik_sense.clients import base

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))


class SSLClient(base.Client):
    """
    An interface over the QlikSense APIs that uses SSL authentication

    Args:
        scheme: http/https
        host: hostname to connect to
        port: port number, defaults to 4242
        certificate: path to .pem client certificate
        verify: false to trust in self-signed certificates
        directory: directory for the user
        user: user, in lieu of admin, whose permissions should be used to execute the request
    """
    _qlik_user = None

    def __init__(self, scheme: str, host: str, port: int = 4242,
                 certificate: str = None, verify: bool = False,
                 directory: str = None, user: str = None):
        super().__init__(scheme=scheme, host=host, port=port)

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
        if self._qlik_user:
            headers.update({'X-Qlik-User': self._qlik_user})
        return headers
