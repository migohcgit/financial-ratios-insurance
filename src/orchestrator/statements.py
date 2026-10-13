#Coordinate a balance sheet and income statement through the existing pipeline
from pathlib import Path
from src.orchestrator.caller import _read
from src.normalization.normalizer import normalize_lines
from src.validation.validator import validate_data
from src.financial_engine.ratios import calculate_ratios
from src.financial_engine.insurer_ratios import calculate_insurer_ratios
from src.interpretation.interpreter import interpret_ratio
from src.models.analysis_result import AnalysisResult, ValidationIssue

INCOME_KEYS = {
    "revenue", "gross_premiums_written", "ceded_premiums", "retained_premiums",
    "direct_premiums", "net_premiums_earned", "premiums_earned", "net_income",
    "investment_income", "investment_financial_result", "underwriting_result",
    "acquisition_costs", "claims_incurred", "gross_claims_incurred",
    "operating_expenses_net", "reinsurance_commissions_ceded", "excess_loss_cover",
    "claims_recovered_nonproportional", "technical_reserves_change",
}


def _extract(path, sheet_name=None):
    raw = _read(path, sheet_name=sheet_name)
    normalized, unknown = normalize_lines(raw)
    data, duplicates = {}, []
    sources = {}
    for row in normalized:
        key = row.get("canonical_name")
        value = row.get("value")
        if key is None or value is None:
            continue
        if key in data:
            duplicates.append((key, sources[key], row.get("source_location")))
            continue
        data[key] = value
        sources[key] = row.get("source_location")
    return raw, data, duplicates, unknown


def analyze_statements(balance_path, income_path, balance_sheet_name=None, income_statement_name=None,
                       balance_sheet_sheet=None, income_statement_sheet=None):
    """Analyze both statement files together, with statement-aware value precedence."""
    balance_raw, balance_data, balance_dupes, balance_unknown = _extract(balance_path, balance_sheet_sheet)
    income_raw, income_data, income_dupes, income_unknown = _extract(income_path, income_statement_sheet)
    data = dict(balance_data)
    # Income statement values take precedence for flow variables such as premiums and profit.
    for key in INCOME_KEYS:
        if key in income_data:
            data[key] = income_data[key]
    # A disclosed cash-and-equivalents line supports both general cash analysis
    # and the insurer reference's available-assets ratio.
    if "cash_and_equivalents" not in data and "available_assets" in data:
        data["cash_and_equivalents"] = data["available_assets"]
    issues_raw = validate_data(data)
    for key, loc1, loc2 in balance_dupes + income_dupes:
        issues_raw.append({"code": "DUPLICATE_CONCEPT", "message": f"Multiple rows map to {key} ({loc1}, {loc2}); first value retained. Review the source.", "severity": "warning", "field": key})
    if balance_unknown or income_unknown:
        labels = sorted(set(balance_unknown + income_unknown))
        issues_raw.append({"code": "UNRECOGNIZED_LABELS", "message": "Some labels were not recognized: " + ", ".join(labels[:25]), "severity": "info", "field": None})
    generic = calculate_ratios(data)
    # Keep useful general ratios without duplicating insurer-specific definitions.
    generic_names = {"current_ratio", "cash_ratio", "debt_to_assets", "equity_ratio", "net_profit_margin", "investment_yield"}
    ratios = [r for r in generic if r.name in generic_names] + calculate_insurer_ratios(data)
    for ratio in ratios:
        ratio.interpretation = interpret_ratio(ratio.name, ratio.value)
    issues = [ValidationIssue(**item) for item in issues_raw]
    status = "error" if any(i.severity == "error" for i in issues) else ("warning" if any(i.severity == "warning" for i in issues) else "success")
    return AnalysisResult(
        source_file=f"Balance: {balance_sheet_name or Path(balance_path).name}; Income statement: {income_statement_name or Path(income_path).name}",
        status=status, normalized_data=data, ratios=ratios, issues=issues,
        metadata={"period": "FY2025 (detected from supplied files; editable in UI)",
                  "balance_sheet_file": balance_sheet_name or Path(balance_path).name,
                  "income_statement_file": income_statement_name or Path(income_path).name,
                  "balance_extracted_lines": len(balance_raw), "income_extracted_lines": len(income_raw),
                  "recognized_concepts": len(data), "unknown_label_count": len(set(balance_unknown + income_unknown)),
                  "note": "PDF extraction is coordinate-aware but heuristic. Review mappings and duplicate warnings before relying on results."}
    )
