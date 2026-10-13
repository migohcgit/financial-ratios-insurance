from .thresholds import THRESHOLDS

def interpret_ratio(name, value):
    if value is None:
        return "Not interpreted: ratio could not be calculated."
    if name in {"combined_ratio", "combined_ratio_reference"}:
        if value < 1:
            return "Below 100%: underwriting result is positive before other income/expenses, subject to classification and period comparability."
        if value == 1:
            return "Approximately 100%: underwriting break-even before other income/expenses."
        return "Above 100%: underwriting result is negative before other income/expenses."
    if name in {"premium_adequacy", "premium_adequacy_with_financial_result"}:
        if value < 0:
            return "Negative premium adequacy: premiums are insufficient under this formula; review costs, claims, assumptions and classification."
        return "Non-negative premium adequacy under this formula; verify assumptions and compare across periods."
    rule = THRESHOLDS.get(name)
    if not rule:
        return "No configured interpretation rule; review in company and regulatory context."
    low, high = rule["low"], rule["high"]
    if rule["higher_is_better"]:
        if value < low:
            return "Below illustrative reference level; investigate in context."
        if value < high:
            return "Within illustrative middle range; compare with peers and prior periods."
        return "Above illustrative reference level; verify that higher is appropriate for this metric."
    if value <= low:
        return "At or below illustrative reference level; assess alongside other indicators."
    if value <= high:
        return "Elevated relative to illustrative reference level; investigate in context."
    return "Above illustrative reference level; investigate risk and company context."
