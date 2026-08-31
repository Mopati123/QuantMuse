"""QuantMuse -> HPL ArchitectureIR federation boundary."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

SPEC_PATH = Path(__file__).with_name("quantmuse.architecture.json")
EXPECTED_CONTRACT = {
    "contract_id": "hpl.architecture-federation",
    "version": "1.0.0",
    "execution_owner": "hpl.scheduler",
    "program_ir_collapse_policy": "architecture_ir_scheduler_sovereignty",
    "evidence_required": True,
    "reconciliation_required": True,
}
REQUIRED_AI_INVARIANTS = {
    "model_output_is_not_authority",
    "recommendation_is_not_evidence",
    "projection_before_execution",
    "scheduler_sovereignty",
    "refusal_first",
    "evidence_required",
    "reconciliation_required",
}
REQUIRED_PROJECTORS = {
    "project_model_output_to_proposal_only",
    "project_strategy_admissibility",
    "project_position_limits",
    "project_drawdown_limits",
    "project_leverage_limits",
    "project_portfolio_constraints",
    "project_execution_boundary",
    "project_total_admissibility",
}


class QuantMuseArchitectureError(ValueError):
    """Raised when QuantMuse violates the universal governed-execution boundary."""


def validate_quantmuse_architecture_spec(spec: Dict[str, Any]) -> None:
    if spec.get("domain") != "quantitative_trading_ai":
        raise QuantMuseArchitectureError("QuantMuse federation domain mismatch")

    invariants = {item.get("id") for item in spec.get("invariants", [])}
    missing = REQUIRED_AI_INVARIANTS - invariants
    if missing:
        raise QuantMuseArchitectureError(f"missing AI governance invariants: {sorted(missing)}")

    projectors = {item.get("id") for item in spec.get("constraints", [])}
    missing = REQUIRED_PROJECTORS - projectors
    if missing:
        raise QuantMuseArchitectureError(f"missing QuantMuse projectors: {sorted(missing)}")

    execution = [item for item in spec.get("authorities", []) if item.get("kind") == "execution"]
    if len(execution) != 1 or execution[0].get("owner") != "hpl.scheduler":
        raise QuantMuseArchitectureError("models, strategies, and backends cannot mint execution authority")

    proposal_ids = {item.get("id") for item in spec.get("proposals", [])}
    if "propose_llm_market_interpretation" not in proposal_ids:
        raise QuantMuseArchitectureError("LLM output must enter the federation as a proposal")

    if not spec.get("evidence"):
        raise QuantMuseArchitectureError("evidence operators are mandatory")
    if not spec.get("reconciliation"):
        raise QuantMuseArchitectureError("reconciliation operators are mandatory")


def load_architecture_spec(path: Path = SPEC_PATH) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        spec = json.load(handle)
    validate_quantmuse_architecture_spec(spec)
    return spec


def compile_with_hpl() -> Dict[str, Any]:
    try:
        from hpl.architecture import compile_architecture_spec, federation_contract, lower_architecture_ir_to_program_ir
    except ImportError as exc:
        raise QuantMuseArchitectureError("HPL architecture federation compiler is required") from exc

    contract = federation_contract()
    if contract != EXPECTED_CONTRACT:
        raise QuantMuseArchitectureError("HPL federation contract drift")

    architecture_ir = compile_architecture_spec(load_architecture_spec())
    if architecture_ir.authority.get("execution_owner") != "hpl.scheduler":
        raise QuantMuseArchitectureError("ArchitectureIR execution authority drift")

    program_ir = lower_architecture_ir_to_program_ir(architecture_ir)
    if program_ir["scheduler"]["collapse_policy"] != EXPECTED_CONTRACT["program_ir_collapse_policy"]:
        raise QuantMuseArchitectureError("ProgramIR scheduler policy drift")

    return {
        "federation_contract": contract,
        "architecture_ir": architecture_ir.to_dict(),
        "program_ir": program_ir,
    }
