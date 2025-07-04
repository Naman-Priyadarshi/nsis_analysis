# NSIS Analysis

A tool for analyzing [NSIS](https://nsis.sourceforge.io/) installer files and `.nsi` scripts to detect potentially suspicious behavior, optionally submitting them to [Hybrid Analysis](https://www.hybrid-analysis.com/) for sandbox scanning.

---

## Features

- Extracts NSIS `.exe` installers using built-in archive support.
- Detects and analyzes `.nsi` scripts for suspicious commands and keywords.
- Scan PE headers for metadata using `pefile`
- Assigns a **suspicion score** based on findings.
- Optionally submits files to **Hybrid Analysis** public API for malware scanning.
- Supports listing contents of installer archives.

---

## Requirements

- Python 3.7+
- 7zip installed and available in your system PATH (required for extraction)
  - **Windows:** Install [7-Zip](https://www.7-zip.org/) and add to PATH
  - **Linux:** Install `p7zip-full` via package manager (`sudo apt install p7zip-full`)
  - **macOS:** Install via Homebrew (`brew install p7zip`)

---

## Installation

```bash
git clone https://github.com/Naman-Priyadarshi/nsis_analysis.git
cd nsis_analysis
python -m venv .env
source .env/bin/activate
pip install -e .
```

> **Note:** If you're submitting to Hybrid Analysis, you'll need an API key. Set it via environment variable or directly in `main.py`.

---

## Usage

```bash
python main.py <file> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `<file>` | Path to `.nsi` script or `.exe` NSIS installer |

### Options

| Option            | Description |
|------------------|-------------|
| `-l`, `--list`   | List contents of an installer archive without extracting |
| `-o <dir>`       | Output directory to extract files (default: temporary folder) |
| `--submit`       | Submit file to Hybrid Analysis for sandbox scanning |

---

## Examples

### Analyze `.nsi` script locally:

```bash
python main.py tests/suspicious.nsi
```

### Analyze `.exe` installer and extract files:

```bash
python main.py installers/hello.exe
```

### List contents of installer without extracting:

```bash
python main.py installers/hello.exe --list
```

### Submit file to Hybrid Analysis:

```bash
python main.py tests/suspicious.nsi --submit
```

---

## Suspicion Scoring

The analyzer detects:

- **Suspicious NSIS commands** (e.g., `ExecShell`, `WriteRegStr`, `Delete`)
- **Suspicious keywords** (e.g., `hacker`, `keylogger`, `backdoor`)
- Assigns a score based on matches (threshold = 7)
- Shows a warning if the installer is flagged as suspicious

Example output:

```
[+] Detected NSI script: tests/suspicious.nsi
Suspicious commands detected: ExecShell, Delete
Suspicious keywords detected: keylogger, trojan
Suspicion score: 16
⚠️ Installer flagged as suspicious!
```

---

## Hybrid Analysis API

To enable submissions, get a free API key from [Hybrid Analysis](https://www.hybrid-analysis.com/) and set it via environment variable:

```bash
export HYBRID_ANALYSIS_API_KEY=your_api_key_here
```

Or update the `hybrid_api_key` in `main.py` directly. (not recommended)

---

## TODO / Improvements

- Add GUI or web interface
- Better parsing of NSIS commands/arguments
- Support unpacking encrypted installers
- Store analysis results in JSON
- Convert nsiDecomp to python3 readable code
