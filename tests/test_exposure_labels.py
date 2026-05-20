from moltrustbench.audit.exact_exposure import annotate_exposure
from moltrustbench.data.benchmark_loader import normalize_benchmark
from moltrustbench.data.build_release_index import build_release_indexes


def test_exact_scaffold_and_nn_exposure_labels():
    import pandas as pd

    releases = {
        "CHEMBL24": pd.DataFrame({"smiles": ["CCO", "CCN"]}),
        "CHEMBL33": pd.DataFrame({"smiles": ["CCCC"]}),
    }
    compound, scaffold, _, _ = build_release_indexes(releases, allow_fallback=True)
    benchmark_raw = pd.DataFrame(
        {
            "smiles": ["CCO", "CCCl", "CCCC"],
            "label": [0, 1, 0],
            "split": ["test", "test", "test"],
        }
    )
    benchmark, _, _ = normalize_benchmark(benchmark_raw, source_name="unit", task_name="exposure", allow_fallback=True)
    annotated = annotate_exposure(benchmark, compound, scaffold, cutoff_release="CHEMBL24", allow_fallback=True)
    exact = annotated[annotated["standard_smiles"] == "CCO"].iloc[0]
    scaffold = annotated[annotated["standard_smiles"] == "CCCl"].iloc[0]
    future = annotated[annotated["standard_smiles"] == "CCCC"].iloc[0]
    assert bool(exact["exact_exposed"])
    assert bool(scaffold["scaffold_exposed"])
    assert not bool(future["exact_exposed"])
    assert "max_nn_similarity_before_cutoff" in annotated
