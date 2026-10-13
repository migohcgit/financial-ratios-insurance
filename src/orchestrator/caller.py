from pathlib import Path
from src.ingestion.excel_reader import read_excel
from src.ingestion.csv_reader import read_csv
from src.ingestion.pdf_reader import read_pdf
from src.normalization.normalizer import normalize_lines
from src.validation.validator import validate_data
from src.financial_engine.ratios import calculate_ratios
from src.interpretation.interpreter import interpret_ratio
from src.models.analysis_result import AnalysisResult, ValidationIssue

def _read(path, sheet_name=None):
    suffix = Path(path).suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return read_excel(path, sheet_name=sheet_name)
    if suffix == ".csv":
        return read_csv(path)
    if suffix == ".pdf":
        return read_pdf(path)
    raise ValueError(f"Unsupported file type: {suffix}. Supported: .xlsx, .xlsm, .xls, .csv, .pdf")

def analyze_file(path, sheet_name=None, period=None):
    source = str(Path(path))
    try:
        raw_lines = _read(path, sheet_name=sheet_name)
        normalized_lines, unknown = normalize_lines(raw_lines)
        # Keep the first recognized value; duplicate concepts are flagged rather than silently summed.
        data, duplicates = {}, []
        for line in normalized_lines:
            key = line.get("canonical_name")
            if key is None:
                continue
            if key in data:
                duplicates.append(key)
            else:
                data[key] = line.get("value")
        issues_raw = validate_data(data)
        for key in sorted(set(duplicates)):
            issues_raw.append({"code": "DUPLICATE_CONCEPT", "message": f"Multiple rows map to {key}; first value retained. Review source rows.", "severity": "warning", "field": key})
        if unknown:
            issues_raw.append({"code": "UNRECOGNIZED_LABELS", "message": "Some financial line labels were not recognized: " + ", ".join(sorted(set(unknown))[:20]), "severity": "info", "field": None})
        ratios = calculate_ratios(data)
        for ratio in ratios:
            ratio.interpretation = interpret_ratio(ratio.name, ratio.value)
        issues = [ValidationIssue(**i) for i in issues_raw]
        status = "error" if any(i.severity == "error" for i in issues) else ("warning" if any(i.severity == "warning" for i in issues) else "success")
        return AnalysisResult(
            source_file=source, status=status, normalized_data=data, ratios=ratios, issues=issues,
            metadata={"period": period, "sheet_name": sheet_name, "extracted_lines": len(raw_lines),
                      "recognized_concepts": len(data), "unknown_label_count": len(set(unknown)),
                      "note": "PDF text/table extraction is heuristic; scanned PDFs require OCR."}
        )
    except Exception as exc:
        return AnalysisResult(source_file=source, status="error", issues=[
            ValidationIssue(code="PIPELINE_ERROR", message=str(exc), severity="error")
        ])
