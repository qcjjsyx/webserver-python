from request import *
from response import *
from server import *

import re
from collections import OrderedDict, defaultdict
from functools import partial
from typing import Callable, Dict, Optional, Pattern, Set, Tuple



class Application:
    def __call__(self, request:Request) -> Response:
        return Response("501 Not Implemented", content="Not Implemented")



RouteT = Tuple[Pattern[str], HandlerT]
RoutesT = Dict[str, Dict[str, RouteT]]
RouteHandlerT = Callable[..., Response]



class Router:
    def __init__(self) -> None:
        self.route_by_names: RouteT = defaultdict(OrderedDict)
        self.route_name: Set[str] = set()

