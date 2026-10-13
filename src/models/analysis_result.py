from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: str = "warning"
    field: str | None = None

    def to_dict(self):
        return asdict(self)

@dataclass
class RatioResult:
    name: str
    value: float | None
    formula: str
    interpretation: str = "Not interpreted"
    status: str = "calculated"
    notes: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

@dataclass
class AnalysisResult:
    source_file: str
    status: str
    normalized_data: dict[str, Any] = field(default_factory=dict)
    ratios: list[RatioResult] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "source_file": self.source_file,
            "status": self.status,
            "normalized_data": self.normalized_data,
            "ratios": [r.to_dict() for r in self.ratios],
            "issues": [i.to_dict() for i in self.issues],
            "metadata": self.metadata,
        }
