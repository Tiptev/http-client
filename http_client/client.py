from models import Response, Request, URL
from connections import TCPConnection
from typing import Optional

class HttpClient:
    @classmethod
    def method(cls, method: str, url: str, headers: dict,
               body: Optional[bytes] = None) -> Response:
        session = cls()
        url = URL.parse(url)
        session.request = Request(method, url, headers, body)
        session.connection = TCPConnection(
            session.request.url.host,
            session.request.url.port)
        response_bytes = (session.connection.
                          run_one_session(session.request.to_bytes()))
        session.response = Response.from_bytes(response_bytes)

        return session.response


    @classmethod
    def get(cls, url: str, headers: dict, body: Optional[bytes] = None) -> Response:
        return cls.method('GET', url, headers, body)



