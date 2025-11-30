from dataclasses import dataclass, field
from typing import Dict, Optional, ClassVar, Self, Literal, List
from urllib.parse import urlparse
import json


@dataclass(frozen=True)
class URL:
    scheme: str
    host: str
    port: Optional[int]
    path: str
    query: str
    fragment: str

    DEFAULT_PORTS = {'http': 80, 'https': 443}

    @classmethod
    def parse(cls, url: str) -> Self:
        parsed = urlparse(url)
        port = parsed.port
        if not port:
            port = cls.DEFAULT_PORTS[parsed.scheme]

        return cls(
            scheme=parsed.scheme.lower(),
            host=parsed.hostname,
            port=port,
            path=parsed.path,
            query=parsed.query,
            fragment=parsed.fragment,
        )


@dataclass(frozen=True)
class Request:
    method: Literal['GET', 'POST']
    url: URL
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[bytes] = None

    HTTP_VERSION: ClassVar[str] = "HTTP/1.1"

    def get_first_string_request(self) -> str:
        return f"{self.method.upper()} {self.url.path} {self.HTTP_VERSION}"

    def get_second_string_request(self) -> str:
        return f"Host: {self.url.host}"

    def get_headers(self) -> List[str]:
        header_string = []
        for header_title, header_value in self.headers.items():
            header_string.append(f"{header_title}: {header_value}")

        return header_string

    def to_bytes(self) -> bytes:
        request_strings = [self.get_first_string_request(), self.get_second_string_request()]
        request_strings.extend(self.get_headers())

        raw_request = "\r\n".join(request_strings).encode("utf-8") + b"\r\n\r\n"
        if self.body is not None:
            raw_request += self.body
        return raw_request


@dataclass(frozen=True)
class Response:
    status_code: int
    reason: str
    headers: Dict[str, str]
    content: bytes

    @classmethod
    def from_bytes(cls, raw: bytes) -> Self:
        header_end = raw.find(b"\r\n\r\n")
        if header_end == -1:
            raise ValueError("Malformed HTTP: no header-body separator")

        header_bytes = raw[:header_end]
        body = raw[header_end + 4:]

        header_lines = header_bytes.split(b"\r\n")
        if not header_lines:
            raise ValueError("No status line")

        try:
            status_line = header_lines[0].decode("utf-8")
            parts = status_line.split(" ", 2)
            if len(parts) < 2:
                raise ValueError("Invalid status line")
            status_code = int(parts[1])
            reason = parts[2] if len(parts) > 2 else ""
        except (UnicodeDecodeError, ValueError, IndexError) as e:
            raise ValueError(f"Failed to parse status line: {e}")

        headers = {}
        for line in header_lines[1:]:
            if b":" in line:
                try:
                    k, v = line.split(b":", 1)
                    key = k.decode("utf-8").strip()
                    val = v.decode("utf-8").strip()
                    headers[key] = val
                except UnicodeDecodeError:
                    continue
        content = body

        return cls(
            status_code=status_code,
            reason=reason,
            headers=headers,
            content=content
        )

    def json(self):
        return json.loads(self.content)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

