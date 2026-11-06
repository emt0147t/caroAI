"""Mutable instrumentation for one bounded Minimax search."""

from dataclasses import asdict, dataclass, field
import time


class SearchTimeBudgetExceeded(TimeoutError):
    """Raised internally when a search exceeds its optional time budget."""


@dataclass
class SearchStats:
    """Low-cardinality counters for one search; never contains board/user data."""

    nodes: int = 0
    leaves: int = 0
    root_candidates: int = 0
    generated_candidates: int = 0
    expanded_candidates: int = 0
    candidate_cap_pruned: int = 0
    alpha_beta_cutoffs: int = 0
    alpha_beta_pruned: int = 0
    branching_factor_sum: int = 0
    branching_factor_nodes: int = 0
    max_branching_factor: int = 0
    elapsed_ms: float = 0.0
    timed_out: bool = False
    shortcut: str = "none"
    deadline_ns: int | None = None
    started_ns: int = field(default_factory=time.perf_counter_ns)

    @property
    def average_branching_factor(self) -> float:
        if self.branching_factor_nodes == 0:
            return 0.0
        return self.branching_factor_sum / self.branching_factor_nodes

    @property
    def candidate_cap_pruning_rate(self) -> float:
        if self.generated_candidates == 0:
            return 0.0
        return self.candidate_cap_pruned / self.generated_candidates

    @property
    def alpha_beta_pruning_rate(self) -> float:
        considered = self.expanded_candidates + self.alpha_beta_pruned
        if considered == 0:
            return 0.0
        return self.alpha_beta_pruned / considered

    def record_branching_factor(self, count: int) -> None:
        self.branching_factor_sum += count
        self.branching_factor_nodes += 1
        self.max_branching_factor = max(self.max_branching_factor, count)

    def check_deadline(self) -> None:
        if self.deadline_ns is not None and time.perf_counter_ns() >= self.deadline_ns:
            self.timed_out = True
            raise SearchTimeBudgetExceeded("AI search time budget exceeded")

    def start_budget(self, time_budget_ms: float | None) -> None:
        if time_budget_ms is None:
            self.deadline_ns = None
            return
        if time_budget_ms < 0:
            raise ValueError("time_budget_ms must be non-negative")
        self.deadline_ns = time.perf_counter_ns() + int(time_budget_ms * 1_000_000)

    def to_dict(self) -> dict:
        """Return JSON-safe counters and explicitly derived rates."""
        values = asdict(self)
        values.pop("deadline_ns", None)
        values.pop("started_ns", None)
        values.update({
            "average_branching_factor": self.average_branching_factor,
            "candidate_cap_pruning_rate": self.candidate_cap_pruning_rate,
            "alpha_beta_pruning_rate": self.alpha_beta_pruning_rate,
        })
        return values
