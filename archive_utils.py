import subprocess
import shutil
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def get_7z_path():
    """
    Locate the 7-Zip executable in common locations or the system PATH.

    Returns:
        str: Path to the 7z executable.

    Raises:
        FileNotFoundError: If 7z executable is not found.
    """
    # Check environment variable first
    env_path = os.environ.get("SEVEN_ZIP_PATH")
    if env_path and shutil.which(env_path):
        logger.debug(f"Found 7z executable in SEVEN_ZIP_PATH: {env_path}")
        return env_path

    # Common executable names
    candidates = ["7z", "7za", "7zr"]

    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            logger.debug(f"Found 7z executable: {path}")
            return path

    raise FileNotFoundError("7z executable not found. Please install 7-Zip or set SEVEN_ZIP_PATH environment variable.")

def list_archive_contents(filepath):
    """
    List contents of an archive using 7z.

    Args:
        filepath (str or Path): Path to archive file.

    Returns:
        list of dict: List of file metadata dictionaries with keys like 'Date', 'Time', 'Attr', 'Size', 'Compressed', 'Name'.
    """
    path_7z = get_7z_path()
    try:
        completed = subprocess.run(
            [path_7z, "l", str(filepath)],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"7z list command failed: {e}")
        raise

    return _parse_7z_list_output(completed.stdout)

def _parse_7z_list_output(output):
    """
    Parse the output from '7z l' command.

    Returns:
        list of dict: Each dict represents one file entry.
    """
    lines = output.splitlines()
    entries = []
    start = False

    for line in lines:
        # The header line that starts the file listing usually looks like:
        # Date      Time    Attr         Size   Compressed  Name
        if line.strip().startswith("Date"):
            start = True
            continue
        if not start:
            continue
        if line.strip() == "" or line.startswith("----"):
            continue
        if line.startswith("---------"):
            break

        # Split fixed width columns: Date, Time, Attr, Size, Compressed, Name
        # We can split by spaces but name can have spaces, so we carefully parse:
        try:
            date = line[0:10].strip()
            time = line[11:19].strip()
            attr = line[20:28].strip()
            size = line[29:40].strip()
            compressed = line[41:53].strip()
            name = line[54:].strip()
        except Exception as e:
            logger.debug(f"Skipping unparsable line: {line}")
            continue

        entries.append({
            "Date": date,
            "Time": time,
            "Attr": attr,
            "Size": size,
            "Compressed": compressed,
            "Name": name,
        })

    return entries

def extract_archive(filepath, output_dir):
    """
    Extract archive files using 7z.

    Args:
        filepath (str or Path): Path to archive file.
        output_dir (str or Path): Directory to extract files into.

    Returns:
        list of Path: List of extracted file paths.
    """
    path_7z = get_7z_path()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(
            [path_7z, "x", str(filepath), f"-o{output_dir}", "-y"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Extraction failed: {e}")
        raise

    extracted_files = list(output_dir.rglob("*"))
    return extracted_files
