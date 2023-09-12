import json
import os
from pathlib import Path

import pytest

from .types import EntryData

from .consolidation.consolidator import Consolidator
from .__main__ import main

ENTRIES_ORIGINAL: list[EntryData] = [  # type: ignore
    {
        "timestamp": 0,
        "windows": [
            {"path": "/program/0.exe", "title": "Zero"},
            {"path": "/program/1.exe", "title": "One", "isActive": True},
            {"path": "/program/2.exe", "title": "Two"},
        ],
    },
    {"timestamp": 1, "durationSinceLastUserInput": 60},
    {
        "timestamp": 2,
        "windows": [
            {"path": "/program/1.exe", "title": "One", "isActive": True},
            {"path": "/program/2.exe", "title": "Two"},
        ],
    },
    {"timestamp": 3, "windows": [{"path": "/program/0.exe", "title": "Zero"}]},
]


def entries_to_json_lines(entries: list[EntryData]) -> str:
    return "\n".join([json.dumps(entry) for entry in entries])


def test_basic(tmp_path):

    root: Path = tmp_path
    print(f"tmp_path: {root}")

    p_one = root / "one.json.log"
    p_two = root / "two.txt"
    p_three = root / "three.json.log"
    p_out = root / "output.json"

    p_one.write_text(entries_to_json_lines(ENTRIES_ORIGINAL[:-2]))
    p_two.write_text("This file should be ignored")
    p_three.write_text(entries_to_json_lines(ENTRIES_ORIGINAL[2:]))

    consolidator_original = Consolidator()
    consolidator_original.append_entries(ENTRIES_ORIGINAL)
    col_serialized_original = consolidator_original.serialize()

    #
    main(
        [
            "main.py",
            "--input",
            "./one.json.log",
            "-i",
            ".\\three.json.log",
            "-o",
            "./output.json",
        ],
        root,
    )
    assert col_serialized_original == json.loads(p_out.read_text("utf-8"))

    #
    os.remove(p_out)
    main(["main.py", "--input", "*", "-o", "./output.json"], root)
    assert col_serialized_original == json.loads(p_out.read_text("utf-8"))

    #
    p_three.write_text("{invalid json")
    with pytest.raises(json.JSONDecodeError):
        main(["main.py", "--input", "*", "-o", "./output.json"], root)


def test_serialized_json(tmp_path: Path):
    consolidator_reference = Consolidator()
    consolidator_reference.append_entries(ENTRIES_ORIGINAL)

    root = tmp_path
    print(f"tmp_path: {root}")

    p_one = root / "one.json.log"
    p_two = root / "two.json"
    p_out = root / "output.json"

    p_one.write_text(entries_to_json_lines(ENTRIES_ORIGINAL[:-2]))

    p_two_consolidator = Consolidator()
    p_two_consolidator.append_entries(ENTRIES_ORIGINAL[2:])
    p_two.write_text(json.dumps(p_two_consolidator.serialize()))

    main(
        ["main.py", "-i", "one.json.log", "-i", "two.json", "-o", "./output.json"], root
    )

    assert consolidator_reference.serialize() == json.loads(p_out.read_text("utf-8"))

    #
    p_two.write_text("{invalid json")
    with pytest.raises(json.JSONDecodeError):
        main(
            ["main.py", "-i", "one.json.log", "-i", "two.json", "-o", "./output.json"],
            root,
        )
