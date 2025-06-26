import logging
from pathlib import Path
from archive_utils import extract_archive, list_archive_contents

logger = logging.getLogger(__name__)

def extract_nsis_installer(installer_path, output_dir):
    """
    Extract an NSIS installer using 7z and return extracted files.

    Args:
        installer_path (str or Path): Path to NSIS installer .exe
        output_dir (str or Path): Directory to extract contents to

    Returns:
        list of Path: Extracted file paths
    """
    logger.info(f"Starting extraction for: {installer_path}")
    extracted_files = extract_archive(installer_path, output_dir)
    logger.info(f"Extracted {len(extracted_files)} files to {output_dir}")
    return extracted_files

def list_nsis_contents(installer_path):
    """
    List contents of an NSIS installer.

    Args:
        installer_path (str or Path): Path to NSIS installer .exe

    Returns:
        list of dict: File metadata entries
    """
    logger.info(f"Listing contents of: {installer_path}")
    contents = list_archive_contents(installer_path)
    logger.info(f"Found {len(contents)} entries in the archive")
    return contents

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract and list NSIS installer contents")
    parser.add_argument("installer", help="Path to NSIS installer .exe")
    parser.add_argument("-o", "--output", default="extracted_files", help="Output directory for extraction")
    parser.add_argument("-l", "--list", action="store_true", help="Only list archive contents, do not extract")
    args = parser.parse_args()

    if args.list:
        files = list_nsis_contents(args.installer)
        for f in files:
            print(f"{f['Date']} {f['Time']} {f['Attr']} {f['Size']:>10} {f['Compressed']:>10} {f['Name']}")
    else:
        extracted = extract_nsis_installer(args.installer, args.output)
        print(f"Extracted {len(extracted)} files to {args.output}")
