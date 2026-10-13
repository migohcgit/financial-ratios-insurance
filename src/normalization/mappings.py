from src.models.assets import ASSETS_MAPPINGS
from src.models.liabilities import LIABILITIES_MAPPINGS
from src.models.equity import EQUITY_MAPPINGS
from src.models.revenue import REVENUE_MAPPINGS
from src.models.expenses import EXPENSES_MAPPINGS

ALL_MAPPINGS = {}
for group in (ASSETS_MAPPINGS, LIABILITIES_MAPPINGS, EQUITY_MAPPINGS, REVENUE_MAPPINGS, EXPENSES_MAPPINGS):
    ALL_MAPPINGS.update(group)
