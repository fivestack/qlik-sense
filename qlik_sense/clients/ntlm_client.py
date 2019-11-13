import logging
import sys

from requests_ntlm import HttpNtlmAuth
from requests_negotiate_sspi import HttpNegotiateAuth

from qlik_sense.clients import base

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))


class NTLMClient(base.Client):
    """
    An interface over the QlikSense QRS API that uses Windows AD authentication. You can pass in an AD domain, user
    name, and password to explicitly execute calls as a specific user. Alternatively, you can provide none of these
    arguments and the current Windows user will be used via SSPI authentication.

    Args:
        host: hostname to connect to
        port: port number
        scheme: http/https, defaults to https
        domain: AD domain for the user
        username: the user
        password: the password for the user
    """

    def __init__(self, host: str, port: int = None, scheme: str = 'https',
                 domain: str = None, username: str = None, password: str = None):
        super().__init__(host=host, port=port, scheme=scheme)

        if domain and username and password:
            _logger.debug('__SET NTLM AUTH')
            self._auth = HttpNtlmAuth(username=f'{domain}\\{username}', password=password)
        else:
            _logger.debug('__SET NTLM SSPI AUTH')
            self._auth = HttpNegotiateAuth()

    def _get_headers(self, xrf_key: str) -> dict:
        """
        Gets the default headers that all requests need (including Xrfkey) and adds in headers that NTLM
        authentication uses, such as a Windows user agent.

        Args:
            xrf_key: the csrf key

        Returns: the headers for the request as a dictionary
        """
        headers = super()._get_headers(xrf_key=xrf_key)
        headers.update({'User-Agent': 'Windows'})
        return headers
