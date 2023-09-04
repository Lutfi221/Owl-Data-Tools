"""
Commonly used data structures
"""

from __future__ import annotations
from typing import Generic, Optional, Sequence, TypeVar, TypedDict
from abc import ABC, abstractmethod

T = TypeVar("T")
"""Type variable used as a paremeter for generics
"""


class RangeView(Sequence, Generic[T]):
    """Readonly view of a list of things with type `T`.

    Rangeview helps with passing long subsections of a very long list
    to other functions or classes without unnecessary duplication
    of the data in the list. It is useful when you want to view
    or process only a subsection of a long list.
    >>>
    """

    _items: list[T]
    _start_i: int
    _len: int

    def __init__(self, start_i: int, n_items: int, items: list[T]):
        """Create a rangeview from the list of items.

        Parameters
        ----------
        start_i : int
            Index where the rangeview begins.
        n_items : int
            Number of items the rangeview will contain.
        items : list[T]
            List of items.
        """
        self._items = items
        self._start_i = start_i
        self._len = n_items

    def __getitem__(self, index: int) -> T:
        """Get item."""
        if index < 0 or index >= self._len:
            raise IndexError(f"Rangeview index out of range.\n" f"index={index}")

        return self._items[self._start_i + index]

    def __len__(self) -> int:
        """Get the number of items."""
        return self._len


class Entry(ABC):
    _windows_view: Sequence[Window]

    def __init__(
        self,
        timestamp: int,
        windows_view: Optional[Sequence[Window]] = None,
        duration_since_last_input: Optional[int] = None,
    ):
        self._timestamp = timestamp
        if windows_view:
            self._windows_view = windows_view
        else:
            self._windows_view = []  # type: ignore
        self._duration_since_last_input = duration_since_last_input

    @property
    def timestamp(self) -> int:
        """Timestamp when the entry was recorded."""
        return self._timestamp

    @property
    def duration_since_last_input(self) -> Optional[int]:
        """Duration since last user input."""
        return self._duration_since_last_input

    @property
    def windows_view(self) -> Sequence[Window]:
        """Readonly range view of the windows contained in the entry."""
        return self._windows_view


class Window(ABC):
    def __init__(self, path, title, is_active=False):
        self._path = path
        self._title = title
        self._is_active = is_active

    @property
    def path(self) -> str:
        """Program path that owns the window."""
        return self._path

    @property
    def title(self) -> str:
        """Title of the window."""
        return self._title

    @property
    def is_active(self) -> bool:
        """If the user is currently active on the window."""
        return self._is_active


class WindowData(TypedDict):
    """Describes a window of a program"""

    path: Optional[str]
    """Path to the program that owns the window
    """

    title: Optional[str]
    """Window title
    """

    isActive: Optional[bool]
    """True ff the user is active in this window
    """


class EntryData(TypedDict):
    """Describes the state of a computer at a point of time."""

    timestamp: int
    """The time when the entry was recorded.
    """

    windows: Optional[list[WindowData]]
    """List of windows that are opened.
    """

    durationSinceLastUserInput: Optional[int]
    """Duration (in seconds) since the last user input.
    """
