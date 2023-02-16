from .base import BaseTitleParser


class ASWTitleParser(BaseTitleParser):
    @classmethod
    def parse(cls, data: str):
        return cls._common_res_logic(data, ep_method=cls._ep_logic_season)
