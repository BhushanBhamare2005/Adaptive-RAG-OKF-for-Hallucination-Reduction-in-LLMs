import hashlib
import math
import re


class LocalHashEmbeddingProvider:
    name = "local"
    model = "hash-v1"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * 384
        for token in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for position in range(0, 12):
                index = int.from_bytes(digest[position * 2:position * 2 + 2], "big") % 384
                vector[index] += 1.0 if digest[position] % 2 else -1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            return [value / norm for value in vector]
        return vector


embedding_provider = LocalHashEmbeddingProvider()
