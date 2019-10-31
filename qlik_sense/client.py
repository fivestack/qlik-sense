"""
The Client class is an interface over the QlikSense APIs. The client sets up authentication, logging, and base
settings for interacting with the Qlik Sense APIs. All calls are configured by appropriate lower level services and
then passed up to this class to execute.
"""
import logging
import sys
import os.path
import random
import string
from typing import Optional, Union
import json

import urllib3
from urllib3.util import Url
import requests
from requests_ntlm import HttpNtlmAuth

from qlik_sense import services


class _Auth:

    def __init__(self, directory: str = None, username: str = None, password: str = None,
                 certificate: str = None, verify: bool = False):
        self._directory = directory
        self._username = username
        self._password = password
        self._certificate = certificate
        self.verify = verify

    def qlik_user(self) -> str:
        return f'UserDirectory={self._directory}; UserId={self._username}'

    def ntlm_auth(self) -> 'Optional[HttpNtlmAuth]':
        if self._directory and self._username and self._password:
            return HttpNtlmAuth(username=f'{self._directory}\\{self._username}', password=self._password)
        return

    def cert(self) -> 'Optional[tuple]':
        if self._certificate:
            (base, ext) = os.path.splitext(self._certificate)
            return f'{base}{ext}', f'{base}_key{ext}'
        return


class Client:
    """
    An interface over the QlikSense APIs

    Args:
        scheme: http/https
        host: hostname to connect to
        port: port number
        certificate: path to .pem client certificate
        user: dict with keys {directory, username, password}
        verify: false to trust in self-signed certificates
        log_name: logger instance name
        verbosity: level of logging, one of [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    """

    _log = None

    def __init__(self,
                 scheme: str, host: str, port: int,
                 user: dict = None, certificate: str = None, verify: bool = False,
                 log_name: str = None, verbosity: int = None):
        if log_name:
            self._set_logger(log_name=log_name, verbosity=verbosity)
        self._log.debug('__SET LOGGING DONE')

        self._log.debug('__SET AUTH')
        self._auth = _Auth(**user, certificate=certificate, verify=verify)

        if not self._auth.verify:
            self._log.debug('__DISABLED WARNINGS')
            urllib3.disable_warnings()

        self._log.debug('__SET BASE URL')
        self._scheme = scheme
        self._host = host
        self._port = port

        self._log.debug('__SET SERVICES')
        self.app = services.AppService(self)

    def _set_logger(self, log_name: str, verbosity: int):
        """
        Sets up logger for the controller

        Args:
            log_name: name of the log
            verbosity: level of logging, one of [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        """
        self._log = logging.getLogger(name=log_name)
        self._log.setLevel(verbosity)
        self._log.addHandler(logging.StreamHandler(sys.stdout))

    def _prepare_request(self, method: str, url: str, params: dict, data: str) -> 'requests.Request':
        """
        Builds the url, url parameters, and headers for the request

        Args:
            method: REST method, one of ['GET', 'POST', 'PUT', 'DELETE']
            url: the starting url
            params: the starting url parameters
            data: data to be inserted in the body of the request

        Returns: a tuple with the updated url, url parameters, and headers
        """
        xrf_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

        url = Url(scheme=self._scheme, host=self._host, port=self._port, path=url)
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) qsAPI APIREST (QSense)',
            'Pragma': 'no-cache',
            'X-Qlik-User': self._auth.qlik_user,
            'x-Qlik-Xrfkey': xrf_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        request = requests.Request(method=method,
                                   url=url,
                                   headers=headers,
                                   data=data,
                                   params=params.update({'Xrfkey': xrf_key}),
                                   auth=self._auth.ntlm_auth())
        return request

    def call(self, method: str, url: str, params: 'Optional[dict]' = None,
             data: 'Optional[Union[str, list, dict]]' = None) -> 'requests.Response':
        """
        All requests are routed through this method.

        Args:
            method: REST method, one of ['GET', 'POST', 'PUT', 'DELETE']
            url: the endpoint for the request
            params: the url parameters for the request
            data: data to be inserted in the body of the request

        Returns: a Response object
        """
        self._log.info(f'API CALL {method} <{url}> params={params} data={len(data) if data else None}')

        self._log.debug(f'__PREPARE REQUEST')
        if not params:
            params = dict()
        if isinstance(data, list) or isinstance(data, dict):
            data = json.dumps(data)
        request = self._prepare_request(method=method, url=url, data=data, params=params)

        self._log.debug(f'__SEND REQUEST headers={request.headers} <{request.url}>')
        session = requests.Session()
        prepared_request = session.prepare_request(request)
        response = session.send(request=prepared_request,
                                cert=self._auth.cert,
                                verify=self._auth.verify,
                                allow_redirects=False)

        self._log.debug(f'__RECEIVED {response.text}')
        return response
