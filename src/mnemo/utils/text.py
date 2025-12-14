import re
import snowballstemmer

from mnemo.enums import Language



WHITESPACE_RE = re.compile(r"\s+")
WORD_RE = re.compile(r"\b\w+\b")
WHITE_LIST = {"c", "go", "js", "ts", "ai", "py", "sql", "css", "html", "jsx", "c#"}
BLACK_LIST = {
    Language.EN: {"the", "and", "or", "to", "of", "in", "on", "for", "with"},
    Language.ES: {"el", "la", "las", "los", "de", "en", "por"},
    Language.RU: {"на", "по", "из", "под", "над", "из-за", "ко"}
}

STEMMERS = {
    Language.EN: snowballstemmer.stemmer("english"),
    Language.ES: snowballstemmer.stemmer("spanish"),
    Language.RU: snowballstemmer.stemmer("russian"),
}



def normalize_text(text:str) -> str:
    text = text.lower()
    text = WHITESPACE_RE.sub(" ", text)
    text = text.strip()
    return text


def tokenize(text:str) -> list[str]:
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
        filtered.append(t)

    return filtered


def stem_word(token: str, *, lang: Language = Language.EN) -> str:
    stemmer = STEMMERS.get(lang)
    if not stemmer:
        return token
    return stemmer.stemWord(token)

def prepare_for_index(text: str, languages: set[Language]) -> list[tuple[str, int]]:
    normalized = normalize_text(text)
    base_tokens = tokenize(normalized)
    all_tokens = []

    for lang in languages:
        filtered = filter_tokens(base_tokens, lang=lang)
        stemmed = [stem_word(t, lang=lang) for t in filtered]
        for pos, token in enumerate(stemmed):
            all_tokens.append((token, pos))

    return all_tokens
