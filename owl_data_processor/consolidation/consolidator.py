"""Collection of classes that are used for consolidating log data.
"""

from __future__ import annotations
from typing import Optional

from owl_data_processor.types import RangeView, Window

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

    def insert_entry(self, entry: EntryData):
        """Insert entry to consolidate.

        Parameters
        ----------
        entry : EntryData
            Entry data
        """
        self._entries.append(_Entry(entry, self._path_cd, self._title_cd))

    def generate_col(self) -> ConsolidatedOwlLogs:
        """Generate a consolidated owl logs object."""
        paths = self._path_cd.generate_values_list()
        titles = self._title_cd.generate_values_list()
        entries: list[Entry] = [_EntryView(x, paths, titles) for x in self._entries]

        return ConsolidatedOwlLogs(entries, paths, titles)


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

    def timestamp(self) -> int:
        return self._entry.timestamp

    def duration_since_last_input(self) -> int:
        return self._entry.duration_since_last_input

    def windows_view(self) -> RangeView[Window]:
        return [_WindowView(x) for x in self._entry.windows]


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
        self,
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
        path_i = path_cd.use_value(window["path"])
        title_i = title_cd.use_value(window["title"])

        is_active = False
        if "isActive" in window:
            is_active = window["isActive"]

        return _Window(path_i, title_i, is_active)

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
        self,
        entry: EntryData,
        path_cd: Dictionary,
        title_cd: Dictionary,
    ) -> _Entry:
        """Creates :class:`_Entry` using :class:`EntryData`."""
        windows = []
        timestamp = entry["timestamp"]
        duration_since_last_input = entry["durationSinceLastUserInput"]

        if "windows" in entry:
            for w in entry["windows"]:
                windows.append(_Window.from_window_data(w, path_cd, title_cd))

        return _Entry(timestamp, windows, duration_since_last_input)

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
