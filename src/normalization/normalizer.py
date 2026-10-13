import re
import unicodedata
from .mappings import ALL_MAPPINGS

def normalize_label(label):
    text = unicodedata.normalize("NFKD", str(label)).encode("ascii", "ignore").decode("ascii").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())

_ALIAS_TO_CANONICAL = {}
for canonical, aliases in ALL_MAPPINGS.items():
    for alias in [canonical, *aliases]:
        _ALIAS_TO_CANONICAL[normalize_label(alias)] = canonical

def canonicalize(label):
    key = normalize_label(label)
    if key in _ALIAS_TO_CANONICAL:
        return _ALIAS_TO_CANONICAL[key]
    # Conservative matching: only exact normalized aliases are auto-mapped.
    return None

def normalize_lines(lines):
    normalized = []
    unknown = []
    for line in lines:
        label = line.get("label", "")
        canonical = canonicalize(label)
        item = {**line, "canonical_name": canonical}
        normalized.append(item)
        if canonical is None:
            unknown.append(label)
    return normalized, unknown
