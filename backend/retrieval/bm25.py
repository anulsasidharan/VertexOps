"""BM25 lexical scorer for hybrid retrieval."""

import math
import re


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class BM25Scorer:
    """Okapi BM25 over an in-memory corpus.

    Corpus is the list of candidate texts; scores are computed per-query.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._corpus: list[list[str]] = []
        self._df: dict[str, int] = {}
        self._avgdl: float = 0.0
        self._n: int = 0

    def fit(self, texts: list[str]) -> "BM25Scorer":
        self._corpus = [_tokenize(t) for t in texts]
        self._n = len(self._corpus)
        self._avgdl = sum(len(doc) for doc in self._corpus) / self._n if self._n else 0.0
        self._df = {}
        for doc in self._corpus:
            for term in set(doc):
                self._df[term] = self._df.get(term, 0) + 1
        return self

    def score(self, query: str) -> list[float]:
        """Return BM25 score for each document in the fitted corpus."""
        if self._n == 0:
            return []
        q_terms = _tokenize(query)
        scores = []
        for doc in self._corpus:
            dl = len(doc)
            tf_map: dict[str, int] = {}
            for term in doc:
                tf_map[term] = tf_map.get(term, 0) + 1
            s = 0.0
            for term in q_terms:
                tf = tf_map.get(term, 0)
                df = self._df.get(term, 0)
                if df == 0:
                    continue
                idf = math.log((self._n - df + 0.5) / (df + 0.5) + 1)
                num = tf * (self.k1 + 1)
                denom = tf + self.k1 * (1 - self.b + self.b * dl / self._avgdl)
                s += idf * num / denom
            scores.append(s)
        return scores
