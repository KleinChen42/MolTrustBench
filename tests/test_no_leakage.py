from moltrustbench.smoke import run_smoke
from moltrustbench.evaluation.sanity_checks import run_sanity_checks


def test_smoke_pipeline_has_no_critical_sanity_failures():
    result = run_smoke(allow_fallback=True)
    report = run_sanity_checks(".")
    failed = report[(report["severity"] == "critical") & (report["status"] == "fail")]
    assert result["benchmark_tasks"] >= 2
    assert failed.empty
