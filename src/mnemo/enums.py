from enum import Enum


class Language(Enum):
    EN = ("en", "English")
    ES = ("es", "Spanish")
    RU = ("ru", "Russian")

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def values(cls) -> list[str]:
        return [l.value for l in cls]

class Source(Enum):
    APPLE = "apple"
    BEAR = "bear"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]
