"""
The domain models are very basic for now, as the core functionality is built out. Once more complicated
functionality is required, these may grow.
"""
from dataclasses import dataclass


@dataclass
class App:
    """
    Represents a Qlik Sense application

    Args:
        guid: the guid of the app on the server
        name: the name of the application
    """
    guid: str
    name: str = None


@dataclass
class Stream:
    """
    Represents a Qlik Sense Stream

    Args:
        guid: the guid of the stream on the server
    """
    guid: str
