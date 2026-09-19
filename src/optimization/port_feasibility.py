"""
FreightMind AI — Port Feasibility Engine
src/optimization/port_feasibility.py

Hard-constraint checker:
  If vessel_draft > port_max_draft → NOT FEASIBLE
  If vessel_LOA   > port_max_loa   → NOT FEASIBLE
  If vessel_beam  > port_max_beam  → NOT FEASIBLE
  If cargo_qty    > vessel_capacity → NOT FEASIBLE

Returns a structured FeasibilityResult per vessel × port combination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.utils.config import get_all_ports, get_all_vessels, get_port_config
from src.utils.logger import logger


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class ConstraintCheck:
    """Result of a single constraint check."""
    name: str
    vessel_value: float | None
    port_limit: float | None
    passed: bool
    message: str

    @property
    def status_label(self) -> str:
        return "[PASS]" if self.passed else "[FAIL]"


@dataclass
class FeasibilityResult:
    """Complete feasibility assessment for one vessel at one port."""
    vessel_type: str
    port_id: str
    port_name: str
    feasible: bool
    checks: list[ConstraintCheck] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    cargo_feasible: bool = True

    def summary(self) -> str:
        status = "[FEASIBLE]" if self.feasible else "[NOT FEASIBLE]"
        failed = [c.name for c in self.checks if not c.passed]
        return (
            f"{status} | {self.vessel_type} @ {self.port_name} | "
            + (f"Failed: {failed}" if failed else "All constraints passed")
        )


# ── Core Engine ───────────────────────────────────────────────────────────────

class PortFeasibilityEngine:
    """
    Evaluates whether a vessel can physically operate at a port.

    Design: Fail-fast on hard constraints. Soft constraints generate warnings.
    Port data quality flags are surfaced in warnings (not errors).
    """

    def __init__(self) -> None:
        self._port_configs = {p["id"]: p for p in get_all_ports()}
        self._vessel_configs = {v["type"]: v for v in get_all_vessels()}

    def check(
        self,
        vessel_type: str,
        port_id: str,
        cargo_quantity_mt: float = 0.0,
    ) -> FeasibilityResult:
        """
        Run all feasibility checks for a vessel at a port.

        Args:
            vessel_type:       e.g. 'Panamax'
            port_id:           e.g. 'paradip'
            cargo_quantity_mt: Required cargo to load/discharge (MT)

        Returns:
            FeasibilityResult with all checks and overall feasibility.
        """
        vessel = self._vessel_configs.get(vessel_type)
        port = self._port_configs.get(port_id)

        if vessel is None:
            raise ValueError(f"Unknown vessel type: {vessel_type}")
        if port is None:
            raise ValueError(f"Unknown port ID: {port_id}")

        checks: list[ConstraintCheck] = []
        warnings: list[str] = []

        # ── 1. Draft check ────────────────────────────────────────────────────
        v_draft = vessel["draft_laden_m"]
        p_draft = port.get("max_draft_m")
        draft_quality = port.get("data_quality", {}).get("max_draft", "unknown")

        if p_draft is None:
            draft_passed = True
            draft_msg = "Port max draft: UNAVAILABLE — cannot verify"
            warnings.append("Draft data unavailable for this port")
        else:
            draft_passed = v_draft <= p_draft
            draft_msg = (
                f"Vessel draft {v_draft}m {'≤' if draft_passed else '>'} "
                f"port max {p_draft}m"
            )
            if draft_quality == "estimated":
                warnings.append(f"Port max draft is estimated, not officially verified")

        checks.append(ConstraintCheck(
            name="Draft",
            vessel_value=v_draft,
            port_limit=p_draft,
            passed=draft_passed,
            message=draft_msg,
        ))

        # ── 2. LOA check ──────────────────────────────────────────────────────
        v_loa = vessel["loa_m"]
        p_loa = port.get("max_loa_m")
        loa_quality = port.get("data_quality", {}).get("max_loa", "unknown")

        if p_loa is None:
            loa_passed = True
            loa_msg = "Port max LOA: UNAVAILABLE — cannot verify"
            warnings.append("LOA data unavailable for this port")
        else:
            loa_passed = v_loa <= p_loa
            loa_msg = (
                f"Vessel LOA {v_loa}m {'≤' if loa_passed else '>'} "
                f"port max {p_loa}m"
            )
            if loa_quality == "estimated":
                warnings.append("Port max LOA is estimated")

        checks.append(ConstraintCheck(
            name="LOA",
            vessel_value=v_loa,
            port_limit=p_loa,
            passed=loa_passed,
            message=loa_msg,
        ))

        # ── 3. Beam check ─────────────────────────────────────────────────────
        v_beam = vessel["beam_m"]
        p_beam = port.get("max_beam_m")
        beam_quality = port.get("data_quality", {}).get("max_beam", "unknown")

        if p_beam is None:
            beam_passed = True
            beam_msg = "Port max beam: UNAVAILABLE — cannot verify"
            warnings.append("Beam data unavailable for this port")
        else:
            beam_passed = v_beam <= p_beam
            beam_msg = (
                f"Vessel beam {v_beam}m {'≤' if beam_passed else '>'} "
                f"port max {p_beam}m"
            )
            if beam_quality == "estimated":
                warnings.append("Port max beam is estimated")

        checks.append(ConstraintCheck(
            name="Beam",
            vessel_value=v_beam,
            port_limit=p_beam,
            passed=beam_passed,
            message=beam_msg,
        ))

        # ── 4. Cargo capacity check ───────────────────────────────────────────
        cargo_feasible = True
        if cargo_quantity_mt > 0:
            v_capacity = vessel["cargo_capacity_mt"]
            cargo_feasible = cargo_quantity_mt <= v_capacity
            checks.append(ConstraintCheck(
                name="Cargo Capacity",
                vessel_value=v_capacity,
                port_limit=cargo_quantity_mt,
                passed=cargo_feasible,
                message=(
                    f"Required {cargo_quantity_mt:,.0f} MT "
                    f"{'≤' if cargo_feasible else '>'} "
                    f"vessel capacity {v_capacity:,.0f} MT"
                ),
            ))

        # ── 5. Overall feasibility ────────────────────────────────────────────
        feasible = all(c.passed for c in checks)

        result = FeasibilityResult(
            vessel_type=vessel_type,
            port_id=port_id,
            port_name=port["name"],
            feasible=feasible,
            checks=checks,
            warnings=warnings,
            cargo_feasible=cargo_feasible,
        )

        logger.debug(result.summary())
        return result

    def check_all_vessels(
        self,
        port_id: str,
        cargo_quantity_mt: float = 0.0,
    ) -> list[FeasibilityResult]:
        """Check all vessel types for a given port."""
        results = []
        for vessel_type in self._vessel_configs:
            result = self.check(vessel_type, port_id, cargo_quantity_mt)
            results.append(result)
        return results

    def get_feasible_vessels(
        self,
        port_id: str,
        cargo_quantity_mt: float = 0.0,
    ) -> list[str]:
        """Return list of vessel types that pass all constraints at this port."""
        results = self.check_all_vessels(port_id, cargo_quantity_mt)
        return [r.vessel_type for r in results if r.feasible]

    def results_to_dict(self, results: list[FeasibilityResult]) -> list[dict[str, Any]]:
        """Convert results to JSON-serialisable dicts for the API."""
        output = []
        for r in results:
            output.append({
                "vessel_type": r.vessel_type,
                "port_id": r.port_id,
                "port_name": r.port_name,
                "feasible": r.feasible,
                "cargo_feasible": r.cargo_feasible,
                "checks": [
                    {
                        "name": c.name,
                        "vessel_value": c.vessel_value,
                        "port_limit": c.port_limit,
                        "passed": c.passed,
                        "status": c.status_label,
                        "message": c.message,
                    }
                    for c in r.checks
                ],
                "warnings": r.warnings,
                "summary": r.summary(),
            })
        return output
