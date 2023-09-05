"""Large objects and dictionaries used for testing."""

from typing import TypedDict

from ..version import VERSION

from .consolidator import ConsolidatedOwlLogsSerialized
from ..types import EntryData

VERSION_STRING = ".".join(map(str, VERSION))


class SerializationTestObject(TypedDict):
    _description: str
    """Short description of the test object.
    Purpose, and scope of the test should be included here.
    
    This is just to help developers to understand the test objects more easier.
    """
    before: list[EntryData]
    after: ConsolidatedOwlLogsSerialized


SERIALIZATION_TEST_OBJECTS: list[SerializationTestObject] = [
    {
        "_description": "Basic test.",
        "before": [  # type: ignore
            {
                "timestamp": 0,
                "windows": [
                    {"path": "/program/0.exe", "title": "Zero"},
                    {"path": "/program/1.exe", "title": "One", "isActive": True},
                    {"path": "/program/2.exe", "title": "Two"},
                ],
            },
            {
                "timestamp": 1,
                "windows": [
                    {"path": "/program/1.exe", "title": "One", "isActive": True},
                    {"path": "/program/2.exe", "title": "Two"},
                ],
            },
            {"timestamp": 2, "durationSinceLastUserInput": 60},
        ],
        "after": {
            "version": VERSION_STRING,
            "dictionaries": [
                {
                    "name": "windows.path",
                    "set": ["/program/0.exe", "/program/1.exe", "/program/2.exe"],
                },
                {"name": "windows.titles", "set": ["Zero", "One", "Two"]},
            ],
            "entries": [
                {
                    "time": 0,
                    "windows": [
                        {"title": 0, "path": 0},
                        {"title": 1, "path": 1, "isActive": True},
                        {"title": 2, "path": 2},
                    ],
                },
                {
                    "time": 1,
                    "windows": [
                        {"title": 1, "path": 1, "isActive": True},
                        {"title": 2, "path": 2},
                    ],
                },
                {"time": 2, "windows": [], "durationSinceLastInput": 60},
            ],
        },
    },
    {
        "_description": "Test to check if empty path and title properties"
        "are handled properly",
        "before": [
            {
                "timestamp": 10010,
                "windows": [
                    {"path": "C:\\program\\chrome.exe", "title": "Chrome"},
                    {"path": "C:\\program\\firefox.exe", "title": "Firefox"},
                ],
            },
            {
                "timestamp": 10020,
                "windows": [
                    {"path": "C:\\program\\chrome.exe", "title": "Chrome"},
                    {"path": "C:\\program\\firefox.exe", "title": "Firefox"},
                    {"path": "", "title": "Task Manager"},
                    {"path": "C:\\notepad.exe", "title": ""},
                    {"path": "", "title": ""},
                    {},
                ],
            },
        ],
        "after": {
            "version": VERSION_STRING,
            "dictionaries": [
                {
                    "name": "windows.path",
                    "set": [
                        "C:\\program\\chrome.exe",
                        "C:\\program\\firefox.exe",
                        "",
                        "C:\\notepad.exe",
                    ],
                },
                {
                    "name": "windows.titles",
                    "set": ["Chrome", "Firefox", "Task Manager", ""],
                },
            ],
            "entries": [
                {
                    "time": 10010,
                    "windows": [{"path": 0, "title": 0}, {"path": 1, "title": 1}],
                },
                {
                    "time": 10020,
                    "windows": [
                        {"path": 0, "title": 0},
                        {"path": 1, "title": 1},
                        {"path": 2, "title": 2},
                        {"path": 3, "title": 3},
                        {"path": 2, "title": 3},
                        {"path": 2, "title": 3},
                    ],
                },
            ],
        },
    },
]
