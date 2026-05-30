#!/usr/bin/env python3
"""
releaseVersion.py
Run from a repo's software/ folder.
Guides you through versioning, building, committing, tagging and pushing a firmware release.
"""

import os
from pathlib import Path


def get_version():
    version = input("Which version will you be releasing?\n")
    print("VERSION " + version + " SELECTED\n")
    return version


def get_commit_text():
    print("Enter a description for the changelog, send 'done' when ready")
    commit_message = ""
    while True:
        line = input()
        if line == "done":
            break
        commit_message += line + "\n"

    temp = Path("src/temp.txt")
    temp.parent.mkdir(exist_ok=True)
    with open(temp, "w") as f:
        f.write(commit_message)


def update_version_number(version):
    with open("src/version.h", "w") as f:
        f.write('const char * version = "' + version + '" ;')


def build_project():
    result = os.system("python src/build.py")
    if result != 0:
        print("[WARN] Build returned non-zero exit code. Check output above before continuing.")
        answer = input("Continue anyway? [y/n]\n")
        if answer.lower() != "y":
            print("Aborted.")
            raise SystemExit(1)


def commit():
    answer = input("Do you wish to perform a git commit? [y/n] (recommended for version.h)\n")
    if answer.lower() == "y":
        os.system('git commit -a -F "src/temp.txt"')
        print("COMMIT MADE\n")
    else:
        print("NO COMMIT MADE\n")

    temp = Path("src/temp.txt")
    if temp.exists():
        temp.unlink()


def tag(version):
    print("MAKING GIT TAG " + version)
    os.system("git tag " + version)


def changelog():
    answer = input("Do you wish to update changelog.txt? [y/n]\n")
    if answer.lower() == "y":
        # Pure Python git log — no grep needed, works on Windows
        os.system('git log --tags --simplify-by-decoration --pretty="format:%ai %D %s" > changelog.txt')
        os.system("git add changelog.txt")
        print("CHANGELOG.TXT UPDATED")
    else:
        print("CHANGELOG.TXT NOT UPDATED")


def push(version):
    answer = input("Do you wish to push to git server? [y/n]\n")
    if answer.lower() == "y":
        os.system("git push")
        os.system("git push origin " + version)   # push the tag as well
        print("REPOSITORY PUSHED\n")
    else:
        print("REPOSITORY NOT PUSHED\n")


################# MAIN #################
if __name__ == "__main__":
    version = get_version()
    get_commit_text()
    update_version_number(version)
    build_project()
    commit()
    tag(version)
    changelog()
    push(version)

    print("\nNEW VERSION SUCCESSFULLY RELEASED!")
