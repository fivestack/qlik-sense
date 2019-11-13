from dataclasses import dataclass
from typing import Union, Optional


@dataclass
class QSAPIRequest:
    method: str
    url: str
    params: dict = None
    data: Optional[Union[str, list, dict]] = None
