"""
The Client class is an interface over the QlikSense APIs. The client sets up authentication, logging, and base
settings for interacting with the Qlik Sense APIs. All calls are configured by appropriate lower level services and
then passed up to this class to execute.
"""
import os.path
import random
import string
from typing import Optional, Union

import urllib3
import requests

from qlik_sense.clients import client


class SSLClient(client.Client):
    """
    An interface over the QlikSense APIs that uses SSL authentication

    Args:
        scheme: http/https
        host: hostname to connect to
        port: port number
        certificate: path to .pem client certificate
        verify: false to trust in self-signed certificates
        log_name: logger instance name
        verbosity: level of logging, one of [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    """

    def __init__(self,
                 scheme: str, host: str, port: int,
                 certificate: str = None, verify: bool = False,
                 log_name: str = None, verbosity: int = None):
        super().__init__(scheme=scheme, host=host, port=port, log_name=log_name, verbosity=verbosity)
        self._log.debug('__SET AUTH')
        self._set_ssl_auth(certificate=certificate, verify=verify)

    def _set_ssl_auth(self, certificate: str, verify: bool = False):
        """
        Sets up SSL authentication

        Args:
            certificate: path to .pem client certificate
            verify: false to trust in self-signed certificates
        """
        (base, ext) = os.path.splitext(certificate)
        self._cert = f'{base}{ext}', f'{base}_key{ext}'
        self._verify = verify
        if not verify:
            urllib3.disable_warnings()

    def call(self, method: str, url: str, params: 'Optional[dict]' = None,
             data: 'Optional[Union[str, list, dict]]' = None) -> 'requests.Response':
        """
        All requests are routed through this method

        Args:
            method: REST method, one of ['GET', 'POST', 'PUT', 'DELETE']
            url: the relative endpoint for the request (e.g. /qrs/app/)
            params: the query string parameters for the request
            data: data to be inserted in the body of the request

        Returns: a Response object
        """
        self._log.info(f'API CALL {method} <{url}> params={params} data={len(data) if data else None}')

        self._log.debug(f'__PREPARE REQUEST')
        xrf_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        request = requests.Request(method=method,
                                   url=self._get_url(url=url),
                                   headers=self._get_headers(xrf_key=xrf_key),
                                   data=self._get_data(data),
                                   params=self._get_params(xrf_key=xrf_key, params=params))
        prepared_request = request.prepare()

        self._log.debug(f'__SEND REQUEST headers={request.headers} <{request.url}>')
        session = requests.Session()
        response = session.send(request=prepared_request,
                                cert=self._cert,
                                verify=self._verify,
                                allow_redirects=False)

        self._log.debug(f'__RESPONSE RECEIVED {response.text}')
        return response
