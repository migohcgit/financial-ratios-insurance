from dataclasses import dataclass, field
from typing import Any

@dataclass
class FinancialLine:
    original_label: str
    value: float | None
    canonical_name: str | None = None
    period: str | None = None
    currency: str | None = None
    source_location: str | None = None
    raw_value: Any = None

@dataclass
class FinancialStatement:
    lines: list[FinancialLine] = field(default_factory=list)
    source_file: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
