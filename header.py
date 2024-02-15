import typing
from collections import defaultdict

HeadersDict = typing.Dict[str, typing.List[str]]
HeadersGenerator = typing.Generator[typing.Tuple[str, str], None, None]


class Headers:
    def __init__(self) -> None:
        self._headers = defaultdict(list)

    def add(self, key:str, value:str) -> None:
        self._headers[key.lower()].append(value)

    def get_all(self, key:str) -> typing.List[str]:
        return self._headers[key.lower()]

    def get(self, key:str, default:typing.Optional[str] = None) -> typing.Optional[str]:
        try:
            return self.get_all(key)[-1]
        except IndexError:
            return default

    def __iter__(self) -> HeadersGenerator:
        for name, values in self._headers.items():
            for value in values:
                yield name, value

