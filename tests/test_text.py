from mnemo.utils import text
from mnemo.enums import Language


def test_normalize_text():
    raw = "  Hello   WORLD\n\n  мир  "
    assert text.normalize_text(raw) == "hello world мир"


def test_tokenize():
    assert text.tokenize("hello, world! 123") == ["hello", "world", "123"]
    assert text.tokenize("ai/ml") == ["ai", "ml"]


def test_filter_tokens_english():
    tokens = ["the", "ai", "neural", "and", "py"]
    assert text.filter_tokens(tokens, lang=Language.EN) == ["ai", "neural", "py"]


def test_filter_tokens_spanish():
    tokens = ["el", "python", "de", "datos"]
    assert text.filter_tokens(tokens, lang=Language.ES) == ["python", "datos"]


def test_filter_tokens_russian():
    tokens = ["на", "python", "по", "данным"]
    assert text.filter_tokens(tokens, lang=Language.RU) == ["python", "данным"]


def test_stem_word():
    assert text.stem_word("running", lang=Language.EN) == "run"
    assert text.stem_word("corriendo", lang=Language.ES) == "corr"
    assert text.stem_word("бегущий", lang=Language.RU) == "бегущ"


def test_prepare_for_index_single_language():
    res = text.prepare_for_index("Python and ai", {Language.EN})
    tokens = [t[0] for t in res]
    assert "python" in tokens
    assert "ai" in tokens
    assert "and" not in tokens


def test_prepare_for_index_multi_lang():
    res = text.prepare_for_index("Python", {Language.EN, Language.ES})
    stems = [t[0] for t in res]
    assert stems.count("python") == 1


def test_prepare_for_search():
    q = text.prepare_for_search("the python and ai", {Language.EN})
    assert "python" in q
    assert "ai" in q
    assert "the" not in q
    assert "and" not in q
