def check_balance_sheet(data, tolerance=0.02):
    #Check Assets ~= Liabilities + Equity when all three totals are available.
    issues = []
    assets, liabilities, equity = (data.get(k) for k in ("total_assets", "total_liabilities", "total_equity"))
    if all(v is not None for v in (assets, liabilities, equity)):
        difference = assets - liabilities - equity
        allowed = max(abs(assets) * tolerance, 1.0)
        if abs(difference) > allowed:
            issues.append({
                "code": "BALANCE_SHEET_NOT_BALANCED",
                "message": f"Assets differ from liabilities plus equity by {difference:.2f}.",
                "severity": "warning",
                "field": "total_assets",
            })
    return issues
