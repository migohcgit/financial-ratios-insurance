from pathlib import Path
import pandas as pd
from .common import parse_number

def read_excel(path, sheet_name=None):
    path = Path(path)
    df = pd.read_excel(path, sheet_name=sheet_name if sheet_name else 0, header=None, dtype=object)
    if isinstance(df, dict):
        # Excel sheet unspecified: first sheet only for predictable behavior.
        df = next(iter(df.values()))
    lines = []
    for idx, row in df.iterrows():
        vals = list(row)
        if not vals:
            continue
        label = next((str(v).strip() for v in vals if pd.notna(v) and str(v).strip()), "")
        if not label:
            continue
        numeric = [parse_number(v) for v in vals[1:]]
        value = next((v for v in numeric if v is not None), parse_number(vals[0]))
        if value is not None:
            lines.append({"label": label, "value": value, "source_location": f"row:{idx+1}"})
    return lines
