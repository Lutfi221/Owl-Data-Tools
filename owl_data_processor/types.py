"""
Commonly used data structures
"""

from __future__ import annotations
from typing import Generic, Optional, TypeVar, TypedDict
from abc import ABC, abstractmethod

T = TypeVar("T")
"""Type variable used as a paremeter for generics
"""


class DataView(Generic[T], ABC):
    """Interface for a read-only view of a list of things
    with type `T`."""

    @abstractmethod
    def __getitem__(self, index: int) -> T:
        """Get item."""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Get the number of items."""
        pass


class Entry(ABC):
    @abstractmethod
    def get_timestamp(self) -> int:
        """Get timestamp when the entry was recorded."""
        pass

    @abstractmethod
    def get_is_user_afk(self) -> bool:
        """Find out if the user is away from keyboard."""
        pass

    @abstractmethod
    def get_duration_since_last_input(self) -> Optional[int]:
        """Get duration since last user input."""
        pass

    @abstractmethod
    def get_windows_view(self) -> DataView[Window]:
        """Get a readonly data view of the windows contained in the entry."""
        pass


class Window(ABC):
    @abstractmethod
    def get_path(self) -> str:
        """Get the program path that owns the window."""
        pass

    @abstractmethod
    def get_title(self) -> str:
        """Get the title of the window."""
        pass

    @abstractmethod
    def get_is_active(self) -> bool:
        """Find out if the user is currently active on the window."""
        pass


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
