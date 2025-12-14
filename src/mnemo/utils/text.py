import re
from snowballstemmer import stemmer
from enum import Enum


class Language(Enum):
    EN = "en"
    ES = "es"
    RU = "ru"


WHITESPACE_RE = re.compile(r"\s+")
WORD_RE = re.compile(r"\b\w+\b")
WHITE_LIST = {"c", "go", "js", "ts", "ai", "go", "py", "sql", "css", "html", "jsx", "c#"}
BLACK_LIST = {
    Language.EN: {"the", "and", "or", "to", "of", "in", "on", "for", "with"},
    Language.EN: {"el", "la", "las", "los", "de", "en", "por"},
    Language.RU: {"на", "по", "из", "под", "над", "из-за", "ко"}
}


def normalize_text(text:str) -> str:
    text = text.lower()
    text = WHITESPACE_RE.sub(" ", text)
    text = text.strip()
    return text


def tokenize(text:str) -> list[str]:
    tokens = []
    tokens = WORD_RE.findall(text)
    tokens = [t for t in tokens if len(t) >= 1]

    return tokens


def filter_tokens(tokens: list[str], *, lang: Language = Language.EN) -> list[str]:
    filtered = []
    for t in tokens:
        if t in WHITE_LIST:
            filtered.append(t)
            continue

        if t in BLACK_LIST[lang]:
            continue

    return filtered


def stem_word(token: str) -> str:
    stemmer("english")
    return stemmer.stemWord(token)

def prepare_for_index(text: str) -> list[str]:
    normalized = normalize_text(text)
    tokens = tokenize(normalized)
    tokens = filter_tokens(tokens)
    tokens = [stem_word(t) for t in tokens]

    return tokens
