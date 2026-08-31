from __future__ import annotations

import copy
import unittest

from architecture.adapter import (
    QuantMuseArchitectureError,
    load_architecture_spec,
    validate_quantmuse_architecture_spec,
)


class QuantMuseArchitectureFederationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_architecture_spec()

    def test_reference_spec_is_admissible(self) -> None:
        validate_quantmuse_architecture_spec(self.spec)
        self.assertEqual(self.spec["architecture_id"], "quantmuse.ai_quant_research.v1")

    def test_llm_enters_as_proposal_not_authority(self) -> None:
        proposals = {item["id"] for item in self.spec["proposals"]}
        self.assertIn("propose_llm_market_interpretation", proposals)
        owners = {item["owner"] for item in self.spec["authorities"]}
        self.assertNotIn("llm", owners)
        self.assertNotIn("openai", owners)

    def test_model_cannot_mint_execution_authority(self) -> None:
        mutated = copy.deepcopy(self.spec)
        mutated["authorities"][0]["owner"] = "quantmuse.llm"
        with self.assertRaises(QuantMuseArchitectureError):
            validate_quantmuse_architecture_spec(mutated)

    def test_execution_backend_cannot_mint_execution_authority(self) -> None:
        mutated = copy.deepcopy(self.spec)
        mutated["authorities"][0]["owner"] = "quantmuse.cpp_backend"
        with self.assertRaises(QuantMuseArchitectureError):
            validate_quantmuse_architecture_spec(mutated)

    def test_model_output_proposal_projector_is_mandatory(self) -> None:
        mutated = copy.deepcopy(self.spec)
        mutated["constraints"] = [item for item in mutated["constraints"] if item["id"] != "project_model_output_to_proposal_only"]
        with self.assertRaises(QuantMuseArchitectureError):
            validate_quantmuse_architecture_spec(mutated)

    def test_recommendation_is_not_evidence_invariant_is_mandatory(self) -> None:
        mutated = copy.deepcopy(self.spec)
        mutated["invariants"] = [item for item in mutated["invariants"] if item["id"] != "recommendation_is_not_evidence"]
        with self.assertRaises(QuantMuseArchitectureError):
            validate_quantmuse_architecture_spec(mutated)

    def test_risk_projectors_are_mandatory(self) -> None:
        for projector in ("project_position_limits", "project_drawdown_limits", "project_leverage_limits"):
            with self.subTest(projector=projector):
                mutated = copy.deepcopy(self.spec)
                mutated["constraints"] = [item for item in mutated["constraints"] if item["id"] != projector]
                with self.assertRaises(QuantMuseArchitectureError):
                    validate_quantmuse_architecture_spec(mutated)

    def test_evidence_and_reconciliation_are_mandatory(self) -> None:
        for collection in ("evidence", "reconciliation"):
            with self.subTest(collection=collection):
                mutated = copy.deepcopy(self.spec)
                mutated[collection] = []
                with self.assertRaises(QuantMuseArchitectureError):
                    validate_quantmuse_architecture_spec(mutated)


if __name__ == "__main__":
    unittest.main()
