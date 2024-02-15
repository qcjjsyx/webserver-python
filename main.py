import sys

from application import  *
from server import *


def main() -> int:
    application = Application()

    server = HTTPServer()
    server.mount(application)
    server.serve()
    return 0


if __name__ == "__main__":
    sys.exit(main())