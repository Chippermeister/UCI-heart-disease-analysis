"""Download the UCI Heart Disease files into data/raw/ and verify their integrity.

Usage:
    python src/download_data.py            # download missing files, then pin or verify checksums
    python src/download_data.py --verify   # only verify existing files against SHA256SUMS
    python src/download_data.py --force    # re-download every file, then verify

On the first run there is no checksum manifest yet, so the script records one
(data/raw/SHA256SUMS). Every later run compares the files on disk against that
manifest and fails loudly if anything has changed. The manifest uses the same
format as the `sha256sum` tool, so it can also be checked with:

    cd data/raw && sha256sum -c SHA256SUMS
"""

import argparse
import hashlib
import sys
from pathlib import Path

import requests

BASE_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/"

# Only the 14-attribute "processed" files plus the documentation. The original
# 76-attribute files are deliberately excluded (see .gitignore).
FILES = [
    "processed.cleveland.data",
    "processed.hungarian.data",
    "processed.switzerland.data",
    "processed.va.data",
    "heart-disease.names",
]

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
CHECKSUM_FILE = RAW_DIR / "SHA256SUMS"
TIMEOUT_SECONDS = 30


def sha256_of(path: Path) -> str:
    """Return the hex SHA-256 digest of a file, read in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(name: str, base_url: str) -> None:
    """Fetch one file, writing to a temporary name first so a failed
    download never leaves a half-written file behind."""
    url = base_url + name
    target = RAW_DIR / name
    tmp = target.with_suffix(target.suffix + ".part")

    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    if not response.content:
        raise RuntimeError(f"{url} returned an empty file")

    tmp.write_bytes(response.content)
    tmp.replace(target)
    print(f"  downloaded {name} ({len(response.content):,} bytes)")


def read_manifest() -> dict[str, str]:
    """Parse SHA256SUMS lines of the form '<hash>  <filename>'."""
    manifest = {}
    for line in CHECKSUM_FILE.read_text().splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            manifest[name.strip()] = digest
    return manifest


def write_manifest() -> None:
    lines = [f"{sha256_of(RAW_DIR / name)}  {name}" for name in FILES]
    CHECKSUM_FILE.write_text("\n".join(lines) + "\n")
    print(f"Recorded checksums for {len(FILES)} files in {CHECKSUM_FILE.name}")


def verify() -> bool:
    """Compare every expected file against the manifest. Returns True if all match."""
    if not CHECKSUM_FILE.exists():
        print(f"No {CHECKSUM_FILE.name} found; run without --verify first.")
        return False

    manifest = read_manifest()
    ok = True
    for name in FILES:
        path = RAW_DIR / name
        expected = manifest.get(name)
        if expected is None:
            print(f"  MISSING FROM MANIFEST  {name}")
            ok = False
        elif not path.exists():
            print(f"  MISSING FILE           {name}")
            ok = False
        elif sha256_of(path) != expected:
            print(f"  CHECKSUM MISMATCH      {name}")
            ok = False
        else:
            print(f"  OK                     {name}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verify", action="store_true", help="only verify, do not download")
    parser.add_argument("--force", action="store_true", help="re-download files that already exist")
    parser.add_argument("--base-url", default=BASE_URL, help="override the source URL (e.g. a mirror)")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if not args.verify:
        print(f"Downloading from {args.base_url}")
        for name in FILES:
            if (RAW_DIR / name).exists() and not args.force:
                print(f"  skipped {name} (already present)")
            else:
                download(name, args.base_url)

        if not CHECKSUM_FILE.exists():
            write_manifest()

    print("Verifying checksums:")
    if verify():
        print("All files verified.")
        return 0
    print("Verification FAILED: the files differ from the recorded checksums.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
