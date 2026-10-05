"""Deterministic English text statistics with offline-safe stopwords."""

import re
from collections import Counter
from functools import lru_cache

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

FALLBACK_STOPWORDS = frozenset(
    "a about above after again against all am an and any are as at be because been before being below between both but by can could did do does doing down during each few for from further had has have having he her here hers herself him himself his how i if in into is it its itself just me more most my myself no nor not now of off on once only or other our ours ourselves out over own same she should so some such than that the their theirs them themselves then there these they this those through to too under until up very was we were what when where which while who whom why will with would you your yours yourself yourselves also may might must one two use using used".split()
)
TOKENIZER = RegexpTokenizer(r"[^\W\d_]+(?:['’][^\W\d_]+)*")


@lru_cache(maxsize=1)
def english_stopwords():
    try:
        return frozenset(stopwords.words("english")) | FALLBACK_STOPWORDS
    except LookupError:
        return FALLBACK_STOPWORDS


def analyze_text(text: str) -> dict:
    """Analyze alphabetic tokens, punctuation-delimited sentences and blank-line paragraphs."""
    words = [word.casefold() for word in TOKENIZER.tokenize(text)]
    counts = Counter(words)
    meaningful = Counter(
        {
            word: count
            for word, count in counts.items()
            if word not in english_stopwords() and len(word) > 1
        }
    )
    sentences = [
        part
        for part in re.split(r"[.!?]+(?:\s+|$)", text.strip())
        if TOKENIZER.tokenize(part)
    ]
    paragraphs = [part for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]
    total = len(words)
    return {
        "word_count": total,
        "character_count": len(text),
        "characters_without_spaces": sum(not char.isspace() for char in text),
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "unique_word_count": len(counts),
        "reading_time": round(total / 200, 2),
        "average_word_length": round(sum(map(len, words)) / total, 2) if total else 0,
        "average_sentence_length": round(total / len(sentences), 2) if sentences else 0,
        "lexical_diversity": round(len(counts) / total * 100, 2) if total else 0,
        "keywords": [
            {"word": word, "count": count} for word, count in meaningful.most_common(20)
        ],
        "common_words": [
            {"word": word, "count": count} for word, count in counts.most_common(20)
        ],
        "longest_words": sorted(meaningful, key=lambda word: (-len(word), word))[:10],
        "shortest_words": sorted(meaningful, key=lambda word: (len(word), word))[:10],
    }


def search_text(text: str, query: str) -> dict:
    """Literal, case-insensitive search with bounded snippets and a full occurrence count."""
    query = query.strip()[:100]
    if not query:
        return {"query": "", "count": 0, "snippets": []}
    snippets, count = [], 0
    for match in re.finditer(re.escape(query), text, re.IGNORECASE):
        count += 1
        if len(snippets) < 30:
            snippets.append(
                {
                    "before": text[max(0, match.start() - 65) : match.start()],
                    "match": match.group(),
                    "after": text[match.end() : match.end() + 90],
                }
            )
    return {"query": query, "count": count, "snippets": snippets}
