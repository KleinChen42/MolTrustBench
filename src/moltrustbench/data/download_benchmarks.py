"""Download or materialize benchmark datasets."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests

from moltrustbench.io import write_dataframe


def fixture_benchmarks() -> dict[tuple[str, str], pd.DataFrame]:
    hERG = pd.DataFrame(
        {
            "smiles": ["CCO", "CCN", "CC(=O)O", "CCOC", "CCCN", "CCCCC", "c1ccccc1O", "CCS", "CCBr", "COC(=O)N", "CCCl", "CC(C)O"],
            "label": [0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1],
            "split": ["train", "train", "train", "train", "train", "train", "test", "test", "test", "test", "test", "test"],
        }
    )
    bbbp = pd.DataFrame(
        {
            "smiles": ["c1ccccc1", "CCCl", "CCCO", "CC(C)N", "CCS", "CCN(CC)CC", "CCOC", "CC(=O)O", "CCCCC", "CCBr", "c1ccncc1", "COC(=O)N"],
            "label": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            "split": ["train", "train", "train", "train", "train", "train", "test", "test", "test", "test", "test", "test"],
        }
    )
    return {("tdc_admet", "hERG"): hERG, ("moleculenet", "BBBP"): bbbp}


def load_tdc_hERG() -> pd.DataFrame:
    try:
        from tdc.single_pred import ADME
    except Exception as exc:
        raise RuntimeError("TDC is not installed. Use --fixture or install the benchmarks extra.") from exc
    data = ADME(name="hERG")
    split = data.get_split()
    frames = []
    for split_name, frame in split.items():
        tmp = frame.rename(columns={"Drug": "smiles", "Y": "label"}).copy()
        tmp["split"] = split_name
        frames.append(tmp[["smiles", "label", "split"]])
    return pd.concat(frames, ignore_index=True)


MOLECULENET_URLS = {
    "BBBP": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/BBBP.csv",
    "ClinTox": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/clintox.csv.gz",
    "ESOL": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/delaney-processed.csv",
    "Lipophilicity": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/Lipophilicity.csv",
    "BACE": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/bace.csv",
    "Tox21": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/tox21.csv.gz",
    "SIDER": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/sider.csv.gz",
}


def _download_csv(url: str, output_path: Path) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)
    return pd.read_csv(output_path)


def load_moleculenet_task(task: str, *, raw_dir: str | Path = "data/raw/benchmarks") -> pd.DataFrame:
    if task not in MOLECULENET_URLS:
        raise ValueError(f"Unsupported MoleculeNet task: {task}")
    raw_path = Path(raw_dir) / Path(MOLECULENET_URLS[task]).name
    frame = _download_csv(MOLECULENET_URLS[task], raw_path)
    if task == "BBBP":
        out = frame.rename(columns={"p_np": "label"})[["smiles", "label"]].copy()
    elif task == "ClinTox":
        out = frame.rename(columns={"FDA_APPROVED": "label"})[["smiles", "label"]].copy()
    elif task == "ESOL":
        out = frame.rename(columns={"measured log solubility in mols per litre": "label"})[["smiles", "label"]].copy()
    elif task == "Lipophilicity":
        out = frame.rename(columns={"exp": "label"})[["smiles", "label"]].copy()
    elif task == "BACE":
        out = frame.rename(columns={"mol": "smiles", "Class": "label"})[["smiles", "label"]].copy()
    else:
        label_cols = [column for column in frame.columns if column not in {"smiles", "mol_id", "Molecule"}]
        out = frame.rename(columns={label_cols[0]: "label"})[["smiles", "label"]].dropna().copy()
    out = out.dropna(subset=["smiles", "label"]).reset_index(drop=True)
    split = ["train"] * len(out)
    if len(out) >= 5:
        cut = int(0.8 * len(out))
        split[cut:] = ["test"] * (len(out) - cut)
    out["split"] = split
    return out[["smiles", "label", "split"]]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--source-name", default="tdc_admet", choices=["tdc_admet", "moleculenet"])
    parser.add_argument("--task-name", default="hERG")
    parser.add_argument("--output-dir", default="data/raw/benchmarks")
    args = parser.parse_args(argv)

    if args.fixture:
        datasets = fixture_benchmarks()
    elif args.source_name == "moleculenet":
        datasets = {("moleculenet", args.task_name): load_moleculenet_task(args.task_name, raw_dir=args.output_dir)}
    else:
        datasets = {("tdc_admet", "hERG"): load_tdc_hERG()}

    for (source, task), frame in datasets.items():
        out = Path(args.output_dir) / f"{source}_{task}.parquet"
        write_dataframe(frame, out)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
