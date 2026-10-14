"""Download hash-pinned local lint and UI tools; no shell profile is modified."""

from pathlib import Path
import hashlib
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = [
    (
        "https://repo.maven.apache.org/maven2/com/pinterest/ktlint/ktlint-cli/1.7.1/ktlint-cli-1.7.1-all.jar",
        ".work/ktlint.jar",
        "5f3de4ee4014137b05c72ed68eb46fe686aeb11fbdef27faf77f55d51c1b2536",
    ),
    (
        "https://github.com/mobile-dev-inc/maestro/releases/download/cli-2.11.0/maestro.zip",
        ".work/maestro.zip",
        "5384593cb4e7a106489e75a821d157dd43f4e438df6bc308b72e82c685e1283a",
    ),
]
for url, relative, expected in TOOLS:
    destination = ROOT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        urllib.request.urlretrieve(url, destination)
    if hashlib.sha256(destination.read_bytes()).hexdigest() != expected:
        raise ValueError(relative + ": checksum mismatch")
with zipfile.ZipFile(ROOT / ".work/maestro.zip") as archive:
    for member in archive.infolist():
        target = (ROOT / ".work/tools" / member.filename).resolve()
        if not target.is_relative_to((ROOT / ".work/tools").resolve()):
            raise ValueError("Unsafe archive member")
        archive.extract(member, ROOT / ".work/tools")
        mode = member.external_attr >> 16
        if mode and not member.is_dir():
            target.chmod(mode)
print("ktlint 1.7.1 and Maestro 2.11.0 are ready in .work/")
