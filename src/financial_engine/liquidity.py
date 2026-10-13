from .ratios import safe_divide


def current_ratio(data):
    return safe_divide(data.get("current_assets"), data.get("current_liabilities"))
