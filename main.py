import argparse
import tempfile
import shutil
import sys
from pathlib import Path
import requests
import logging

from archive_utils import extract_archive, list_archive_contents
from analyzer import analyze
from pe_analysis import analyze_pe  # Added import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HYBRID_API_URL = "https://www.hybrid-analysis.com/api/v2/quick-scan/file"
hybrid_api_key = "your_api_key"  # set via env var HYBRID_ANALYSIS_API_KEY


def submit_to_hybrid_analysis(file_path, api_key):
    url = HYBRID_API_URL
    headers = {
        "User-Agent": "Falcon Sandbox",
        "api-key": api_key,
        "accept": "application/json",
    }

    files = {
        "file": (file_path.name, open(file_path, "rb"), "application/x-msdownload")
    }

    data = {
        "scan_type": "all"
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        json_response = response.json()
        job_id = json_response.get('job_id') or json_response.get('sha256') or "Unknown"
        print(f"[+] Submission successful! View analysis at: https://www.hybrid-analysis.com/sample/{job_id}")
        return json_response
    else:
        print(f"[!] Submission failed: {response.status_code} {response.reason}")
        print(f"[!] Response body: {response.text}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Extract and analyze NSIS installers, scripts, and PE files")
    parser.add_argument("installer", type=Path, help="Path to NSIS installer (.exe) or NSI script")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output directory for extraction")
    parser.add_argument("-l", "--list", action="store_true", help="Only list archive contents, do not extract")
    parser.add_argument("--submit", action="store_true", help="Submit file to Hybrid Analysis public API")
    args = parser.parse_args()

    installer_path = args.installer

    if not installer_path.exists():
        print(f"[!] File {installer_path} does not exist.")
        sys.exit(1)

    # Analyze with PE analyzer if it's an executable
    if installer_path.suffix.lower() == ".exe":
        print(f"[+] Performing PE analysis on: {installer_path}")
        try:
            pe_info = analyze_pe(installer_path)
            print("[+] PE File Analysis:")
            for key, value in pe_info.items():
                print(f"    {key}: {value}")
        except Exception as e:
            print(f"[!] Error analyzing PE file: {e}")

    # If listing archive contents only
    if args.list:
        print(f"[+] Listing contents of: {installer_path}")
        try:
            files = list_archive_contents(installer_path)
            print(f"Date       Time     Attr       Size   Compressed  Name")
            print("-------------------------------------------------------")
            for f in files:
                print(f"{f['Date']} {f['Time']} {f['Attr']:8} {f['Size']:>10} {f['Compressed']:>10} {f['Name']}")
        except Exception as e:
            print(f"[!] Error listing archive contents: {e}")
        return

    # Detect if input is .nsi script or an installer
    if installer_path.suffix.lower() == ".nsi":
        print(f"[+] Detected NSI script: {installer_path}")

        try:
            findings = analyze(installer_path)
            for line in findings:
                print(line)
        except Exception as e:
            print(f"[!] Error analyzing script {installer_path}: {e}")

    else:
        # Extract and analyze installer .exe
        output_dir = args.output
        temp_dir = None
        if output_dir is None:
            temp_dir = tempfile.TemporaryDirectory(prefix="nsis_extract_")
            output_dir = Path(temp_dir.name)
            print(f"[+] Extracting files to temporary directory: {output_dir}")
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"[+] Extracting files to: {output_dir}")

        try:
            extracted_files = extract_archive(installer_path, output_dir)
            print(f"[+] Extracted {len(extracted_files)} files.")

            if len(extracted_files) == 0:
                print("[!] No files extracted. Are you sure this is a valid NSIS installer?")
            else:
                print("Files found:")
                for f in extracted_files:
                    print(f" - {f.name}")

            # Ask user whether to delete or keep extracted files (only if using temp folder)
            if temp_dir is not None:
                while True:
                    choice = input("Delete extracted files? (Y/n): ").strip().lower()
                    if choice in ("", "y", "yes"):
                        temp_dir.cleanup()
                        print("[+] Extracted files deleted.")
                        break
                    elif choice in ("n", "no"):
                        save_path_input = input("Enter path to save extracted files (will create directory): ").strip()
                        save_path = Path(save_path_input) if save_path_input else Path(".")
                        save_path.mkdir(parents=True, exist_ok=True)
                        for f in extracted_files:
                            target = save_path / f.name
                            shutil.copy2(f, target)
                        print(f"[+] Extracted files saved to: {save_path.resolve()}")
                        break
                    else:
                        print("Please answer Y or n.")

            # Try to find NSI script among extracted files
            nsi_files = [f for f in extracted_files if f.suffix.lower() == ".nsi"]

            if nsi_files:
                print(f"[+] Found NSI script(s): {[f.name for f in nsi_files]}")
                for nsi_file in nsi_files:
                    print(f"\n[+] Analyzing NSI script: {nsi_file}")
                    try:
                        findings = analyze(nsi_file)
                        for line in findings:
                            print(line)
                    except Exception as e:
                        print(f"[!] Error analyzing script {nsi_file}: {e}")
            else:
                print("[!] No NSI scripts found among extracted files.")

        except Exception as e:
            print(f"[!] Extraction failed: {e}")
            if temp_dir:
                temp_dir.cleanup()
            sys.exit(1)

        if temp_dir is not None and Path(temp_dir.name).exists():
            temp_dir.cleanup()

    # Submit to Hybrid Analysis if requested
    if args.submit:
        print(f"[+] Submitting {installer_path.suffix} file to Hybrid Analysis...")
        submit_to_hybrid_analysis(installer_path, hybrid_api_key)


if __name__ == "__main__":
    main()
