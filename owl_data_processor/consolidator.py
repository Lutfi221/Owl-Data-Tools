"""Collection of classes that are used for consolidating log data.
"""

from __future__ import annotations

from typing import Optional
from .types import EntryData, WindowData


class ConsolidatorDictionary:
    """A wrapper of a dictionary intended to store values and
    their index. This class is used to reduce redundant data
    being stored in memory/file.

    It provides a :meth:`use_value` method that takes a value
    as input, and returns a unique number representing it.

    In order to get the value represented by a number, you will
    need to get the list of values in the dictionary by calling
    :meth:`generate_values_list`, and using the unique number
    as index for the list. See the examples below for more
    clarity.

    Examples
    --------
    >>> limb_dict = ConsolidatorDictionary()
    >>> limbs = []
    >>> limbs.append(limb_dict.use_value("head"))
    >>> limbs.append(limb_dict.use_value("arm"))
    >>> limbs.append(limb_dict.use_value("arm"))
    >>> limbs.append(limb_dict.use_value("leg"))
    >>> limbs.append(limb_dict.use_value("leg"))
    >>> print(limbs)
    [0, 1, 1, 2, 2]
    >>> limbs_list = limb_dict.generate_values_list()
    >>> print(limb_list[limbs[2]])
    arm
    """

    _dict: dict[str, int]
    _size = 0

    def __init__(self):
        self._dict = {}

    def use_value(self, value: str) -> int:
        """Gets or creates the unique dictionary index
        for `value`.

        Parameters
        ----------
        value : str
            Value to be referenced from the dictionary.

        Returns
        -------
        int
            The dictionary index for `value`
        """
        if value in self._dict:
            return self._dict[value]

        self._dict[value] = self._size
        self._size += 1

        return self._dict[value]

    def generate_values_list(self) -> list[str]:
        """Generates a list of values that has been used.

        Returns
        -------
        list[str]
            List of values
        """
        values = [""] * self._size
        for value, index in self._dict.items():
            values[index] = value

        return values


class Consolidator:
    _path_cd: ConsolidatorDictionary
    _title_cd: ConsolidatorDictionary

    _entries: list[_EntryConsolidated]

    def __init__(self):
        self._path_cd = ConsolidatorDictionary()
        self._title_cd = ConsolidatorDictionary()

    def insert_entry(self, entry: EntryData):
        """Insert entry to consolidate.

        Parameters
        ----------
        entry : EntryData
            Entry data
        """
        self._entries.append(_EntryConsolidated(entry, self._path_cd, self._title_cd))

    def generate_col(self):
        """Generate a consolidated owl logs object."""
        pass


class _WindowConsolidated:
    _path_i: int
    _title_i: int
    _is_active: bool

    __slots__ = ("_path_i", "_title_i", "_is_active")

    def __init__(
        self,
        window: WindowData,
        path_cd: ConsolidatorDictionary,
        title_cd: ConsolidatorDictionary,
    ):
        self._path_i = path_cd.use_value(window["path"])
        self._title_i = title_cd.use_value(window["title"])

        if "isActive" in window:
            self._is_active = window["isActive"]
        else:
            self._is_active = False


class _EntryConsolidated:
    _timestamp: int
    _duration_since_last_input: Optional[int]
    _windows: list[_WindowConsolidated]

    __slots__ = ("_timestamp", "_duration_since_last_input", "_windows")

    def __init__(
        self,
        entry: EntryData,
        path_cd: ConsolidatorDictionary,
        title_cd: ConsolidatorDictionary,
    ):
        self._windows = []

        self._timestamp = entry["timestamp"]
        self._duration_since_last_input = entry["durationSinceLastUserInput"]

        if "windows" in entry:
            for w in entry["windows"]:
                self._windows.append(_WindowConsolidated(w, path_cd, title_cd))
