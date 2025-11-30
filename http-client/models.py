from typing import Optional, Dict, Any, Union, Literal
from dataclasses import dataclass

METHODS = Literal['GET', 'POST']

@dataclass(frozen=True)
class Address:
    ip: str
    port: int

    def get_address(self):
        return self.ip, self.port

@dataclass(frozen=True)
class Request:
    method: METHODS
    url: str  # или URL
    headers: Dict[str, str]
    body: Optional[bytes] = None


@dataclass(frozen=True)
class Response:
    status_code: int
    headers: Dict[str, str]
    content: bytes
    url: str



