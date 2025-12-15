from enum import Enum


class Language(Enum):
    EN = "en"
    ES = "es"
    RU = "ru"

    @property
    def label(self) -> str:
        return {
            "en": "English",
            "es": "Spanish",
            "ru": "Russian"
        }[self.value]

    @classmethod
    def values(cls) -> list[str]:
        return [l.value for l in cls]

class Source(Enum):
    APPLE = "apple"
    BEAR = "bear"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]
