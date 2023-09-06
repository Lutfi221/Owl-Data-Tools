"""Collection of classes that are used for consolidating log data.
"""

from __future__ import annotations
from typing import Optional, Sequence, TypedDict
from ..exceptions import OwlError

from owl_data_processor.types import Window
from ..utils import find_first
from ..version import VERSION

from .consolidated_owl_logs import ConsolidatedOwlLogs
from .dictionary import Dictionary, DictionaryMapper
from ..types import Entry, EntryData, Window, WindowData


class Consolidator:
    """Class used to consolidate multiple entries into a unified object."""

    _path_cd: Dictionary
    _title_cd: Dictionary

    _entries: list[_Entry]
    _optimized = True
    """If :class:`Consolidator` is in an optimized state."""

    def __init__(self):
        """Constructs :class:`Consolidator`"""
        self._path_cd = Dictionary()
        self._title_cd = Dictionary()
        self._entries = []

    def append_entry(self, entry: EntryData):
        """Append and consolidate entry.

        Entries must be appended in chronological order
        from earliest to latest.

        Parameters
        ----------
        entry : EntryData
            Entry data
        """
        if len(self._entries) > 0 and self._entries[-1].timestamp > entry["timestamp"]:
            raise OwlError(
                "Attempting to append an entry with a timestamp earlier "
                "than the latest entry in the Consolidator.\n\n"
                "Make sure the entries you are appending are sorted "
                "chronologically from earliest to latest.\n\n"
                f"Offending entry:\n{str(entry)}"
            )

        self._entries.append(
            _Entry.from_entry_data(entry, self._path_cd, self._title_cd)
        )

        self._optimized = False

    def append_entries(self, entries: Sequence[EntryData]):
        """Append and consolidate entries.

        Entries must be sorted in chronological order
        from earliest to latest.

        Parameters
        ----------
        entries : Sequence[EntryData]
            Entries
        """
        for entry in entries:
            self.append_entry(entry)

    def generate_col(self) -> ConsolidatedOwlLogs:
        """Generate a consolidated owl logs object."""
        paths = self._path_cd.generate_values_list()
        titles = self._title_cd.generate_values_list()
        entries: list[Entry] = [_EntryView(x, paths, titles) for x in self._entries]

        return ConsolidatedOwlLogs(entries, paths, titles)

    def optimize(self):
        """Optimize internal consolidated data."""
        if self._optimized:
            return

        path_i_to_count: list[int] = [0] * self._path_cd.size
        title_i_to_count: list[int] = [0] * self._title_cd.size

        for entry in self._entries:
            for window in entry.windows:
                path_i_to_count[window.path_i] += 1
                title_i_to_count[window.title_i] += 1

        path_i_and_counts: list[tuple[int, int]] = [
            (path_i, count) for path_i, count in enumerate(path_i_to_count)
        ]
        title_i_and_counts: list[tuple[int, int]] = [
            (title_i, count) for title_i, count in enumerate(title_i_to_count)
        ]

        path_i_and_counts.sort(key=lambda x: x[1], reverse=True)
        title_i_and_counts.sort(key=lambda x: x[1], reverse=True)

        old_path_i_to_new: list[int] = [0] * len(path_i_and_counts)
        old_title_i_to_new: list[int] = [0] * len(title_i_and_counts)

        for new_i, [old_i, _] in enumerate(path_i_and_counts):
            old_path_i_to_new[old_i] = new_i
        for new_i, [old_i, _] in enumerate(title_i_and_counts):
            old_title_i_to_new[old_i] = new_i

        for entry in self._entries:
            for window in entry.windows:
                window.path_i = old_path_i_to_new[window.path_i]
                window.title_i = old_title_i_to_new[window.title_i]

        paths = self._path_cd.generate_values_list()
        titles = self._title_cd.generate_values_list()

        self._path_cd = Dictionary([paths[i] for [i, _] in path_i_and_counts])
        self._title_cd = Dictionary([titles[i] for [i, _] in title_i_and_counts])

        self._optimized = True

    def serialize(self, optimize=True) -> ConsolidatedOwlLogsSerialized:
        """Generate JSON-serializable dictionary.

        Parameters
        ----------
        optimize : bool, optional
            Optimize :class:`Consolidator` before
            serializing, by default True.

        Returns
        -------
        ConsolidatedOwlLogsSerialized
            Serialized consolidated owl logs.
        """
        if optimize:
            self.optimize()

        obj: ConsolidatedOwlLogsSerialized = {
            "version": ".".join(map(str, VERSION)),
            "dictionaries": [],
            "entries": [],
        }

        obj["dictionaries"].append(
            {"name": "windows[].path", "set": self._path_cd.generate_values_list()}
        )
        obj["dictionaries"].append(
            {"name": "windows[].title", "set": self._title_cd.generate_values_list()}
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

    def append_from_serialized(self, serialized: ConsolidatedOwlLogsSerialized):
        """Append from serialized data.

        Parameters
        ----------
        serialized : ConsolidatedOwlLogsSerialized
            Serialized :class:`Consolidator`
        """
        title_set = find_first(  # type: ignore
            serialized["dictionaries"], lambda elem: elem["name"] == "windows[].title"
        )["set"]
        path_set = find_first(  # type: ignore
            serialized["dictionaries"], lambda elem: elem["name"] == "windows[].path"
        )["set"]

        title_dmap = DictionaryMapper(title_set, self._title_cd)
        path_dmap = DictionaryMapper(path_set, self._path_cd)

        for entry in serialized["entries"]:
            windows_mapped: list[_Window] = []

            if "windows" in entry:
                for w in entry["windows"] or []:
                    windows_mapped.append(
                        _Window(
                            path_dmap.source_to_target(w["path"]),
                            title_dmap.source_to_target(w["title"]),
                            w.get("isActive") or False,
                        ),
                    )

            self._entries.append(
                _Entry(
                    entry["time"], windows_mapped, entry.get("durationSinceLastInput")
                )
            )

        self._optimized = False


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

    path_i: int
    title_i: int
    is_active: bool

    __slots__ = ("path_i", "title_i", "is_active")

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
        self.path_i = path_i
        self.title_i = title_i
        self.is_active = is_active

    @classmethod
    def from_window_data(
        cls,
        window: WindowData,
        path_cd: Dictionary,
        title_cd: Dictionary,
    ) -> _Window:
        """Create window structure from :class:`WindowData`,
        and path and title :class:`Dictionary`.

        Parameters
        ----------
        window : WindowData
            Window data
        path_cd : Dictionary
            Paths dictionary
        title_cd : Dictionary
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
