from .ratios import safe_divide


def debt_to_assets(data):
    return safe_divide(data.get("total_liabilities"), data.get("total_assets"))
