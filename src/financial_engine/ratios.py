from src.models.analysis_result import RatioResult

def safe_divide(numerator, denominator):
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator

def calculate_ratios(data):
    results = []
    def add(name, value, formula, notes=None):
        status = "calculated" if value is not None else "not_calculable"
        results.append(RatioResult(name=name, value=value, formula=formula, status=status, notes=notes or []))

    add("current_ratio", safe_divide(data.get("current_assets"), data.get("current_liabilities")),
        "Current assets / Current liabilities", ["Not meaningful if current liabilities are unavailable or zero."])
    add("cash_ratio", safe_divide(data.get("cash_and_equivalents"), data.get("current_liabilities")),
        "Cash and cash equivalents / Current liabilities")
    add("debt_to_assets", safe_divide(data.get("total_liabilities"), data.get("total_assets")),
        "Total liabilities / Total assets")
    add("equity_ratio", safe_divide(data.get("total_equity"), data.get("total_assets")),
        "Total equity / Total assets")
    add("net_profit_margin", safe_divide( data.get("net_income"), data.get("net_premiums_earned") ),"Net income / Net premiums earned")
    add("return_on_assets", safe_divide(data.get("net_income"), data.get("total_assets")),
        "Net income / Total assets (period-end proxy; average assets preferred)")
    add("return_on_equity", safe_divide(data.get("net_income"), data.get("total_equity")),
        "Net income / Total equity (period-end proxy; average equity preferred)")

    premiums = data.get("net_premiums_earned")
    claims = data.get("claims_incurred")
    expenses = data.get("underwriting_expenses")
    if expenses is None:
        acquisition = data.get("acquisition_costs")
        expenses = acquisition
    add("claims_ratio", safe_divide(claims, premiums), "Claims incurred / Net premiums earned")
    add("expense_ratio", safe_divide(expenses, premiums), "Underwriting expenses / Net premiums earned")
    combined = None
    cr = safe_divide(claims, premiums)
    er = safe_divide(expenses, premiums)
    if cr is not None and er is not None:
        combined = cr + er
    add("combined_ratio", combined, "(Claims incurred + Underwriting expenses) / Net premiums earned",
        ["Only calculated when both claims and underwriting expenses are available; classification must be verified."])
    add("investment_yield", safe_divide(data.get("investment_income"), data.get("investments")),
        "Investment income / Investments (period-end proxy; average investments preferred)")
    return results
