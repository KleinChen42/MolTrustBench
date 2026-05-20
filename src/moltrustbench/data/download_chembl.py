"""Download ChEMBL SQLite archives for configured releases."""

from __future__ import annotations

import argparse
from pathlib import Path
import tarfile

import requests

from moltrustbench.constants import CHEMBL_RELEASES
from moltrustbench.io import ensure_dir, file_sha256, write_json


def chembl_sqlite_url(release_id: str) -> str:
    version = release_id.replace("CHEMBL", "").lower()
    return f"https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_{version}/chembl_{version}_sqlite.tar.gz"


def download_file(url: str, output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with out.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    return out


def download_chembl_release(release_id: str, *, output_dir: str | Path = "data/raw/chembl", skip_existing: bool = True) -> dict:
    url = chembl_sqlite_url(release_id)
    archive_path = Path(output_dir) / f"{release_id.lower()}_sqlite.tar.gz"
    extract_dir = Path(output_dir) / release_id.lower()
    existing_sqlite = next(extract_dir.rglob("*.db"), None) if extract_dir.exists() else None
    if skip_existing and archive_path.exists() and existing_sqlite and existing_sqlite.exists():
        sqlite_path = existing_sqlite
    else:
        download_file(url, archive_path)
        sqlite_path = extract_sqlite_archive(archive_path, extract_dir)
    manifest = {
        "release_id": release_id,
        "url": url,
        "archive_path": str(archive_path),
        "sqlite_path": str(sqlite_path),
        "archive_sha256": file_sha256(archive_path),
        "sqlite_sha256": file_sha256(sqlite_path),
        "release_date": CHEMBL_RELEASES[release_id].date,
        "release_doi": CHEMBL_RELEASES[release_id].doi,
    }
    write_json(manifest, Path("data/manifests") / f"chembl_{release_id.lower()}.json")
    return manifest


def extract_sqlite_archive(archive_path: str | Path, output_dir: str | Path) -> Path:
    out_dir = ensure_dir(output_dir)
    with tarfile.open(archive_path) as archive:
        members = [member for member in archive.getmembers() if member.name.endswith((".db", ".sqlite", ".sqlite3"))]
        if not members:
            raise ValueError(f"No SQLite database found in {archive_path}")
        member = members[0]
        archive.extract(member, out_dir)
        return out_dir / member.name


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="append", default=None, choices=sorted(CHEMBL_RELEASES))
    parser.add_argument("--output-dir", default="data/raw/chembl")
    parser.add_argument("--force", action="store_true", help="Re-download and re-extract even if local files exist.")
    args = parser.parse_args(argv)

    releases = args.release or list(CHEMBL_RELEASES)
    for release_id in releases:
        manifest = download_chembl_release(release_id, output_dir=args.output_dir, skip_existing=not args.force)
        print(f"Downloaded {release_id}: {manifest['sqlite_path']}")


if __name__ == "__main__":
    main()
