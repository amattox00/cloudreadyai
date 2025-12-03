from pathlib import Path
from typing import Iterable, List

import zipfile

from .utils import ensure_reports_dir


def create_zip_package(run_id: str, files: Iterable[Path]) -> Path:
    """
    Create a ZIP package for the given run_id containing the provided files.

    Returns the path to the created ZIP file.
    """
    reports_dir = ensure_reports_dir(run_id)
    zip_path = reports_dir / "CloudReadyAI-Assessment-Package.zip"

    # Normalize to list and filter out missing files
    file_list: List[Path] = [
        Path(f) for f in files if f is not None and Path(f).is_file()
    ]

    if not file_list:
        # We still create an empty zip to avoid 404s in the API layer.
        with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED):
            pass
        return zip_path

    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in file_list:
            # Store files using only the filename (not full path)
            zf.write(file_path, arcname=file_path.name)

    return zip_path
