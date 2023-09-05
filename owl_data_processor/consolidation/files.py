from glob import iglob
import json
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

from .consolidator import Consolidator


def consolidator_from_files(
    file_patterns: Sequence[str],
    output_paths: Optional[Sequence[str]] = None,
    root_dir: Optional[Path] = None,
    entry_transform: Optional[Callable[[dict[str, Any]], None]] = None,
) -> Consolidator:
    """Create an instance of :class:`Consolidator` from multiple files.

    Parameters
    ----------
    file_patterns : Sequence[str]
        List of file path patterns. Normal paths, and globs are supported.
    output_paths : Optional[Sequence[str]], optional
        Output file paths, by default None
    root_dir : Optional[Path], optional
        Root directory to resolve any relative file paths, by default None
    entry_transform : Optional[Callable[[dict[str, Any]], None]], optional
        Function that transform the entry JSON before being
        fed into :class:`Consolidator`, by default None

    Returns
    -------
    Consolidator
    """
    consolidator = Consolidator()

    for file_pattern in file_patterns:
        for path_str in iglob(file_pattern, root_dir=root_dir, recursive=True):
            path = Path(path_str)
            if root_dir and not path.exists():
                path = Path(root_dir) / path

            print(path, end="\t")

            if "".join(path.suffixes).endswith(".json.log"):
                with open(path, "r", encoding="utf-8") as f:
                    for no, line in enumerate(f.readlines(), 1):
                        if "{" in line:
                            try:
                                entry = json.loads(line)
                                if entry_transform:
                                    entry_transform(entry)
                                consolidator.insert_entry(entry)
                            except Exception as e:
                                print(
                                    f"\nException occured while processing `{path}` "
                                    f"at line no: {no}"
                                )
                                raise e

                print("(LOADED)")
            else:
                print("(IGNORED)")

    col_json = json.dumps(consolidator.serialize())

    if output_paths:
        for path_str in output_paths:
            path = Path(path_str)
            if root_dir and not path.exists():
                path = Path(root_dir) / path

            print(path, end="\t")
            with open(path, "w", encoding="utf-8") as f:
                f.write(col_json)

            print("(OUTPUT)")

    return consolidator
