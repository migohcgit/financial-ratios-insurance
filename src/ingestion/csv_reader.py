from pathlib import Path
import csv
import pandas as pd
from .common import parse_number

def read_csv(path):
    path = Path(path)
    # pandas handles common delimiters and encoding, fallback for latin-1.
    try:
        df = pd.read_csv(path, header=None, dtype=object, sep=None, engine="python", encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, header=None, dtype=object, sep=None, engine="python", encoding="latin-1")
    lines = []
    for idx, row in df.iterrows():
        vals = list(row)
        if not vals:
            continue
        label = next((str(v).strip() for v in vals if pd.notna(v) and str(v).strip()), "")
        if not label:
            continue
        value = next((n for n in (parse_number(v) for v in vals[1:]) if n is not None), None)
        if value is None:
            value = parse_number(vals[0])
        if value is not None:
            lines.append({"label": label, "value": value, "source_location": f"row:{idx+1}"})
    return lines
