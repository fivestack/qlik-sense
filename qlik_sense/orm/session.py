import logging
from typing import Union
import sys
import os.path
import urllib.parse
import random
import string
import json

import urllib3
import requests
from requests_ntlm import HttpNtlmAuth


class _FileUpload:

    def __init__(self, filename: str, chunk_size: int = 512):
        self._filename = filename
        self._chunk_size = chunk_size << 10
        self._total_size = os.path.getsize(filename)
        self._read_so_far = 0

    def __iter__(self):
        with open(self._filename, 'rb') as file:
            while True:
                data = file.read(self._chunk_size)
                if not data:
                    break
                self._read_so_far += len(data)
                yield data

    def __len__(self):
        return self._total_size


class Session:
    """
    A QlikSense session that uses the QRS and QPS APIs

    Args:
        log_name: logger instance name
        verbosity: debug level
        schema: http/https
        host: hostname to connect to
        port: port number
        certificate: path to .pem client certificate
        verify: false to trust in self-signed certificates
        user: dict with keys {directory, username, password}
    """

    _referer = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) qsAPI APIREST (QSense)'
    _session = None
    _cert = None
    _chunk_size = 512  # Kb

    def __init__(self,
                 log_name: str, verbosity: 'Union[str, int]',
                 schema: str, host: str, port: int,
                 certificate: str = None, verify: bool = False, user: dict = None):
        self._set_logger(log_name=log_name, verbosity=verbosity)
        self._baseurl = f'{schema}://{host}:{str(port)}'
        self._session = requests.Session()
        self._set_auth(certificate=certificate, verify=verify, user=user)

    def _set_logger(self, log_name: str, verbosity: 'Union[str, int]'):
        self._log = logging.getLogger(log_name)
        if not self._log.hasHandlers():
            self._log.addHandler(logging.StreamHandler(sys.stdout))
        self._log.setLevel(verbosity)

    def _set_auth(self, certificate: str, verify: bool, user: dict):
        if certificate:
            self._log.debug('PEM authentication enabled')
            self._set_cert(certificate=certificate, verify=verify)
        elif user:
            self._log.debug('NTLM authentication enabled')
            self._set_user(user=user)
        else:
            self._log.debug('NO authentication enabled')

    def _set_cert(self, certificate: str, verify: bool):
        (base, ext) = os.path.splitext(certificate)
        self._cert = (base + ext, base + '_key' + ext)
        self._log.debug(f'CERTKEY: {base}.{ext}')
        self._verify = verify
        if not self._verify:
            urllib3.disable_warnings()

    def _set_user(self, user: dict):
        self.user_directory = user.get('directory')
        self.user = user.get('username')
        self.password = user.get('password')
        self._session.auth = HttpNtlmAuth(f'{self.user_directory}\\{self.user}', self.password)

    def _params_prepare(self, params: dict = None, xhd: dict = None) -> tuple:
        par = {'Xrfkey': ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))}
        if params:
            for p, v in params.items():
                if v is not None:
                    if isinstance(v, bool):
                        par[p] = str(v).lower()
                    else:
                        par[p] = str(v)
                    self._log.debug(f' >> {p}=>{par[p]}')
                else:
                    self._log.debug(f' >> {p}=>(default)')
        hd = {'User-agent': self._referer,
              'Pragma': 'no-cache',
              'X-Qlik-User': f'UserDirectory={self.user_directory}; UserId={self.user}',
              'x-Qlik-Xrfkey': par.get('Xrfkey'),
              'Accept': 'application/json',
              'Content-Type': 'application/json'}
        if xhd:
            hd.update(xhd)
        return par, hd

    @staticmethod
    def _params_update(url: str, params: dict) -> str:
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)
        p = urllib.parse.parse_qs(query)
        p.update(params)
        query = urllib.parse.urlencode(p, doseq=True, quote_via=urllib.parse.quote)
        return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

    def _call(self, method: str, url, params: dict = None, data: str = None, files=None) -> requests.Response:
        if method.upper() not in ('GET', 'POST', 'PUT', 'DELETE'):
            raise ValueError(f'invalid method <{method}>')

        self._log.info(f'API {method} <{url}>')
        updated_params, headers = self._params_prepare(params,
                                       {} if files is None else {'Content-Type': 'application/vnd.qlik.sense.app'})
        updated_url = self._params_update(urllib.parse.urljoin(self._baseurl, url), updated_params)
        request = requests.Request(method=method,
                                   url=updated_url,
                                   headers=headers,
                                   data=data,
                                   files=files,
                                   auth=self._session.auth)
        prepared_request = self._session.prepare_request(request)

        self._log.debug(f'SEND: {request.url}')
        response = self._session.send(request=prepared_request,
                                      cert=self._cert,
                                      verify=self._verify,
                                      allow_redirects=False)
        redirects = 0
        while response.is_redirect:
            redirects += 1
            if redirects > self._session.max_redirects:
                raise requests.HTTPError('Too many re-directions')
            self._session.rebuild_auth(prepared_request=response.next, response=response)
            response.next.prepare_headers(headers)
            response.next.prepare_cookies(response.cookies)
            response.next.url = self._params_update(url=response.next.url, params=updated_params)
            self._log.debug(f'REDIR: {response.next.url}')
            response = self._session.send(request=response.next, verify=self._verify, allow_redirects=False)

        self._log.debug(f'RECEIVED: {response.text}')
        return response

    def download(self, url: str, filename: str, params: dict = None) -> requests.Response:
        self._log.info(f'API DOWNLOAD <{url}>')
        updated_params, headers = self._params_prepare(params=params)
        updated_url = self._params_update(urllib.parse.urljoin(self._baseurl, url), updated_params)

        self._log.debug(f'__SEND: {updated_url}')
        response = self._session.get(updated_url,
                                     headers=headers,
                                     cert=self._cert,
                                     verify=self._verify,
                                     stream=True,
                                     auth=self._session.auth)

        self._log.info(f'__Downloading (in {str(self._chunk_size)}Kb blocks): ')
        self._save_file(filename=filename, response=response)
        return response

    def _save_file(self, filename: str, response: requests.Response):
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=self._chunk_size << 10):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
            self._log.info(f'__Saved: {os.path.abspath(filename)}')

    def upload(self, url: str, filename: str, params: dict = None) -> requests.Response:
        self._log.info(f'API UPLOAD <{url}>')
        updated_params, headers = self._params_prepare(params, {'Content-Type': 'application/vnd.qlik.sense.app'})
        updated_url = self._params_update(urllib.parse.urljoin(self._baseurl, url), updated_params)

        self._log.debug(f'__SEND: {updated_url}')
        self._log.info(f'__Uploading {os.path.getsize(filename)} bytes')
        response = self._session.post(updated_url,
                                      headers=headers,
                                      cert=self._cert,
                                      verify=self._verify,
                                      data=_FileUpload(filename, self._chunk_size),
                                      auth=self._session.auth)

        self._log.info('__Done.')
        return response

    def get(self, url: str, params: dict = None) -> requests.Response:
        """
        Executes a get request

        Args:
            url: uri REST path
            params: url parameters as a dict (example: {'filter': "name eq 'myApp'} )
        """
        return self._call(method='GET', url=url, params=params)

    def post(self, url: str, params: dict = None, data: 'Union[str, dict, list]' = None,
             files=None) -> requests.Response:
        """
        Executes a post request

        Args:
            url: uri REST path
            params: url parameters as a dict (example: {'filter': "name eq 'myApp'} )
            data: stream data input (native dict/list structures are json formatted)
            files: file input
        """
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        return self._call(method='POST', url=url, params=params, data=data, files=files)

    def put(self, url: str, params: dict = None, data: 'Union[str, dict, list]' = None) -> requests.Response:
        """
        Executes a put request

        Args:
            url: uri REST path
            params: url parameters as a dict (example: {'filter': "name eq 'myApp'} )
            data: stream data input (native dict/list structures are json formatted)
        """
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        return self._call(method='PUT', url=url, params=params, data=data)

    def delete(self, url: str, params: dict = None) -> requests.Response:
        """
        Executes a delete request

        Args:
            url: uri REST path
            params: url parameters as a dict (example: {'filter': "name eq 'myApp'} )
        """
        return self._call(method='DELETE', url=url, params=params)
