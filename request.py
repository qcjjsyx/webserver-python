import typing
import socket

from header import Headers
import io


class BodyReader(io.IOBase):
    def __init__(self, sock: socket.socket, *, buff: bytes = b"", buffsize: int = 16_384) -> None:
        self._sock = sock
        self._buff = buff
        self._buffsize = buffsize

    def readable(self) -> bool:
        return True

    def read_nbytes(self, n: int) -> bytes:
        while len(self._buff) < n:
            data = self._sock.recv(self._buffsize)
            if not data:
                break
            self._buff += data

        res, self._buff = self._buff[:n], self._buff[n:]
        return res


class Request(typing.NamedTuple):
    method: str
    path: str
    headers: Headers
    body: BodyReader
    @classmethod
    def from_sock(cls, sock: socket.socket) -> "Request":
        lines = iter_lines(sock)

        try:
            request_line = next(lines).decode("ascii")
        except StopIteration:
            raise ValueError("Request line missing")

        try:
            method, path, _ = request_line.split(' ')
        except ValueError:
            raise ValueError(f"Malformed request line {request_line!r}")

        headers = Headers()
        buff = b""
        while True:
            try:
                line = next(lines)
            except StopIteration as e:
                buff = e.value
                break

            try:
                name, _, value = line.decode("ascii").partition(":")
                headers.add(name, value.lstrip())
            except ValueError:
                raise ValueError(f"Malformed header line {line!r}.")

        body = BodyReader(sock=sock, buff=buff)

        return cls(method=method.upper(), path=path, headers=headers, body=body)


def iter_lines(sock: socket.socket, buffsize: int = 16_384) -> typing.Generator[bytes, None, bytes]:
    """_summary_
        分析得到的客户机请求行
    Args:
        sock (socket.socket): _description_
        buffsize (int, optional): _description_. Defaults to 16_384.

    Returns:
        typing.Generator[bytes,None,bytes]: _description_

    Yields:
        Iterator[typing.Generator[bytes,None,bytes]]: 将接受到的请求按照'\r\n'进行分割，便于处理请求
    """
    buff = b""
    while True:
        data = sock.recv(buffsize)
        if not data:
            return b""

        buff += data
        while True:
            try:
                i = buff.index(b"\r\n")
                line, buff = buff[:i], buff[i + 2:]
                if not line:
                    return buff
                yield line
            except IndexError:
                break
