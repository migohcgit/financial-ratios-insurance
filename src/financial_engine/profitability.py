from .ratios import safe_divide


def return_on_assets(data):
    return safe_divide(data.get("net_income"), data.get("total_assets"))


def return_on_equity(data):
    return safe_divide(data.get("net_income"), data.get("total_equity"))
