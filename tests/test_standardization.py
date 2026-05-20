from moltrustbench.chem import StandardizationError, standardize_smiles
from moltrustbench.data.standardize import standardize_dataframe


def test_fallback_standardization_is_deterministic():
    first = standardize_smiles(" CCO ", allow_fallback=True)
    second = standardize_smiles("CCO", allow_fallback=True)
    assert first.standard_inchikey == second.standard_inchikey
    assert first.canonical_smiles == "CCO"
    assert first.standardization_backend in {"rdkit", "fallback-fixture-only"}


def test_empty_smiles_rejected():
    try:
        standardize_smiles("", allow_fallback=True)
    except StandardizationError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("Expected empty SMILES to be rejected")


def test_standardize_dataframe_reports_rejects():
    import pandas as pd

    df = pd.DataFrame({"smiles": ["CCO", ""], "label": [0, 1], "split": ["train", "test"]})
    standardized, rejected, report = standardize_dataframe(df, allow_fallback=True, source_name="fixture", task_name="unit")
    assert len(standardized) == 1
    assert len(rejected) == 1
    assert report["rejected_rows"] == 1
