"""
This module provides the mechanics for interacting with Qlik Sense streams. It uses a one-to-one model
to wrap the QRS endpoints and uses marshmallow to parse the results into Qlik Sense Stream objects where appropriate.
"""
from typing import TYPE_CHECKING, List, Optional
from dataclasses import asdict

from qlik_sense.models.stream import StreamCondensedSchema, StreamSchema
from qlik_sense.services import util, base

if TYPE_CHECKING:
    from qlik_sense.clients.base import Client
    from qlik_sense.models.stream import StreamCondensed, Stream
    import requests


class StreamService(base.BaseService):
    """
    StreamService wraps each one of the stream-based QlikSense endpoints in a method. This buffers the application
    from API updates.

    Args:
        client: a Client class that provides an interface over the Qlik Sense APIs

    Supported Methods:

        - qrs/stream: GET, POST
        - qrs/stream/many: POST
        - qrs/stream/count: GET
        - qrs/stream/full: GET
        - qrs/stream/{stream.id}: GET, PUT, DELETE

    Unsupported Methods:

        - qrs/stream/previewcreateprivilege: POST
        - qrs/stream/previewprivileges: POST
        - qrs/stream/table: POST
    """
    requests = list()

    def __init__(self, client: 'Client'):
        self.client = client
        self.url = '/qrs/stream'

    def _call(self, request: 'util.QSAPIRequest') -> 'requests.Response':
        return self.client.call(**asdict(request))

    def query(self, filter_by: str = None, order_by: str = None, privileges: 'Optional[List[str]]' = None,
              full_attribution: bool = False) -> 'Optional[List[StreamCondensed]]':
        """
        This method queries Qlik Sense streams based on the provided criteria and provides either partial or
        full attribution of the streams based on the setting of full_attribution

        Args:
            filter_by: a filter string in jquery format
            order_by: an order by string
            privileges:
            full_attribution: allows the response to contain the full user attribution,
            defaults to False (limited attribution)

        Returns: a list of Qlik Sense condensed Streams that meet the query_string criteria (or None)
        """
        if full_attribution:
            schema = StreamSchema()
        else:
            schema = StreamCondensedSchema()
        return self._query(schema=schema, filter_by=filter_by, order_by=order_by, privileges=privileges,
                           full_attribution=full_attribution)

    def get_by_name(self, name: str) -> 'Optional[List[StreamCondensed]]':
        """
        This method is such a common use case of the query() method that it gets its own method

        Args:
            name: name of the stream

        Returns: the Qlik Sense condensed Stream(s) that fit the criteria
        """
        filter_by = f"name eq '{name}'"
        return self.query(filter_by=filter_by)

    def get(self, id: str, privileges: 'Optional[List[str]]' = None) -> 'Optional[Stream]':
        """
        This method returns a Qlik Sense stream by its id

        Args:
            id: id of the stream on the server in uuid format
            privileges:

        Returns: a Qlik Sense Stream with full attribution
        """
        return self._get(schema=StreamSchema(), id=id, privileges=privileges)

    def create(self, stream: 'Stream', privileges: 'Optional[List[str]]' = None) -> 'Optional[Stream]':
        """
        This method creates a new stream on the server with the provided attribution

        Args:
            stream: the new stream
            privileges:
        """
        return self._create(schema=StreamSchema(), entity=stream, privileges=privileges)

    def create_many(self, streams: 'List[Stream]', privileges: 'Optional[List[str]]' = None) -> 'Optional[List[Stream]]':
        """
        This method creates new streams on the server with the provided attribution

        Args:
            streams: a list of new streams
            privileges:
        """
        return self._create_many(schema=StreamSchema(), entities=streams, privileges=privileges)

    def update(self, stream: 'Stream', privileges: 'Optional[List[str]]' = None) -> 'Optional[Stream]':
        """
        This method updates attributes of the provided stream on the server

        Args:
            stream: stream to update
            privileges:
        """
        return self._update(schema=StreamSchema(), entity=stream, privileges=privileges)

    def delete(self, stream: 'StreamCondensed'):
        """
        This method deletes the provided stream from the server

        Args:
            stream: stream to delete
        """
        self._delete(entity=stream)
