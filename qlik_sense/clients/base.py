"""
The Client class is an interface over the QlikSense APIs. The client sets up authentication, logging, and base
settings for interacting with the Qlik Sense APIs. All calls are configured by appropriate lower level services and
then passed up to this class to execute.
"""
import logging
import sys
from typing import Optional, Union
import json
import abc
import random
import string

from urllib3.util import Url
import requests

from qlik_sense import services

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))


class Client(abc.ABC):
    """
    An interface over the QlikSense APIs

    Args:
        scheme: http/https
        host: hostname to connect to
        port: port number
    """
    _auth = None
    _cert = None
    _verify = False

    def __init__(self, scheme: str, host: str, port: int):
        _logger.debug('__SET BASE URL')
        self._scheme = scheme
        self._host = host
        self._port = port

        _logger.debug('__SET SERVICES')
        self.app = services.AppService(self)
        self.stream = services.StreamService(self)
        self.user = services.UserService(self)

    def _get_headers(self, xrf_key: str) -> dict:
        """
        Builds the headers for the request

        Args:
            xrf_key: the csrf key

        Returns: the headers for the request as a dictionary

        """
        headers = {
            'x-Qlik-Xrfkey': xrf_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        return headers

    def _get_url(self, url: str) -> 'Url':
        """
        Builds the url for the request

        Args:
            url: the relative endpoint for the request (e.g. /qrs/app/)

        Returns: the url as a Url object
        """
        return Url(scheme=self._scheme, host=self._host, port=self._port, path=url)

    @staticmethod
    def _get_params(xrf_key: str, params: dict = None) -> dict:
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

    @staticmethod
    def _get_data(data: 'Optional[Union[str, list, dict]]' = None) -> 'Optional[str]':
        """
        Formats the data to be inserted into a request body

        Args:
            data: data to be inserted into the request body

        Returns: the data as a string, in json format if it was originally a dictionary or a list
        """
        if not data:
            return None
        if isinstance(data, list) or isinstance(data, dict):
            data = json.dumps(data)
        return data

    def _get_prepared_request(self, method: str, url: str, params: dict, data: str) -> 'requests.PreparedRequest':
        """
        Builds a prepared request

        Args:
            method: REST method, one of ['GET', 'POST', 'PUT', 'DELETE']
            url: the relative endpoint for the request (e.g. /qrs/app/)
            params: the query string parameters for the request
            data: data to be inserted in the body of the request

        Returns: the prepared request, ready to send
        """
        _logger.debug(f'__PREPARE REQUEST {method} <{url}> params={params} data={len(data) if data else None}')
        xrf_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        request = requests.Request(method=method,
                                   url=self._get_url(url=url),
                                   headers=self._get_headers(xrf_key=xrf_key),
                                   data=self._get_data(data),
                                   params=self._get_params(xrf_key=xrf_key, params=params),
                                   auth=self._auth)
        return request.prepare()

    def _send_request(self, request: 'requests.PreparedRequest', session: 'requests.Session') -> 'requests.Response':
        """
        Executes the call

        Args:
            request: request to be made

        Returns: the response
        """
        _logger.debug(f'__SEND REQUEST {request.method} <{request.url}>'
                      f' headers={request.headers} body_size={len(request.body())}')
        return session.send(request=request,
                            cert=self._cert,
                            verify=self._verify,
                            allow_redirects=False)

    def _handle_redirect(self, response: 'requests.Response', headers: dict,
                         session: 'requests.Session') -> 'requests.Response':
        """
        Handles redirects for the request. This happens when using the proxy service.

        Args:
            response: the response with a redirect
            headers: the original headers from the original request
            session: the session

        Returns: the final response with no redirect
        """
        count = 0
        while response.is_redirect:
            _logger.debug('f__REDIRECT ENCOUNTERED')
            count += 1
            if count > session.max_redirects:
                raise requests.HTTPError('Exceeded max redirects')
            request = response.next
            session.rebuild_auth(prepared_request=request, response=response)
            request.prepare_headers(headers=headers)
            request.prepare_cookies(cookies=response.cookies)
            response = self._send_request(request=request, session=session)
        return response

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
        _logger.info(f'API CALL {method} <{url}> params={params} data={len(data) if data else None}')
        prepared_request = self._get_prepared_request(method=method, url=url, params=params, data=data)
        session = requests.Session()
        response = self._send_request(request=prepared_request, session=session)
        if response.is_redirect:
            response = self._handle_redirect(response=response, headers=prepared_request.headers, session=session)

        _logger.debug(f'__RESPONSE RECEIVED {response.text} headers={response.headers}')
        return response
