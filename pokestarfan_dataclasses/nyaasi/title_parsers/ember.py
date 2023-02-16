import re

from .base import BaseTitleParser
from .exceptions import TitleDoesNotMatchException


class EmberTitleParser(BaseTitleParser):
    _season_batch_regex = re.compile(r"Season ([\d]+)", flags=re.IGNORECASE)

    @classmethod
    def parse(cls, data: str):
        try:
            return cls._common_res_logic(data, ep_method=cls._ep_logic_season)
        except TitleDoesNotMatchException:
            # Batched episodes don't have a batch mark.
            bracket_data = cls._get_brackets(data)
            met = False
            for item in bracket_data:
                if cls._season_batch_regex.search(item):
                    data += " [Batch]"  # Trick into becoming a batch
                    met = True
                    break
            if met:
                return cls._common_res_logic(data, ep_method=cls._ep_logic_season)
            else:
                raise
