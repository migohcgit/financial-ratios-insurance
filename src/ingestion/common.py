import math
import re

def parse_number(value):
    #Parse common financial number formats; return None if not numeric
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(float(value)) else None
    s = str(value).strip()
    if not s or s.lower() in {"-", "—", "n/a", "na", "null", "none", "nm"}:
        return None
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("() ").replace("$", "").replace("€", "").replace("£", "").replace("¥", "")
    s = re.sub(r"(?i)\b(usd|mxn|eur|gbp)\b", "", s).replace("%", "").replace(" ", "")
    # Interpret 1,234.56 as US style; 1.234,56 as European style.
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        tail = s.rsplit(",", 1)[-1]
        s = s.replace(",", ".") if len(tail) in (1, 2) else s.replace(",", "")
    try:
        number = float(s)
        return -number if negative else number
    except ValueError:
        return None
