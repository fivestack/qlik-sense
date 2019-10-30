"""
The models are very basic for now. They will grow as the core functionality is built out.
"""
from dataclasses import dataclass, field
from typing import Union


@dataclass(unsafe_hash=True)
class Stream:
    """
    Represents a Qlik Sense stream

    Args:
        id: the id of the stream on the server in uuid format
        name: the name of the stream
        privileges:
    """
    id: str = field(hash=True)
    name: str = field(default=None, hash=False)
    privileges: list = field(default_factory=list, hash=False)


@dataclass(unsafe_hash=True)
class App:
    """
    Represents a Qlik Sense application

    Args:
        id: the id of the app on the server in uuid format
        name: the name of the application
        stream: the stream that contains the application
    """
    id: str = field(hash=True)
    name: str = field(default=None, hash=False)
    stream: Stream = field(default=None, hash=False)


@dataclass
class QSAPIRequest:
    method: str
    url: str
    params: dict = None
    data: Union[str, list, dict] = None
