"""Collection of classes that are used for consolidating log data.
"""

from __future__ import annotations

from typing import Optional

from .dictionary import Dictionary

from ..types import EntryData, WindowData


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

    def generate_col(self):
        """Generate a consolidated owl logs object."""
        pass


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
        entry: EntryData,
        path_cd: Dictionary,
        title_cd: Dictionary,
    ):
        """Constructs :class:`_Entry`."""
        self._windows = []

        self._timestamp = entry["timestamp"]
        self._duration_since_last_input = entry["durationSinceLastUserInput"]

        if "windows" in entry:
            for w in entry["windows"]:
                self._windows.append(_Window(w, path_cd, title_cd))

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
