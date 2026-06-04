"""Repackage the dream-underwrite skill into a Claude.ai-uploadable bundle.

Run after editing anything under .skills/dream-underwrite/. Produces both
.zip and .skill bundles in the user's Downloads folder, ready to drag into
Claude.ai's skill upload dialog.

Why this script exists:
  PowerShell's Compress-Archive writes Windows-style backslashes into ZIP
  paths, which Claude.ai rejects as "invalid characters". Python's zipfile
  module writes spec-compliant forward slashes via Path.as_posix(). This
  script also excludes __pycache__, .DS_Store, and Thumbs.db so junk
  artifacts never ship with the bundle.

Usage:
  cd <repo-root>
  python .skills/dream-underwrite/scripts/repackage-skill.py

Or from the script directory:
  cd .skills/dream-underwrite/scripts
  python repackage-skill.py

The script auto-locates the skill folder (its own parent's parent) and the
user's Downloads folder.
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent  # .skills/dream-underwrite/
DOWNLOADS = Path.home() / "Downloads"
SKILL_NAME = SKILL_ROOT.name  # "dream-underwrite"

EXCLUDE_DIRS = {"__pycache__"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}


def should_include(path: Path) -> bool:
    """Skip junk artifacts, hidden files, and the bundle output itself."""
    rel_parts = path.relative_to(SKILL_ROOT).parts
    for part in rel_parts:
        if part.startswith("."):
            return False
        if part in EXCLUDE_DIRS:
            return False
    if path.name in EXCLUDE_FILES:
        return False
    if path.suffix == ".pyc":
        return False
    return True


def repackage() -> tuple[Path, Path]:
    if not DOWNLOADS.exists():
        DOWNLOADS.mkdir(parents=True, exist_ok=True)

    out_zip = DOWNLOADS / f"{SKILL_NAME}.zip"
    out_skill = DOWNLOADS / f"{SKILL_NAME}.skill"

    for existing in (out_zip, out_skill):
        if existing.exists():
            existing.unlink()

    files_added = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(SKILL_ROOT.rglob("*")):
            if f.is_file() and should_include(f):
                arcname = f.relative_to(SKILL_ROOT).as_posix()
                zf.write(f, arcname)
                files_added += 1

    shutil.copy2(out_zip, out_skill)

    print(f"\n[ok] Repackaged {SKILL_NAME}")
    print(f"     source : {SKILL_ROOT}")
    print(f"     files  : {files_added}")
    print(f"     size   : {out_zip.stat().st_size / 1024:.1f} KB")
    print(f"     bundle : {out_zip}")
    print(f"     bundle : {out_skill}")
    return out_zip, out_skill


def verify(bundle: Path) -> None:
    """Print the contents of the bundle so the user can sanity-check before upload."""
    with zipfile.ZipFile(bundle) as zf:
        names = zf.namelist()
    print(f"\n[verify] {len(names)} entries in {bundle.name}:")
    for n in names:
        print(f"  {n}")


def main() -> int:
    if not SKILL_ROOT.exists():
        print(f"[err] Skill folder not found: {SKILL_ROOT}", file=sys.stderr)
        return 1
    if not (SKILL_ROOT / "SKILL.md").exists():
        print(f"[err] SKILL.md not found in {SKILL_ROOT}", file=sys.stderr)
        return 1

    zip_path, _ = repackage()

    if "--verify" in sys.argv or "-v" in sys.argv:
        verify(zip_path)

    print(
        "\nNext step: drag the .zip into Claude.ai skill upload dialog.\n"
        "  Settings > Capabilities > Skills > Upload skill\n"
        "Claude.ai will replace the existing skill with the same name.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
