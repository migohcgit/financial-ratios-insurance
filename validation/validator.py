from .accounting_rules import check_balance_sheet
from .financial_rules import check_values

def validate_data(data):
    issues = []
    if not data:
        return [{"code": "NO_DATA", "message": "No recognized financial concepts were extracted.", "severity": "error", "field": None}]
    if data.get("total_assets") is None:
        issues.append({"code": "MISSING_TOTAL_ASSETS", "message": "Total assets were not recognized; some ratios cannot be calculated.", "severity": "warning", "field": "total_assets"})
    if data.get("total_liabilities") is None:
        issues.append({"code": "MISSING_TOTAL_LIABILITIES", "message": "Total liabilities were not recognized.", "severity": "warning", "field": "total_liabilities"})
    if data.get("total_equity") is None:
        issues.append({"code": "MISSING_TOTAL_EQUITY", "message": "Total equity was not recognized.", "severity": "warning", "field": "total_equity"})
    issues.extend(check_balance_sheet(data))
    issues.extend(check_values(data))
    return issues
