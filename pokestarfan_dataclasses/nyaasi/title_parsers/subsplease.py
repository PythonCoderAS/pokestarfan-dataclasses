from .base import BaseTitleParser
from .exceptions import TitleDoesNotMatchException


class SubsPleaseTitleParser(BaseTitleParser):
    @classmethod
    def parse(cls, data: str):
        return cls._common_res_logic(data)
