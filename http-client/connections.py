import socket

class TCPConnection:
    def __init__(self, host: str, port: int, time_out: float = None):
        self.server_host: str = host
        self.server_port: int = port
        self.time_out: float = time_out

        self._connection: bool = False
        self._sock: socket.socket = None

        self.content: bytes = bytes()
        self.buffer: bytearray = bytearray()

    def open_connection(self):
        self._sock = socket.socket(family=socket.AF_INET,
                                   type=socket.SOCK_STREAM)
        if self.time_out:
            self._sock.settimeout(self.time_out)
        self._sock.connect((self.server_host, self.server_port))
        self._connection = True

    def send_content(self, content: bytes):
        if not isinstance(content, bytes):
            raise TypeError("content должен быть типа bytes")
        try:
            self._sock.sendall(content)
            self.content = content
        except socket.timeout:
            return self.close()

    def read_chunk(self):
        chunk = self._sock.recv(128)
        try:
            if not chunk:
                return False
            else:
                self.buffer.extend(chunk)
                return True
        except socket.timeout:
            return self.close()

    def close(self):
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            finally:
                self._sock = None
                self._connection = False

    def run_one_session(self, content: bytes):
        self.open_connection()
        try:
            if content is not None:
                self.send_content(content)
            while self.read_chunk():
                pass
            return self.buffer
        finally:
            self.close()
