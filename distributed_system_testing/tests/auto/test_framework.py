# AUTO-GENERATED from test plan: distributed_system_testing/docs/test-plan.md
# Scenario: S1, S2, S3, S4
# These tests verify the distributed_system_testing framework itself using
# known-good and known-bad cluster configurations.

import pytest

from distributed_system_testing.claims import Claim, ClaimCategory, ClaimRegistry
from distributed_system_testing.faults import FaultInjector, FaultType, Nemesis
from distributed_system_testing.oracles import (
    IdempotencyOracle,
    LinearizabilityOracle,
    MonotonicReadOracle,
)
from distributed_system_testing.simulator import Cluster, OperationHistory
from distributed_system_testing.verdicts import (
    Verdict,
    VerdictDecisionTree,
    aggregate_arm_verdicts,
    session_level_verdict,
)


class TestClaimRegistry:
    def test_add_and_retrieve(self):
        registry = ClaimRegistry()
        c = Claim("C1", "writes are durable", ClaimCategory.DURABILITY, "README")
        registry.add(c)
        assert registry.get("C1") is c

    def test_duplicate_id_raises(self):
        registry = ClaimRegistry()
        registry.add(Claim("C1", "text", ClaimCategory.SAFETY, "src"))
        with pytest.raises(ValueError):
            registry.add(Claim("C1", "other", ClaimCategory.LIVENESS, "src"))

    def test_serious_categories(self):
        assert ClaimCategory.SAFETY.is_serious
        assert ClaimCategory.DURABILITY.is_serious
        assert ClaimCategory.ISOLATION.is_serious
        assert not ClaimCategory.PERFORMANCE_SLO.is_serious
        assert not ClaimCategory.LIVENESS.is_serious

    def test_surface_decomposition_categories(self):
        assert ClaimCategory.BOUNDARY.requires_surface_decomposition
        assert ClaimCategory.FAIRNESS.requires_surface_decomposition
        assert not ClaimCategory.SAFETY.requires_surface_decomposition

    def test_render_table(self):
        registry = ClaimRegistry()
        registry.add(Claim("C1", "text", ClaimCategory.SAFETY, "docs"))
        table = registry.render_table()
        assert "C1" in table
        assert "safety" in table


class TestVerdictDecisionTree:
    def _base(self, **overrides):
        base = dict(
            attempted=True,
            fault_planned=True,
            fault_proven_landed=True,
            checker_ran=True,
            history_fields_complete=True,
            checker_covered_all_ops=True,
            violation_found=False,
            reproducer_obtained=False,
            env_capability_missing=False,
            serious_scenario=True,
        )
        base.update(overrides)
        return VerdictDecisionTree(**base)

    def test_not_run(self):
        assert self._base(attempted=False).evaluate() == Verdict.NOT_RUN

    def test_inconclusive_env(self):
        assert self._base(env_capability_missing=True).evaluate() == Verdict.INCONCLUSIVE_ENV

    def test_fail_reproducible(self):
        t = self._base(violation_found=True, reproducer_obtained=True)
        assert t.evaluate() == Verdict.FAIL_REPRODUCIBLE

    def test_fail_nondeterministic(self):
        t = self._base(violation_found=True, reproducer_obtained=False)
        assert t.evaluate() == Verdict.FAIL_NONDETERMINISTIC

    def test_inconclusive_fault_not_proven(self):
        t = self._base(fault_proven_landed=False)
        assert t.evaluate() == Verdict.INCONCLUSIVE_FAULT_NOT_PROVEN

    def test_partial_surface_no_checker(self):
        t = self._base(checker_ran=False)
        assert t.evaluate() == Verdict.PARTIAL_SURFACE

    def test_inconclusive_oracle_too_weak(self):
        t = self._base(history_fields_complete=False)
        assert t.evaluate() == Verdict.INCONCLUSIVE_ORACLE_TOO_WEAK

    def test_partial_model(self):
        t = self._base(checker_covered_all_ops=False)
        assert t.evaluate() == Verdict.PARTIAL_MODEL

    def test_pass_hardening(self):
        assert self._base().evaluate() == Verdict.PASS_HARDENING

    def test_pass_smoke(self):
        t = self._base(fault_planned=False, fault_proven_landed=False)
        assert t.evaluate() == Verdict.PASS_SMOKE

    def test_aggregate_not_run_caps_at_partial(self):
        verdicts = [Verdict.PASS_HARDENING, Verdict.NOT_RUN]
        assert aggregate_arm_verdicts(verdicts) == Verdict.PARTIAL_SURFACE

    def test_aggregate_all_pass_hardening(self):
        verdicts = [Verdict.PASS_HARDENING, Verdict.PASS_HARDENING]
        assert aggregate_arm_verdicts(verdicts) == Verdict.PASS_HARDENING

    def test_aggregate_fail_dominates(self):
        verdicts = [Verdict.PASS_HARDENING, Verdict.FAIL_REPRODUCIBLE]
        assert aggregate_arm_verdicts(verdicts) == Verdict.FAIL_REPRODUCIBLE

    def test_session_verdict_fail(self):
        assert session_level_verdict([Verdict.PASS_HARDENING, Verdict.FAIL_REPRODUCIBLE]) == "FAIL"

    def test_session_verdict_done(self):
        assert session_level_verdict([Verdict.PASS_HARDENING, Verdict.PASS_SMOKE]) == "DONE"

    def test_session_verdict_done_with_concerns(self):
        assert session_level_verdict([Verdict.PASS_HARDENING, Verdict.NOT_RUN]) == "DONE_WITH_CONCERNS"


class TestSimulator:
    def test_write_then_read_from_leader(self):
        cluster = Cluster(["n1", "n2", "n3"])
        history = OperationHistory()
        w = cluster.write("x", 42, process_id="p1")
        r = cluster.read("x", process_id="p1")
        history.record(w)
        history.record(r)

        assert w.output_value == "ok"
        assert r.output_value == 42
        assert history.has_required_fields()

    def test_write_fails_when_no_leader(self):
        cluster = Cluster(["n1"])
        cluster.crash_node("n1")
        op = cluster.write("x", 99)
        assert op.error == "NO_LEADER"

    def test_crash_triggers_new_leader_election(self):
        cluster = Cluster(["n1", "n2", "n3"])
        assert cluster.leader is not None
        old_leader = cluster.leader.node_id
        cluster.crash_node(old_leader)
        new_leader = cluster.leader
        assert new_leader is not None
        assert new_leader.node_id != old_leader

    def test_partition_makes_node_unavailable(self):
        cluster = Cluster(["n1", "n2"])
        cluster.partition_node("n2")
        ok, _ = cluster.nodes["n2"].read("x")
        assert not ok

    def test_heal_restores_replication(self):
        cluster = Cluster(["n1", "n2"])
        cluster.write("x", 1)
        cluster.partition_node("n2")
        cluster.write("x", 2)
        cluster.heal_node("n2")
        _, val = cluster.nodes["n2"].read("x")
        assert val == 2


class TestLinearizabilityOracle:
    def test_clean_history_passes(self):
        cluster = Cluster(["n1", "n2", "n3"])
        history = OperationHistory()
        for i in range(5):
            history.record(cluster.write("x", i))
        history.record(cluster.read("x"))

        oracle = LinearizabilityOracle()
        result = oracle.check(history)
        assert result.passed, result.anomalies

    def test_empty_history_passes(self):
        history = OperationHistory()
        oracle = LinearizabilityOracle()
        result = oracle.check(history)
        assert result.passed

    def test_ops_consumed_count(self):
        cluster = Cluster(["n1"])
        history = OperationHistory()
        for _ in range(3):
            history.record(cluster.write("k", 1))
        for _ in range(2):
            history.record(cluster.read("k"))
        oracle = LinearizabilityOracle()
        result = oracle.check(history)
        assert result.ops_consumed == 5


class TestMonotonicReadOracle:
    def test_consistent_reads_pass(self):
        cluster = Cluster(["n1"])
        history = OperationHistory()
        history.record(cluster.write("x", "v1"))
        history.record(cluster.read("x", process_id="p1"))
        history.record(cluster.read("x", process_id="p1"))

        oracle = MonotonicReadOracle()
        result = oracle.check(history)
        assert result.passed, result.anomalies


class TestIdempotencyOracle:
    def test_unique_writes_pass(self):
        cluster = Cluster(["n1"])
        history = OperationHistory()
        history.record(cluster.write("k", "val1"))
        history.record(cluster.write("k", "val2"))
        oracle = IdempotencyOracle()
        result = oracle.check(history)
        assert result.passed

    def test_duplicate_input_detected(self):
        cluster = Cluster(["n1"])
        history = OperationHistory()
        op1 = cluster.write("k", "same-value")
        op2 = cluster.write("k", "same-value")
        history.record(op1)
        history.record(op2)
        oracle = IdempotencyOracle()
        result = oracle.check(history)
        assert not result.passed
        assert result.anomaly_count >= 1


class TestFaultInjector:
    def test_partition_produces_landing_evidence(self):
        injector = FaultInjector(random_seed=0)
        nemesis = Nemesis(
            fault_type=FaultType.NETWORK_PARTITION,
            target_nodes=["n1", "n2"],
            duration=30.0,
        )
        evidence = injector.inject(nemesis)
        assert evidence.proven
        assert evidence.fault_type == FaultType.NETWORK_PARTITION
        assert "n1" in evidence.affected_nodes

    def test_heal_removes_active_fault(self):
        injector = FaultInjector()
        nemesis = Nemesis(FaultType.NODE_CRASH, ["n1"])
        injector.inject(nemesis)
        assert len(injector.active_faults()) == 1
        injector.heal(nemesis)
        assert len(injector.active_faults()) == 0

    def test_all_fault_types_produce_evidence(self):
        injector = FaultInjector()
        for ft in FaultType:
            nemesis = Nemesis(ft, ["n1"])
            evidence = injector.inject(nemesis)
            assert evidence.fault_type == ft
