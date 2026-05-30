#!/usr/bin/env python3
"""
cloneOrg.py
Run from the organisation root folder (the folder that contains scripts/).
Clones every repository in the Open-Source-Model-Railway-Electronics GitHub
organisation that is not already present locally.
Repos that already exist as a local folder are skipped.

Requirements:
  - GitHub CLI (gh) installed and authenticated  ->  gh auth login
"""

import subprocess
import sys
import shutil
from pathlib import Path

ORG = "Open-Source-Model-Railway-Electronics"


def run(cmd, check=True):
    return subprocess.run(cmd, text=True, capture_output=True, check=check)

def fail(msg):
    print("[FAIL] " + msg)
    sys.exit(1)

def info(msg):
    print("[INFO] " + msg)

def success(msg):
    print("[OK] " + msg)


def check_prerequisites():
    if shutil.which("gh") is None:
        fail("GitHub CLI (gh) not found. Install it from https://cli.github.com/ and run 'gh auth login'.")

    result = run(["gh", "auth", "status"], check=False)
    if result.returncode != 0:
        fail("Not authenticated with GitHub CLI. Run 'gh auth login' first.")


def fetch_repo_names() -> list:
    info(f"Fetching repository list for organisation: {ORG} ...")
    result = run([
        "gh", "repo", "list", ORG,
        "--limit", "200",
        "--json", "name",
        "--jq",   ".[].name",
    ])
    repos = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not repos:
        fail("No repositories returned. Check your organisation name and gh authentication.")
    info(f"Found {len(repos)} repositories.")
    return sorted(repos)


def clone_all(repos: list):
    cloned  = 0
    skipped = 0
    failed  = 0

    for repo in repos:
        if Path(repo).is_dir():
            info(f"Already present, skipping: {repo}")
            skipped += 1
            continue

        info(f"Cloning: {repo}")
        result = run(["gh", "repo", "clone", f"{ORG}/{repo}", repo], check=False)

        if result.returncode != 0:
            print(f"[WARN] Could not clone {repo}:\n       {result.stderr.strip()}")
            failed += 1
        else:
            success(f"Cloned: {repo}")
            cloned += 1

    print(f"\nDone.  Cloned: {cloned}   Already present: {skipped}   Failed: {failed}")


def main():
    check_prerequisites()
    repos = fetch_repo_names()
    clone_all(repos)


if __name__ == "__main__":
    main()
