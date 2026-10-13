def check_values(data):
    issues = []
    for key, value in data.items():
        if value is not None and value < 0 and key in {"total_assets", "current_assets", "total_liabilities", "total_equity"}:
            issues.append({"code": "NEGATIVE_BALANCE", "message": f"{key} is negative ({value}). Verify the source.", "severity": "warning", "field": key})
    return issues
