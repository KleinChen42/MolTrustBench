import pandas as pd

from moltrustbench.data.build_release_index import build_release_indexes


def test_release_index_keeps_earliest_release():
    frames = {
        "CHEMBL24": pd.DataFrame({"smiles": ["CCO", "CCN"]}),
        "CHEMBL30": pd.DataFrame({"smiles": ["CCO", "CCCl"]}),
    }
    compound, scaffold, counts, rejected = build_release_indexes(frames, allow_fallback=True)
    cco = compound[compound["standard_smiles"] == "CCO"].iloc[0]
    assert cco["first_seen_release"] == "CHEMBL24"
    assert cco["first_seen_order"] == 24
    assert counts["unique_standard_inchikey"].sum() >= 3
    assert rejected.empty
