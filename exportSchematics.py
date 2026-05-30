#!/usr/bin/env python
"""
exportSchematics.py
Run from the organisation root folder.
Exports all KiCad root schematics to PDF -> releases/schematic-<name>.pdf
Cleans up any PDF files kicad-cli may have left in the hardware folder.

Root schematic detection rule: filename stem starts with the repo name,
autosave files (_autosave-*) are skipped.

Works for:
  - Single-board repos  (e.g. OS-Duplex)       -> releases/schematic-OS-Duplex.pdf
  - Multi-board repos   (e.g. OS-S88n)          -> releases/schematic-OS-S88n-CS.pdf  etc.
"""

import sys
import subprocess
from pathlib import Path


def fail(msg):
    print("[FAIL] " + msg)
    sys.exit(1)

def info(msg):
    print("[INFO] " + msg)

def success(msg):
    print("[OK] " + msg)


def find_kicad_cli() -> str:
    candidates = [
        r"C:\Program Files\KiCad\8.0\bin\kicad-cli.exe",
        r"C:\Program Files\KiCad\7.0\bin\kicad-cli.exe",
        "/usr/bin/kicad-cli",
        "/usr/local/bin/kicad-cli",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    fail("kicad-cli not found. Install KiCad or add it to PATH.")


def find_root_schematics(hardware_dir: Path, repo_name: str) -> list:
    """
    Return all .kicad_sch files whose stem starts with repo_name.
    Skips _autosave files. Searches recursively for multi-board repos.
    """
    found = []
    for sch in sorted(hardware_dir.rglob("*.kicad_sch")):
        if sch.stem.startswith("_"):
            continue
        if sch.stem.startswith(repo_name):
            found.append(sch)
    return found


def cleanup_hardware_pdfs(hardware_dir: Path):
    """Remove any stray PDFs kicad-cli may have written into the hardware folder."""
    for pdf in hardware_dir.rglob("*.pdf"):
        try:
            pdf.unlink()
            info("Removed stray PDF: " + str(pdf))
        except Exception as e:
            info("Could not remove " + str(pdf) + ": " + str(e))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    kicad_cli = find_kicad_cli()
    org_root = Path.cwd().resolve()
    exported = 0

    for repo_dir in sorted(org_root.iterdir()):
        if not repo_dir.is_dir():
            continue
        hardware_dir = repo_dir / "hardware"
        if not hardware_dir.is_dir():
            continue

        repo_name = repo_dir.name
        schematics = find_root_schematics(hardware_dir, repo_name)

        if not schematics:
            info("No root schematic found in: " + repo_name)
            continue

        releases_dir = repo_dir / "releases"
        releases_dir.mkdir(exist_ok=True)

        for sch in schematics:
            out_name = "schematic-" + sch.stem + ".pdf"
            out_path = releases_dir / out_name
            info("Exporting: " + sch.name + "  ->  " + str(out_path))

            result = subprocess.run(
                [
                    kicad_cli, "sch", "export", "pdf",
                    "-o", str(out_path),
                    "--no-background-color",
                    str(sch),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                fail("kicad-cli failed for " + sch.name + ":\n" + result.stderr)

            success(out_name + " exported.")
            exported += 1

        cleanup_hardware_pdfs(hardware_dir)

    success(f"Done: {exported} schematic(s) exported.")


if __name__ == "__main__":
    main()
