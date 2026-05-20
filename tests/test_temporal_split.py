from moltrustbench.splits.exposure_removed import exact_removed_split


def test_exact_removed_split_excludes_exposed_test_rows():
    import pandas as pd

    df = pd.DataFrame(
        {
            "row_id": [0, 1, 2, 3],
            "split": ["train", "train", "test", "test"],
            "exact_exposed": [True, False, True, False],
        }
    )
    split = exact_removed_split(df)
    assert split["train"] == [0, 1]
    assert split["test"] == [3]
