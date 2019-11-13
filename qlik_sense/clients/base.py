"""
The Client class is an interface over the QlikSense APIs. The client sets up authentication, logging, and base
settings for interacting with the Qlik Sense APIs. All calls are configured by appropriate lower level services and
then passed up to this class to execute.
"""
import logging
import sys
from typing import Optional, Union
import abc
import random
import string

from urllib3.util import Url
import requests

from qlik_sense import services

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))
_logger.setLevel(logging.DEBUG)


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

    def __init__(self, host: str, port: int, scheme: str = 'https'):
        _logger.debug('__SET BASE URL')
        self._host = host
        self._port = port
        self._scheme = scheme

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
                                   data=data,
                                   params=self._get_params(xrf_key=xrf_key, params=params),
                                   auth=self._auth)
        _logger.debug(f'__REQUEST BUILT {request.method} <{request.url}> '
                      f'params={request.params} '
                      f'data={len(request.data) if request.data else None}')
        prepared_request = request.prepare()
        _logger.debug(f'__REQUEST PREPARED {prepared_request.method} <{prepared_request.url}> '
                      f'headers={prepared_request.headers} '
                      f'body={len(prepared_request.body) if prepared_request.body else None}')
        return prepared_request

    def _send_request(self, request: 'requests.PreparedRequest', session: 'requests.Session') -> 'requests.Response':
        """
        Executes the call

        Args:
            request: request to be made

        Returns: the response
        """
        _logger.debug(f'__SEND REQUEST {request.method} <{request.url}> headers={request.headers} '
                      f'body={len(request.body) if request.body else None}')
        response = session.send(request=request,
                                cert=self._cert,
                                verify=self._verify,
                                allow_redirects=False)
        _logger.debug(f'__RESPONSE RECEIVED {response.status_code} {response.reason} headers={response.headers} '
                      f'content_size={len(response.content) if response.content else None} '
                      f'is_redirect={response.is_redirect}')
        return response

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
            _logger.debug('__REDIRECT ENCOUNTERED')
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
        _logger.info(f'API REQUEST {method} <{url}> params={params} data={len(data) if data else None}')
        prepared_request = self._get_prepared_request(method=method, url=url, params=params, data=data)
        session = requests.Session()
        response = self._send_request(request=prepared_request, session=session)
        if response.is_redirect:
            response = self._handle_redirect(response=response, headers=prepared_request.headers, session=session)
        _logger.info(f'API RESPONSE {response.text} headers={response.headers}')
        return response
