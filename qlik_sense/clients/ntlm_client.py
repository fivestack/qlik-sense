"""
The Client class is an interface over the QlikSense APIs. The client sets up authentication, logging, and base
settings for interacting with the Qlik Sense APIs. All calls are configured by appropriate lower level services and
then passed up to this class to execute.
"""
import logging
import sys

from requests_ntlm import HttpNtlmAuth
from requests_negotiate_sspi import HttpNegotiateAuth

from qlik_sense.clients import base

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))


class NTLMClient(base.Client):
    """
    An interface over the QlikSense APIs

    Args:
        scheme: http/https
        host: hostname to connect to
        port: port number
        domain: AD domain for the user
        username: the user
        password: the password for the user
    """

    def __init__(self, scheme: str, host: str, port: int = None,
                 domain: str = None, username: str = None, password: str = None):
        super().__init__(scheme=scheme, host=host, port=port)

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
