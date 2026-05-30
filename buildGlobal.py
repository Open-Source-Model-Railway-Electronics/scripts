#!/usr/bin/env python3
"""
buildGlobal.py
Run from a repo's software/ folder.
Compiles the firmware, moves the .hex to releases/<repo-name>.hex, cleans up build folder.
"""

import os
import sys
import shutil
import time
from pathlib import Path


def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)

def info(msg):
    print(f"[INFO] {msg}")

def success(msg):
    print(f"[OK] {msg}")


def main():
    software_dir = Path.cwd()
    repo_root = software_dir.parent
    repo_name = repo_root.name

    sketch_path = software_dir / "software.ino"
    build_dir = software_dir / "build"
    hex_file = build_dir / "arduino.avr.nano" / "software.ino.hex"
    release_dir = repo_root / "releases"

    if not sketch_path.exists():
        fail(f"Bestand niet gevonden: {sketch_path}")

    info("Compileren met arduino-cli...")
    result = os.system("arduino-cli compile -b arduino:avr:nano -e --fqbn arduino:avr:nano .")
    if result != 0:
        fail("Build gefaald!")

    if not hex_file.exists():
        fail(f".hex bestand niet gevonden: {hex_file}")

    release_dir.mkdir(exist_ok=True)

    target = release_dir / f"{repo_name}.hex"
    shutil.copy2(str(hex_file), str(target))
    success(f"HEX gekopieerd naar: {target}")

    # Also copy to OS-software-tool distribution repo
    org_root = repo_root.parent
    software_tool_dir = org_root / "OS-software-tool"
    if software_tool_dir.is_dir():
        dist_target = software_tool_dir / f"{repo_name}.hex"
        shutil.copy2(str(target), str(dist_target))
        success(f"HEX ook naar OS-software-tool: {dist_target}")
    else:
        info("OS-software-tool map niet gevonden, overgeslagen.")

    # Wacht even zodat Windows file locks vrijgeeft
    time.sleep(1)

    try:
        shutil.rmtree(build_dir)
        info("Build-folder volledig verwijderd.")
    except Exception as e:
        fail(f"Kon build folder niet verwijderen: {e}")

    success("Klaar!")


if __name__ == "__main__":
    main()
