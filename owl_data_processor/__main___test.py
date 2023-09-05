import json
from pathlib import Path

import pytest

from .consolidation.consolidator import Consolidator
from .__main__ import main


def test_basic(tmp_path):
    entries_original = [
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

    root: Path = tmp_path
    print(f"tmp_path: {root}")

    p_one = root / "one.json.log"
    p_two = root / "two.txt"
    p_three = root / "three.json.log"
    p_out = root / "output.json"

    p_one.write_text("\n".join([json.dumps(entry) for entry in entries_original[:-2]]))
    p_two.write_text("This file should be ignored")
    p_three.write_text("\n".join([json.dumps(entry) for entry in entries_original[2:]]))

    consolidator_original = Consolidator()
    consolidator_original.insert_entries(entries_original)
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
    p_out.write_text("")
    main(["main.py", "--input", "*", "-o", "./output.json"], root)
    assert col_serialized_original == json.loads(p_out.read_text("utf-8"))

    #
    p_three.write_text("{invalid json")
    with pytest.raises(json.JSONDecodeError):
        main(["main.py", "--input", "*", "-o", "./output.json"], root)
