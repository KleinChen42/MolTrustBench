import pandas as pd

from moltrustbench.splits.density_matched import (
    density_control_table,
    density_matched_clean_split,
)
from moltrustbench.training.train import split_train_test


def _frame():
    return pd.DataFrame(
        {
            "row_id": [0, 1, 2, 3, 4, 5, 6],
            "split": ["train", "valid", "test", "test", "test", "test", "test"],
            "exact_exposed": [False, False, True, True, False, False, False],
            "max_nn_similarity_before_cutoff": [0.0, 0.0, 0.1, 0.9, 0.2, 0.8, 0.85],
        }
    )


def test_density_matched_clean_split_matches_bins():
    split = density_matched_clean_split(_frame(), bins=2)

    assert split["train"] == [0, 1]
    assert len(split["test"]) == 2
    assert set(split["test"]).issubset({4, 5, 6})


def test_density_control_table_reports_selected_counts():
    split = density_matched_clean_split(_frame(), bins=2)
    table = density_control_table(_frame(), selected_test_ids=split["test"], bins=2)

    assert table["exposed_test_n"].sum() == 2
    assert table["selected_clean_test_n"].sum() == 2


def test_training_density_matched_clean_split_is_clean():
    _, test = split_train_test(_frame(), split_name="density_matched_clean")

    assert len(test) == 2
    assert not test["exact_exposed"].any()
