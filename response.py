import os
import socket
import typing
from header import Headers
import io

# RESPONSE = b"""\
# HTTP/1.1 200 OK
# Content-type: text/html
# Content-length: 15
#
# <h1>Hello!</h1>""".replace(b"\n", b"\r\n")
#
#
# BAD_RESPONSE = b"""\
# HTTP/1.1 400 Bad Request
# Content-type: text/plain
# Content-length: 11
#
# Bad Request""".replace(b"\n", b"\r\n")
#
# NOT_FOUND_RESPONSE = b"""\
# HTTP/1.1 404 Not Found
# Content-type: text/plain
# Content-length: 9
#
# Not Found""".replace(b"\n", b"\r\n")
#
# METHOD_NOT_ALLOWED_RESPONSE = b"""\
# HTTP/1.1 405 Method Not Allowed
# Content-type: text/plain
# Content-length: 17
#
# Method Not Allowed""".replace(b"\n", b"\r\n")


class Response:

    def __init__(self,
                 status: str,
                 headers: typing.Optional[Headers] = None,
                 body: typing.Optional[typing.IO] = None,
                 content: typing.Optional[str]=None,
                 encoding: str="utf-8") -> None:
        self.status = status.encode()
        self.headers = headers or Headers()

        if content is not None:
            self.body = io.BytesIO(content.encode(encoding))
        elif body is None:
            self.body = io.BytesIO()
        else:
            self.body = body
            

    def send(self, sock:socket.socket) -> None:
        content_length = self.headers.get("content-length")

        if content_length is None:
            try:
                body_status = os.fstat(self.body.fileno())
                content_length = body_status.st_size
            except OSError:
                self.body.seek(0, os.SEEK_END)
                content_length = self.body.tell()
                self.body.seek(0, os.SEEK_SET)

            if content_length>0:
                self.headers.add("content_length", content_length)

        headers = b"HTTP/1.1 " + self.status + b"\r\n"
        for header_name, header_value in self.headers:
            headers += f"{header_name}: {header_value}\r\n".encode()

        sock.sendall(headers+b"\r\n")
        if content_length>0:
            sock.sendfile(self.body)

