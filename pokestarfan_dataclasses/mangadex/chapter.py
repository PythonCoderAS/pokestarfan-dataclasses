import datetime
from typing import List, Optional

from .group import MangadexGroup
from ..base import BaseDataClass
from ..util import dict_copy, dict_copy_mapping, try_num


class MangadexPage(BaseDataClass):
    REQUIRED_FIELDS = ("number", "filepath", "chapter", "server")
    REPR_FIELDS = ("number", "filepath")
    COMP_FIELD = "number"
    __slots__ = ("number", "filepath", "chapter", "fallback", "server", "hash")

    number: int
    filepath: str
    chapter: "MangadexChapter"
    server: str
    fallback: Optional[str]

    @property
    def url(self):
        return f"{self.server}/{self.chapter.hash}/{self.filepath}"

    @property
    def fallback_url(self):
        return f"{self.fallback}/{self.chapter.hash}/{self.filepath}"


class MangadexChapter(BaseDataClass):
    REPR_FIELDS = ("num", "title", "id")
    COMP_FIELD = "id"
    REQUIRED_FIELDS = ("id",)
    __slots__ = (
        "id", "hash", "volume", "num", "title", "language", "groups", "uploader_id", "timestamp", "comments", "views", "pages")

    id: int
    hash: Optional[str]
    volume: Optional[int]
    num: Optional[float]
    title: Optional[str]
    language: Optional[str]
    uploader_id: Optional[int]
    timestamp: Optional[datetime.datetime]
    comments: Optional[int]
    views: Optional[int]
    groups: Optional[List[MangadexGroup]]
    pages: Optional[List[MangadexPage]]

    @classmethod
    def from_api_v2_list(cls, data: dict):
        final_data = {}
        dict_copy(data, final_data, "hash", "title", "language")
        dict_copy(data, final_data, "volume", "comments", "views", condition=lambda val: str(val).isnumeric() and int(val),
                  on_item=lambda item: int(item))
        dict_copy_mapping(data, final_data, uploader="uploader_id", id="id", on_item=lambda item: item)
        num = data.get("chapter", None)
        self = cls(**final_data)
        self.groups = [MangadexGroup.from_api_v2(item) for item in data["groups"]]
        try_num(self, num)
        self.timestamp = datetime.datetime.utcfromtimestamp(float(data["timestamp"]))
        return self

    @classmethod
    def from_api_v2_individual(cls, data: dict):
        real_data = data["data"]
        self = cls.from_api_v2_list(real_data)
        self.add_pages(data)
        return self

    @classmethod
    def from_api_v1(cls, id: str, data: dict):
        final_data = {"id": int(id)}
        dict_copy(data, final_data, "title")
        dict_copy_mapping(data, final_data, lang_code="language")
        dict_copy(data, final_data, "volume", "comments", condition=lambda val: str(val).isnumeric() and int(val), on_item=lambda item: int(item))
        num = data.get("chapter", None)
        self = cls(**final_data)
        try_num(self, num)
        self.timestamp = datetime.datetime.utcfromtimestamp(float(data["timestamp"]))
        groups = []
        for suffix in ("", "_2", "_3"):
            if data["group_id" + suffix] != 0:
                groups.append(MangadexGroup(id=data["group_id" + suffix], name=data["group_name" + suffix]))
        self.groups = groups
        return self

    @property
    def chapter_str(self):
        return (str(self.num) or "") + ": " + (self.title or "")

    def add_pages(self, data: dict):
        real_data = data["data"]
        server = real_data["server"]
        fallback = real_data.get("serverFallback", None)
        self.pages = [MangadexPage(number=num, filepath=page, chapter=self, server=server, fallback=fallback) for num, page in
                      enumerate(real_data["pages"], start=1)]


class MangadexChapterList(list, List[MangadexChapter]):
    @property
    def latest(self) -> Optional[MangadexChapter]:
        return sorted(self)[-1] if self else None

    __slots__ = ("lang")

    def __init__(self, *args, lang=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang

    def __repr__(self) -> str:
        return f"{type(self).__name__}<{len(self)} chapters, latest={self.latest!r}, lang={self.lang!r}>"

    def id_list(self):
        return [item.id for item in self]

    def filter_lang(self, lang="gb") -> "MangadexChapterList":
        return type(self)([chap for chap in self if chap.language and chap.language == lang], lang=lang)

    def filter_duplicates(self) -> "MangadexChapterList":
        seen = []
        final = []
        for item in self:
            identifier = item.num if item.num else item.title
            if identifier not in seen:
                seen.append(identifier)
                final.append(item)
        return type(self)(final)

    def get_chapter(self, num: float):
        for chap in self:
            if chap.num == num:
                return chap
        return None

    @classmethod
    def from_chapter_list_v2(cls, data: dict):
        data = data["data"]
        chapters: list = data["chapters"]
        groups: list = data["groups"]
        group_data_dict = {item["id"]: item["name"] for item in groups}
        intermediate = cls()
        for item in chapters:
            chap = MangadexChapter.from_api_v2_list(item)
            for group in chap.groups:
                group.name = group_data_dict[group.id]
            intermediate.append(chap)
        return intermediate

    @classmethod
    def from_chapter_list_v1(cls, data: dict):
        return cls(MangadexChapter.from_api_v1(id, item) for id, item in data["chapter"].items())
