#Coordinate aware PDF extraction for one and two column financial statements.
import re
import pdfplumber
from .common import parse_number

_NUMBER_AT_END = re.compile( r"(\(?-?[$€£]?\s*\d[\d,. ]*\d\)?|\(?-?[$€£]?\d\)?)\s*$")


def _line_to_item(text, location):
    text = " ".join(text.split()).strip()
    match = _NUMBER_AT_END.search(text)
    if not match:
        return None
    value = parse_number(match.group(1))
    label = text[:match.start()].strip(" .:-")
    if not label or value is None:
        return None
    return {"label": label, "value": value, "source_location": location}


def read_pdf(path):
    #Extract lines by page coordinates to avoid mixing left/right balance-sheet columns.

    #This remains heuristic: layouts with multiple values in a single cell or scanned
    #pages need OCR or manual review.
    
    lines = []
    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(x_tolerance=2, y_tolerance=3, keep_blank_chars=False)
            if words:
                rows = {}
                for word in words:
                    key = round(float(word["top"]), 1)
                    rows.setdefault(key, []).append(word)
                # A two-column balance sheet commonly has its first amount around
                # 38% of page width and its second around 90%. Income statements often
                # have only one amount column near 70-90% of page width.
                numeric_word = re.compile(r"^\(?-?[$€£]?\d[\d,.]*\)?$")
                left_amount_count = sum(
                    1 for row in rows.values() for w in row
                    if page.width * 0.25 <= float(w["x0"]) <= page.width * 0.48
                    and numeric_word.match(w["text"].replace(" ", ""))
                )
                has_left_amount = left_amount_count >= 3
                for row_idx, row_words in enumerate(rows.values(), start=1):
                    if not has_left_amount:
                        text = " ".join(w["text"] for w in sorted(row_words, key=lambda x: x["x0"]))
                        item = _line_to_item(text, f"page:{page_num},line:{row_idx}")
                        if item:
                            lines.append(item)
                        continue
                    split_x = page.width * 0.455
                    left = [w for w in row_words if float(w["x0"]) < split_x]
                    right = [w for w in row_words if float(w["x0"]) >= split_x]
                    for side_name, side_words in (("left", left), ("right", right)):
                        if not side_words:
                            continue
                        text = " ".join(w["text"] for w in sorted(side_words, key=lambda x: x["x0"]))
                        item = _line_to_item(text, f"page:{page_num},line:{row_idx},{side_name}")
                        if item:
                            lines.append(item)
                if lines:
                    continue
            # Fallback for PDFs whose word coordinates are unavailable.
            text = page.extract_text() or ""
            for row_idx, line in enumerate(text.splitlines(), start=1):
                item = _line_to_item(line, f"page:{page_num},line:{row_idx}")
                if item:
                    lines.append(item)
    if not lines:
        raise ValueError("No financial line items could be extracted. The PDF may be scanned or its layout may not be supported.")
    return lines
