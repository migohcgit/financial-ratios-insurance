from .ratios import safe_divide
from src.models.analysis_result import RatioResult


def calculate_insurer_ratios(data):
    out = []
    def add(name, numerator, denominator, formula, note=None):
        value = safe_divide(numerator, denominator)
        # Omit the ratio if any required input is unavailable or denominator is zero.
        if value is None:
            return None
        out.append(RatioResult(name=name, value=value, formula=formula,
                               status="calculated", notes=[note] if note else []))
        return value
    def get(key): return data.get(key)
    def sum_if_all(*values): return sum(values) if all(v is not None for v in values) else None

    # Liquidity ratios: current assets/current liabilities are not inferred from totals.
    add("liquidity_current", get("current_assets"), get("current_liabilities"), "Current assets / Current liabilities", "Requires an explicit current-assets and current-liabilities classification.")
    add("liquidity_available_to_exigible", get("available_assets"), get("exigible_liabilities"), "Available assets / Exigible liabilities", "Available assets are approximated only by recognized cash and equivalents in this version.")
    add("liquidity_current_to_exigible", get("current_assets"), get("exigible_liabilities"), "Current assets / Exigible liabilities")
    add("liquidity_current_to_technical_reserves", get("current_assets"), get("technical_reserves"), "Current assets / Technical reserves")
    add("liquidity_investments_to_current_liabilities", get("financial_investments"), get("current_liabilities"), "Financial investments / Current liabilities")

    add("solvency_total_assets_to_liabilities", get("total_assets"), get("total_liabilities"), "Total assets / Total liabilities")
    nonfixed_assets = None if get("total_assets") is None or get("fixed_assets") is None else get("total_assets") - get("fixed_assets")
    excluded_reserves = sum_if_all(get("preventive_reserves"), get("course_risk_reserves"), get("pending_claims_reserves"))
    denom = None if get("total_liabilities") is None or excluded_reserves is None else get("total_liabilities") - excluded_reserves
    add("solvency_adjusted_assets", nonfixed_assets, denom, "(Total assets - Fixed assets) / (Total liabilities - preventive reserves - course-risk reserves - pending-claims reserves)", "Not calculated unless all reserve classifications are present.")
    equity_plus_preventive = sum_if_all(get("total_equity"), get("preventive_reserves"))
    add("solvency_retained_premiums_to_equity", get("retained_premiums"), equity_plus_preventive, "Retained premiums / (Equity + Preventive reserves)")
    gross_requirement = sum_if_all(get("minimum_guarantee_capital"), get("preventive_reserves"))
    capital_backing = sum_if_all(get("total_equity"), get("preventive_reserves"))
    add("solvency_capital_to_gross_requirement", capital_backing, gross_requirement, "(Equity + Preventive reserves) / Gross solvency requirement (minimum guarantee capital + preventive reserves)")
    add("guarantee_capital_coverage", get("guarantee_capital"), get("minimum_guarantee_capital"), "Guarantee capital / Minimum guarantee capital")
    add("solvency_margin_to_guarantee_capital", get("solvency_margin"), get("guarantee_capital"), "Solvency margin / Guarantee capital")
    claims_and_recoveries = sum_if_all(get("retained_claims"), get("reinsurance_claims_recovered"))
    add("preventive_reserves_to_claims", get("preventive_reserves"), claims_and_recoveries, "Preventive reserves / (Retained claims + Reinsurance recoveries)")
    numerator_assets_backing = None if any(get(k) is None for k in ("financial_investments", "premiums_receivable", "deferred_commissions")) else get("financial_investments") + get("premiums_receivable") - get("deferred_commissions")
    denominator_assets_backing = sum_if_all(get("technical_reserves"), get("contractual_obligations"), get("retirement_reserve"))
    add("investment_backing_contractual_obligations", numerator_assets_backing, denominator_assets_backing, "(Investments + Premiums receivable - Deferred commissions) / (Technical reserves + Contractual obligations + Retirement reserve)")
    add("leverage_liabilities_to_equity", get("total_liabilities"), get("total_equity"), "Total liabilities / Equity")
    add("leverage_technical_reserves_to_equity", get("technical_reserves"), get("total_equity"), "Technical reserves / Equity")
    add("leverage_reserve_change_to_equity", get("technical_reserves_change"), get("total_equity"), "Change in technical reserves / Equity", "Requires prior-period technical reserves.")

    direct_premiums = get("direct_premiums")
    add("operating_cost_ratio", get("operating_expenses_net"), direct_premiums, "Net operating expenses / Direct premiums")
    add("acquisition_cost_ratio", get("acquisition_costs"), get("retained_premiums"), "Net acquisition costs / Retained premiums")
    add("claims_ratio", get("claims_incurred"), get("net_premiums_earned"), "Net claims cost / Net earned retained premiums")
    op = safe_divide(get("operating_expenses_net"), direct_premiums)
    acq = safe_divide(get("acquisition_costs"), get("retained_premiums"))
    claims = safe_divide(get("claims_incurred"), get("net_premiums_earned"))
    combined = sum([op, acq, claims]) if all(x is not None for x in (op, acq, claims)) else None
    if combined is not None:
        out.append(RatioResult("combined_ratio_reference", combined,
            "Operating cost ratio + Acquisition cost ratio + Claims ratio",
            status="calculated",
            notes=["The three components use the denominators specified in the supplied reference."]))
        out.append(RatioResult("premium_adequacy", 1 - combined,
            "1 - Combined ratio", status="calculated"))
    fin_ratio = safe_divide(get("investment_financial_result"), get("net_premiums_earned"))
    financial_adequacy = None if combined is None or fin_ratio is None else 1 - (combined - fin_ratio)
    if financial_adequacy is not None:
        out.append(RatioResult("premium_adequacy_with_financial_result", financial_adequacy,
            "1 - (Combined ratio - Financial result / Net earned retained premiums)",
            status="calculated"))

    add("ceded_premium_ratio", get("ceded_premiums"), get("gross_premiums_written"), "Ceded premiums / Written premiums")
    add("retention_ratio", get("retained_premiums"), get("gross_premiums_written"), "Retained premiums / Written premiums")
    add("ceded_reinsurance_commission_ratio", get("reinsurance_commissions_ceded"), get("ceded_premiums"), "Ceded reinsurance commissions / Ceded premiums")
    add("excess_loss_cover_ratio", get("excess_loss_cover"), get("retained_premiums"), "Excess-of-loss cover / Retained premiums")
    ceded_plus_excess = sum_if_all(get("ceded_earned_premiums"), get("excess_loss_cover"))
    add("nonproportional_recovery_ratio", get("claims_recovered_nonproportional"), ceded_plus_excess, "Non-proportional claims recovered / (Ceded earned premiums + Excess-of-loss cover)", "Ceded earned premiums are not identified separately in the supplied statements.")
    recovery_and_commissions = sum_if_all(get("claims_recovered_nonproportional"), get("reinsurance_commissions_recovered"))
    add("reinsurance_recovery_ratio", recovery_and_commissions, get("ceded_premiums"), "(Claims recovered + Reinsurance commissions recovered) / Ceded premiums")
    net_reinsurance_result = None if any(get(k) is None for k in ("ceded_earned_premiums", "excess_loss_cover", "reinsurance_commissions_ceded", "claims_recovered_nonproportional")) else get("ceded_earned_premiums") + get("excess_loss_cover") - get("reinsurance_commissions_ceded") - get("claims_recovered_nonproportional")
    add("reinsurer_profit_ratio", net_reinsurance_result, ceded_plus_excess, "(Ceded earned premiums + Excess-of-loss cover - Ceded commissions - Claims recovered) / (Ceded earned premiums + Excess-of-loss cover)")
    retained_claims = get("retained_claims")
    add("retained_claims_ratio", retained_claims, get("net_premiums_earned"), "Retained claims / Net earned retained premiums")

    add("return_on_equity", get("net_income"), get("total_equity"), "Net income / Equity")
    add("return_on_paid_capital", get("net_income"), get("paid_in_capital"), "Net income / Paid-in capital")
    capital_plus_reserves = sum_if_all(get("paid_in_capital"), get("capital_reserve"))
    add("return_on_paid_capital_plus_reserve", get("net_income"), capital_plus_reserves, "Net income / (Paid-in capital + Capital reserve)")
    add("real_growth_capital_reserves", get("real_growth_preventive_reserves_plus_equity_plus_catastrophe_reserves"), 1, "Real growth in preventive reserves + equity + catastrophe reserves", "Requires current/prior-year balances and inflation adjustment; not derivable from this single-year pair of statements.")
    direct_premiums_for_margin = get("direct_premiums")
    add("net_margin_direct_premiums", get("net_income"), direct_premiums_for_margin, "Net income / Direct premiums")
    add("net_margin_written_premiums", get("net_income"), get("gross_premiums_written"), "Net income / Written premiums")
    add("net_margin_retained_premiums", get("net_income"), get("retained_premiums"), "Net income / Retained premiums")
    add("technical_margin", get("underwriting_result"), get("net_premiums_earned"), "Technical result / Net earned retained premiums")
    add("net_income_to_working_capital", get("net_income"), get("working_capital"), "Net income / Working capital", "Requires a defined current-assets/current-liabilities classification.")
    add("return_on_assets", get("net_income"), get("total_assets"), "Net income / Total assets")
    adjusted_profit = None if any(get(k) is None for k in ("net_income", "change_in_surplus", "change_in_capital_reserves")) else get("net_income") + get("change_in_surplus") + get("change_in_capital_reserves")
    add("adjusted_roa", adjusted_profit, get("total_assets"), "(Net income + Change in surplus + Change in capital reserves) / Total assets")
    add("adjusted_roe", adjusted_profit, get("total_equity"), "(Net income + Change in surplus + Change in capital reserves) / Equity")
    add("adjusted_return_on_written_premiums", adjusted_profit, get("gross_premiums_written"), "(Net income + Change in surplus + Change in capital reserves) / Written premiums")
    return out
