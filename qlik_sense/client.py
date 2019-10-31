"""
The Client class is an interface over the QlikSense APIs. The client sets up authentication, logging, and base
settings for interacting with the Qlik Sense APIs. All calls are configured by appropriate lower level services and
then passed up to this class to execute.
"""
import logging
import sys
import os.path
import urllib.parse
import random
import string

import urllib3
import requests
from requests_ntlm import HttpNtlmAuth

from qlik_sense import services


class Client:
    """
    An interface over the QlikSense APIs

    Args:
        schema: http/https
        host: hostname to connect to
        port: port number
        certificate: path to .pem client certificate
        user: dict with keys {directory, username, password}
        verify: false to trust in self-signed certificates
        log_name: logger instance name
        verbosity: level of logging, one of [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    """

    _referer = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) qsAPI APIREST (QSense)'
    _session = None
    _cert = None
    _verify = False
    _qlik_user = None

    def __init__(self,
                 schema: str, host: str, port: int,
                 certificate: str = None, user: dict = None, verify: bool = False,
                 log_name: str = None, verbosity: int = None):
        if log_name:
            self._set_logger(log_name=log_name, verbosity=verbosity)
        self._baseurl = f'{schema}://{host}:{str(port)}'
        self._session = requests.Session()
        self._set_auth(certificate=certificate, user=user)
        self._verify = verify
        if not self._verify:
            urllib3.disable_warnings()

        self.app = services.AppService(self)

    def _set_logger(self, log_name: str, verbosity: int):
        """
        Sets up logger for the controller

        Args:
            log_name: name of the log
            verbosity: level of logging, one of [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        """
        self._log = logging.getLogger(log_name)
        if not self._log.hasHandlers():
            self._log.addHandler(logging.StreamHandler(sys.stdout))
        self._log.setLevel(verbosity)
        self._log.info('SET LOGGER')

    def _set_auth(self, certificate: str, user: dict):
        """
        Sets up authentication for the controller. Routes based on whether a certificate or a user was provided

        Args:
            certificate: path to .pem client certificate
            user: a dictionary with user credentials, in the form {'directory': '', 'username': '', 'password': ''}
        """
        self._log.debug(f'__SET AUTH')
        if certificate and user:
            self._log.info('INVALID authentication provided')
            raise AttributeError('Provide only one of certificate (for PEM) and user (for NTLM)')
        elif user:
            self._log.info('NTLM authentication enabled')
        elif certificate:
            self._log.info('PEM authentication enabled')
            self._set_cert(certificate=certificate)
            user = {'directory': None, 'username': None, 'password': None}
        else:
            self._log.info('NO authentication enabled')
            user = {'directory': None, 'username': None, 'password': None}
        self._set_user(user=user)

    def _set_cert(self, certificate: str):
        """
        Sets up PEM authentication for the controller

        Args:
            certificate: path to .pem client certificate
        """
        self._log.debug(f'__SET CERTIFICATE certificate={certificate}')
        (base, ext) = os.path.splitext(certificate)
        self._cert = (base + ext, base + '_key' + ext)
        self._log.debug(f'CERTKEY: {base}.{ext}')

    def _set_user(self, user: dict):
        """
        Sets up NTLM authentication for the controller

        Args:
            user: a dictionary with user credentials, in the form {'directory': '', 'username': '', 'password': ''}
        """
        self._log.debug(f'__SET USER')
        directory = user.get('directory')
        username = user.get('username')
        password = user.get('password')
        self._qlik_user = f'UserDirectory={directory}; UserId={username}'
        self._session.auth = HttpNtlmAuth(username=f'{directory}\\{username}', password=password)

    def _prepare_params(self, params: dict = None) -> dict:
        """
        Builds the url parameters for the request

        Args:
            params: the starting url parameters

        Returns: the updated url parameters
        """
        self._log.debug(f'__PREPARE PARAMS params={params}')
        updated_params = {'Xrfkey': ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))}
        if params:
            for p, v in params.items():
                if v is not None:
                    if isinstance(v, bool):
                        updated_params[p] = str(v).lower()
                    else:
                        updated_params[p] = str(v)
                    self._log.debug(f' >> {p}=>{updated_params[p]}')
                else:
                    self._log.debug(f' >> {p}=>(default)')
        return updated_params

    def _prepare_headers(self, headers: dict = None) -> dict:
        """
        Builds the headers for the request

        Args:
            headers: the starting headers

        Returns: the updated headers
        """
        self._log.debug(f'__PREPARE HEADERS headers={headers}')
        updated_headers = {
            'User-agent': self._referer,
            'Pragma': 'no-cache',
            'X-Qlik-User': self._qlik_user,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if headers:
            updated_headers.update(headers)
        return headers

    def _prepare_request(self, url: str, params: dict) -> tuple:
        """
        Builds the url, url parameters, and headers for the request

        Args:
            url: the starting url
            params: the starting url parameters
            headers: the starting headers

        Returns: a tuple with the updated url, url parameters, and headers
        """
        self._log.debug(f'__PREPARE REQUEST <{url}> params={params}')
        updated_params = self._prepare_params(params=params)
        headers = {'x-Qlik-Xrfkey': updated_params.get('Xrfkey')}
        updated_headers = self._prepare_headers(headers=headers)
        updated_url = self._update_params(url=urllib.parse.urljoin(self._baseurl, url), params=updated_params)
        return updated_url, updated_params, updated_headers

    def _update_params(self, url: str, params: dict) -> str:
        """
        Updates url parameters with new values.

        Args:
            url: the request url
            params: the parameters to update (and their new values)

        Returns: the updated request url
        """
        self._log.debug(f'__UPDATE PARAMS <{url}> params={params}')
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)
        p = urllib.parse.parse_qs(query)
        p.update(params)
        query = urllib.parse.urlencode(p, doseq=True, quote_via=urllib.parse.quote)
        return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

    def call(self, method: str, url: str, params: dict = None, data: str = None) -> 'requests.Response':
        """
        All requests are routed through this method.

        Args:
            method: REST method, one of ['GET', 'POST', 'PUT', 'DELETE']
            url: the endpoint for the request
            params: the url parameters for the request
            data: data to be inserted in the body of the request

        Returns: a Response object
        """
        self._log.info(f'API {method} <{url}> params={params} data={len(data) if data else None}')
        updated_url, updated_params, updated_headers = self._prepare_request(url=url, params=params)

        self._log.debug(f'__PREPARE headers={updated_headers} <{updated_url}>')
        request = requests.Request(method=method,
                                   url=updated_url,
                                   headers=updated_headers,
                                   data=data,
                                   auth=self._session.auth)
        prepared_request = self._session.prepare_request(request)

        self._log.debug(f'__SEND headers={request.headers} <{request.url}>')
        response = self._session.send(request=prepared_request,
                                      cert=self._cert,
                                      verify=self._verify,
                                      allow_redirects=False)
        redirects = 0
        while response.is_redirect:
            redirects += 1
            self._log.debug(f'__REDIRECT {redirects} <{response.next.url}>')
            if redirects > self._session.max_redirects:
                raise requests.HTTPError('Too many re-directions')

            self._log.debug(f'__PREPARE headers={response.headers} <{response.next.url}>')
            self._session.rebuild_auth(prepared_request=response.next, response=response)
            response.next.prepare_headers(updated_headers)
            response.next.prepare_cookies(response.cookies)
            response.next.url = self._update_params(url=response.next.url, params=updated_params)

            self._log.debug(f'__SEND: headers={updated_headers} <{response.next.url}>')
            response = self._session.send(request=response.next,
                                          verify=self._verify,
                                          allow_redirects=False)

        self._log.debug(f'__RECEIVED {response.text}')
        return response
