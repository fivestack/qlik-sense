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

NTLM = 1
SSL = 2


class _Auth:

    def __init__(self, directory: str = None, username: str = None, password: str = None,
                 certificate: str = None, verify: bool = False):
        self._directory = directory
        self._username = username
        self._password = password
        self._certificate = certificate
        self.verify = verify
        if not verify:
            urllib3.disable_warnings()

    @property
    def type(self) -> int:
        if self._certificate:
            return SSL
        elif self._directory and self._username and self._password:
            return NTLM
        else:
            raise AttributeError('Please provide either a certificate or Windows credentials')

    def qlik_user(self) -> str:
        return f'UserDirectory={self._directory}; UserId={self._username}'

    def ntlm_auth(self) -> 'Optional[HttpNtlmAuth]':
        if self.type == NTLM:
            return HttpNtlmAuth(username=f'{self._directory}\\{self._username}', password=self._password)
        return

    def cert(self) -> 'Optional[tuple]':
        if self.type == SSL:
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
        self._set_logger(log_name=log_name, verbosity=verbosity)

        self._log.debug('__SET AUTH')
        self._auth = _Auth(**user, certificate=certificate, verify=verify)

        self._log.debug('__SET BASE URL')
        self._scheme = scheme
        self._host = host
        self._port = port

        self._log.debug('__SET SERVICES')
        self.app = services.AppService(self)
        self.stream = services.StreamService(self)
        self.user = services.UserService(self)

    def _set_logger(self, log_name: str = None, verbosity: int = None):
        """
        Sets up logger for the controller

        Args:
            log_name: name of the log
            verbosity: level of logging, one of [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        """
        if not log_name:
            log_name = 'qlik_sense_api_client'
        if not verbosity:
            verbosity = logging.CRITICAL
        self._log = logging.getLogger(name=log_name)
        self._log.setLevel(verbosity)
        self._log.addHandler(logging.StreamHandler(sys.stdout))

    def _get_url(self, url: str) -> 'Url':
        """
        Builds the url for the request

        Args:
            url: the relative endpoint for the request (e.g. /qrs/app/)

        Returns: the url as a Url object
        """
        return Url(scheme=self._scheme, host=self._host, port=self._port, path=url)

    def _get_params(self, xrf_key: str, params: dict = None) -> dict:
        """
        Builds the query string parameters for the request

        Args:
            xrf_key: the csrf key
            params: the query string parameters for the request

        Returns: the query string parameters as a dictionary
        """
        if not params:
            params = dict()
        params.update({'Xrfkey': xrf_key})
        return params

    def _get_headers(self, xrf_key: str) -> dict:
        """
        Builds the headers for the request

        Args:
            xrf_key: the csrf key

        Returns: the headers as a dictionary

        """
        headers = {
            'X-Qlik-User': self._auth.qlik_user,
            'x-Qlik-Xrfkey': xrf_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers

    def _get_data(self, data: 'Optional[Union[str, list, dict]]' = None) -> 'Optional[str]':
        if not data:
            return None
        if isinstance(data, list) or isinstance(data, dict):
            data = json.dumps(data)
        return data

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
                                   params=self._get_params(xrf_key=xrf_key, params=params),
                                   auth=self._auth.ntlm_auth())
        prepared_request = request.prepare()

        self._log.debug(f'__SEND REQUEST headers={request.headers} <{request.url}>')
        session = requests.Session()
        response = session.send(request=prepared_request,
                                cert=self._auth.cert,
                                verify=self._auth.verify,
                                allow_redirects=False)

        self._log.debug(f'__RESPONSE RECEIVED {response.text}')
        return response
