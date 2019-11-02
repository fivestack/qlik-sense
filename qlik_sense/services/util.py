from dataclasses import dataclass
from typing import Union


@dataclass
class QSAPIRequest:
    method: str
    url: str
    params: dict = None
    data: Union[str, list, dict] = None