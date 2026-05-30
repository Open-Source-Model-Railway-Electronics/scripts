# Open Source Model Railway Scripts

Toolchain automation scripts for the [Open-Source-Model-Railway-Electronics](https://github.com/Open-Source-Model-Railway-Electronics) organisation.

These scripts live in a shared `scripts/` folder at the organisation root and are called from the individual project repositories.

---

## Prerequisites

### Python 3

All scripts require Python 3.8 or newer.

Download: https://www.python.org/downloads/

Verify your installation:
```
python --version
```

No third-party packages are needed — only the Python standard library is used.

### arduino-cli

Required by `buildGlobal.py` and `releaseVersion.py`.

Download: https://arduino.github.io/arduino-cli/latest/installation/

After installing, add the AVR platform:
```
arduino-cli core install arduino:avr
```

Verify:
```
arduino-cli version
```

### KiCad 8

Required by `exportSchematics.py`. The script uses `kicad-cli`, which ships with KiCad 8.

Download: https://www.kicad.org/download/

The script looks for `kicad-cli` in the default Windows installation path
(`C:\Program Files\KiCad\8.0\bin\`) and common Linux paths. KiCad 7 is also accepted as a fallback.

### Git + GitHub CLI

Required by `releaseVersion.py` and `initGitOSMRE.py`.

- Git: https://git-scm.com/downloads
- GitHub CLI (`gh`): https://cli.github.com/

Authenticate `gh` before using `initGitOSMRE.py`:
```
gh auth login
```

---

## Expected folder layout

```
Open-Source-Model-Railway-Electronics/   ← organisation root
├── scripts/                             ← this repository
│   ├── buildGlobal.py
│   ├── releaseVersion.py
│   ├── releaseBoardFiles.py
│   ├── exportSchematics.py
│   └── initGitOSMRE.py
├── OS-software-tool/                    ← hex distribution repo
├── OS-Solenoid-Decoder/
│   ├── software/
│   │   └── .vscode/tasks.json           ← calls ../../scripts/buildGlobal.py
│   ├── hardware/
│   └── releases/
└── OS-<other-repos>/
```

The VS Code `tasks.json` in each project's `software/` folder already points to these scripts via a relative path (`../../scripts/<script>.py`), so no PATH changes are needed.

---

## Scripts

### `buildGlobal.py`

**Run from:** a repo's `software/` folder.

Compiles the firmware with arduino-cli, copies the resulting `.hex` to `releases/<repo-name>.hex` and to `OS-software-tool/<repo-name>.hex`, then removes the build folder.

```
cd OS-Solenoid-Decoder/software
python ../../scripts/buildGlobal.py
```

In VS Code this is wired to the **Build** task (`Ctrl+Shift+B`).

---

### `releaseVersion.py`

**Run from:** a repo's `software/` folder.

Interactive release wizard. Steps through:
1. Ask for the version number (e.g. `v1.2.0`)
2. Ask for a changelog description
3. Write `src/version.h` with the new version string
4. Build the firmware via `src/build.py`
5. Git commit (using the changelog text as the commit message)
6. Create a git tag
7. Update `changelog.txt` from the git log
8. Push to remote including the tag

```
cd OS-Solenoid-Decoder/software
python ../../scripts/releaseVersion.py
```

In VS Code this is the **Release new version** task.

---

### `releaseBoardFiles.py`

**Run from:** the organisation root, or from a single repo root.

After exporting production files from KiCad (Fabrication → JLCPCB), this script:
1. Finds all `jlcpcb/production_files/` folders recursively
2. Copies `BOM-*.csv`, `CPL-*.csv`, and `GERBER-*.zip` to the correct `releases/` folder
3. Removes the `jlcpcb/` folder and any stale `fp-info-cache` files

```
cd Open-Source-Model-Railway-Electronics
python scripts/releaseBoardFiles.py
```

---

### `exportSchematics.py`

**Run from:** the organisation root.

Scans every repo for a KiCad root schematic (the `.kicad_sch` whose filename starts with the repo name) and exports it to `releases/schematic-<name>.pdf` using `kicad-cli`. Hierarchical schematics export as a single multi-page PDF. Cleans up any stray PDFs that `kicad-cli` writes into the `hardware/` folder.

```
cd Open-Source-Model-Railway-Electronics
python scripts/exportSchematics.py
```

---

### `initGitOSMRE.py`

**Run from:** the root of a new, not-yet-published repo.

Automates the first-time repository setup:
1. Initialises a local git repo (`git init`)
2. Creates a minimal `README.md` and `.gitignore` if not present
3. Makes an initial commit with just those two files
4. Creates a `v0.0.0` tag
5. Creates a public repository under the `Open-Source-Model-Railway-Electronics` GitHub organisation
6. Pushes the initial commit and the tag

Requires the GitHub CLI to be installed and authenticated (`gh auth login`).

```
cd Open-Source-Model-Railway-Electronics/OS-NewProject
python ../scripts/initGitOSMRE.py
```
