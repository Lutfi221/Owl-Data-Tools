"""Collection of classes that are used for consolidating log data.
"""

from __future__ import annotations
from typing import Optional, Sequence, TypedDict

from owl_data_processor.types import Window
from ..version import VERSION

from .consolidated_owl_logs import ConsolidatedOwlLogs
from .dictionary import Dictionary
from ..types import Entry, EntryData, Window, WindowData


class Consolidator:
    """Class used to consolidate multiple entries into a unified object."""

    _path_cd: Dictionary
    _title_cd: Dictionary

    _entries: list[_Entry]

    def __init__(self):
        """Constructs :class:`Consolidator`"""
        self._path_cd = Dictionary()
        self._title_cd = Dictionary()
        self._entries = []

    def append_entry(self, entry: EntryData):
        """Append and consolidate entry.

        Parameters
        ----------
        entry : EntryData
            Entry data
        """
        self._entries.append(
            _Entry.from_entry_data(entry, self._path_cd, self._title_cd)
        )

    def append_entries(self, entries: Sequence[EntryData]):
        """Append and consolidate entries."""
        for entry in entries:
            self.append_entry(entry)

    def generate_col(self) -> ConsolidatedOwlLogs:
        """Generate a consolidated owl logs object."""
        paths = self._path_cd.generate_values_list()
        titles = self._title_cd.generate_values_list()
        entries: list[Entry] = [_EntryView(x, paths, titles) for x in self._entries]

        return ConsolidatedOwlLogs(entries, paths, titles)

    def serialize(self) -> ConsolidatedOwlLogsSerialized:
        """Generate JSON-serializable dictionary."""
        obj: ConsolidatedOwlLogsSerialized = {
            "version": ".".join(map(str, VERSION)),
            "dictionaries": [],
            "entries": [],
        }

        obj["dictionaries"].append(
            {"name": "windows.path", "set": self._path_cd.generate_values_list()}
        )
        obj["dictionaries"].append(
            {"name": "windows.title", "set": self._title_cd.generate_values_list()}
        )

        for entry in self._entries:
            windows_serialized: list[_ColsWindowData] = []

            for window in entry.windows:
                window_serialized: _ColsWindowData = {  # type: ignore
                    "title": window.title_i,
                    "path": window.path_i,
                }
                if window.is_active:
                    window_serialized["isActive"] = True

                windows_serialized.append(window_serialized)

            entry_serialized: _ColsEntryData = {  # type: ignore
                "time": entry.timestamp,
                "windows": windows_serialized,
            }
            if entry.duration_since_last_input is not None:
                entry_serialized[
                    "durationSinceLastInput"
                ] = entry.duration_since_last_input

            obj["entries"].append(entry_serialized)

        return obj


class _WindowView(Window):
    _window: _Window
    _paths: list[str]
    _titles: list[str]

    __slots__ = ("_window", "_paths", "_titles")

    def __init__(self, window: _Window, paths: list[str], titles: list[str]):
        self._window = window
        self._paths = paths
        self._titles = titles

    @property
    def path(self) -> str:
        return self._paths[self._window.path_i]

    @property
    def title(self) -> str:
        return self._titles[self._window.title_i]

    @property
    def is_active(self) -> bool:
        return self._window.is_active


class _EntryView(Entry):
    _entry: _Entry
    _paths: list[str]
    _titles: list[str]

    __slots__ = ("_entry", "_paths", "_titles")

    def __init__(self, entry: _Entry, paths: list[str], titles: list[str]):
        self._entry = entry
        self._paths = paths
        self._titles = titles

    @property
    def timestamp(self) -> int:
        return self._entry.timestamp

    @property
    def duration_since_last_input(self):
        return self._entry.duration_since_last_input

    @property
    def windows_view(self) -> list[_WindowView]:
        return [_WindowView(x, self._paths, self._titles) for x in self._entry.windows]


class _Window:
    """One-off private class to store window data
    only to be used in :class:`Consolidator`.
    """

    _path_i: int
    _title_i: int
    _is_active: bool

    __slots__ = ("_path_i", "_title_i", "_is_active")

    def __init__(self, path_i: int, title_i: int, is_active=False):
        """
        Parameters
        ----------
        path_i : int
            Window path's index
        title_i : int
            Window title's index
        is_active : bool, optional
            True if the user is active in the window, by default False
        """
        self._path_i = path_i
        self._title_i = title_i
        self._is_active = is_active

    @classmethod
    def from_window_data(
        cls,
        window: WindowData,
        path_cd: Dictionary,
        title_cd: Dictionary,
    ) -> _Window:
        """Create window structure from :class:`.types.WindowData`,
        and path and title :class:`ConsolidatorDictionary`.

        Parameters
        ----------
        window : WindowData
            Window data
        path_cd : ConsolidatorDictionary
            Paths dictionary
        title_cd : ConsolidatorDictionary
            Titles dictionary

        Returns
        -------
        _Window
        """
        path_i = path_cd.use_value(window.get("path") or "")
        title_i = title_cd.use_value(window.get("title") or "")

        is_active = False
        if "isActive" in window:
            is_active = window["isActive"]

        return cls(path_i, title_i, bool(is_active))

    @property
    def path_i(self):
        """Window path dictionary index"""
        return self._path_i

    @property
    def title_i(self):
        """Window title dictionary index"""
        return self._title_i

    @property
    def is_active(self):
        """True if user is active in the window,
        False otherwise
        """
        return self._is_active


class _Entry:
    """One-off private class to store entry data
    only to be used in :class:`Consolidator`.
    """

    _timestamp: int
    _duration_since_last_input: Optional[int]
    _windows: list[_Window]

    __slots__ = ("_timestamp", "_duration_since_last_input", "_windows")

    def __init__(
        self,
        timestamp: int,
        windows: list[_Window],
        duration_since_last_input: Optional[int],
    ):
        """Constructs :class:`_Entry`."""
        self._timestamp = timestamp
        self._windows = windows
        self._duration_since_last_input = duration_since_last_input

    @classmethod
    def from_entry_data(
        cls,
        entry: EntryData,
        path_cd: Dictionary,
        title_cd: Dictionary,
    ) -> _Entry:
        """Creates :class:`_Entry` using :class:`EntryData`."""
        windows = []
        timestamp = entry["timestamp"]
        if "durationSinceLastUserInput" in entry:
            duration_since_last_input = entry["durationSinceLastUserInput"]
        else:
            duration_since_last_input = None

        entry_windows = entry.get("windows")
        if entry_windows:
            for w in entry_windows:
                windows.append(_Window.from_window_data(w, path_cd, title_cd))

        return cls(timestamp, windows, duration_since_last_input)

    @property
    def timestamp(self):
        """Timestamp when the entry was recorded."""
        return self._timestamp

    @property
    def duration_since_last_input(self):
        """Duration since last user input."""
        return self._duration_since_last_input

    @property
    def windows(self):
        """Windows captured."""
        return self._windows


class ConsolidatedOwlLogsSerialized(TypedDict):
    """Serialized consolidated owl logs data."""

    version: str
    dictionaries: list[_ColsDictionaryData]
    entries: list[_ColsEntryData]


class _ColsDictionaryData(TypedDict):
    """Consolidated owl logs dictionary data."""

    name: str
    set: list[str]


class _ColsEntryData(TypedDict):
    """Consolidated owl logs entry data."""

    time: int
    durationSinceLastInput: Optional[int]
    windows: Optional[list[_ColsWindowData]]


class _ColsWindowData(TypedDict):
    """Consolidated owl logs window data."""

    path: int
    title: int
    isActive: Optional[bool]
