from .ratios import safe_divide


def net_profit_margin(data):
    return safe_divide(data.get("net_income"), data.get("revenue"))
