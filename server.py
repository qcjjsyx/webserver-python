import logging
import mimetypes
import socket
import typing
from queue import Queue
from threading import Thread

from application import *
from request import Request
from response import *

HandlerT = typing.Callable[[Request], Response]

SERVE_ROOT = os.path.abspath("")

class HTTPServer:
    def __init__(self, host="127.0.0.1", port=9000, worker_count=16) -> None:
        self.handlers = []
        self.host = host
        self.port = port
        self.worker_count = worker_count
        self.worker_backlog = worker_count*8
        self.connection_queue = Queue(self.worker_backlog)

    def serve(self) -> None:
        workers = []
        print("start")
        for _ in range(self.worker_count):
            worker = HTTPWorkers(self.connection_queue, self.handlers)
            worker.start()
            workers.append(worker)
        print("workers ready")
        with socket.socket() as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen(self.worker_backlog)
            print(f"Listening on {self.host}:{self.port}...")

            while True:
                try:
                    self.connection_queue.put(server_sock.accept())
                except KeyboardInterrupt:
                    break

        for worker in workers:
            worker.stop()

        for worker in workers:
            worker.join(timeout=30)

    def mount(self, handler: HandlerT) -> None:
        self.handlers.append(handler)


class HTTPWorkers(Thread):
    def __init__(self, connection_queue: Queue, handlers: typing.List[HandlerT]) -> None:
        super().__init__(daemon=True)

        self.connection_queue = connection_queue
        self.handlers = handlers
        self.running = False

    def stop(self) -> None:
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            try:
                client_socket, client_addr = self.connection_queue.get(timeout=1)
            except:
                continue

            try:
                self.handle_client(client_socket, client_addr)
            except Exception as e:
                print(f"Unhadle error: {e}")
                continue
            finally:
                self.connection_queue.task_done()

    def handle_client(self, client_socket: socket.socket, client_addr: typing.Tuple[str, int]) -> None:
        with client_socket:
            try:
                request = Request.from_sock(client_socket)
                # print(request)
            except:
                logging.WARNING("Failed to parse request.", exc_info=True)
                response = Response(status="400 Bad Request", content="Bad Request")
                response.send(client_socket)
                return

            if "100-continue" in request.headers.get("expect", ""):
                response = Response(status="100 Continue")
                response.send(client_socket)

            for handler in self.handlers:
                try:
                    response = handler(request)
                    response.send(client_socket)
                except Exception as e:
                    logging.exception("Unexpected error from handler %r.", handler)
                    response = Response(status="500 Internal Server Error", content="Internal Error")
                    response.send(client_socket)
                finally:
                    break


            else:
                response = Response(status="404 Not Found", content="Not Found")
                response.send(client_socket)









# def app(request: Request) -> Response:
#     return Response(status="200 OK", content="Hello!")
#
# def wrap_auth(handler: HandlerT) -> HandlerT:
#     def auth_handler(request: Request) -> Response:
#         authorization = request.headers.get("authorization", "")
#         if authorization.startswith("Bearer ") and authorization[len("Bearer "):] == "opensesame":
#             return handler(request)
#         return Response(status="403 Forbidden", content="Forbidden!")
#     return auth_handler


# def serve_static(serve_root: str) -> HandlerT:
#
#     def handler(request: Request) -> Response:
#         path = request.path
#
#         if path == "":
#             path = "/html/example.html"
#
#         abspath = os.path.normpath(os.path.join(serve_root, path.lstrip("/")))
#         # print(abspath)
#
#         if not abspath.startswith(serve_root):
#             response = Response(status="404 Not Found", content="Not Found")
#             return response
#
#         try:
#
#             content_type, encoding = mimetypes.guess_type(abspath)
#
#             if content_type is None:
#                 content_type = "application/octet-stream"
#
#             if encoding is not None:
#                 content_type += f"; charset={encoding}"
#             f = open(abspath, "rb")
#             response = Response(status="200 OK", body=f)
#             response.headers.add("content-type", content_type)
#             return response
#         except FileNotFoundError:
#             response = Response(status="404 Not Found", content="Not Found")
#             return response
#
#     return handler




