from .ratios import safe_divide


def claims_ratio(claims_incurred, net_premiums_earned):
    return safe_divide(claims_incurred, net_premiums_earned)


def expense_ratio(underwriting_expenses, net_premiums_earned):
    return safe_divide(underwriting_expenses, net_premiums_earned)


def combined_ratio(claims_incurred, underwriting_expenses, net_premiums_earned):
    claims = claims_ratio(claims_incurred, net_premiums_earned)
    expenses = expense_ratio(underwriting_expenses, net_premiums_earned)
    return None if claims is None or expenses is None else claims + expenses
