"""Commonly used data structures
"""

from typing import Generic, Optional, TypeVar, TypedDict
from abc import ABC, abstractmethod

T = TypeVar("T")


class DataView(Generic[T], ABC):
    def __getitem__(self, index: int) -> T:
        pass

    def __len__(self) -> int:
        pass


class Entry(ABC):
    @abstractmethod
    def get_timestamp(self) -> str:
        pass

    @abstractmethod
    def get_is_user_afk(self) -> bool:
        pass

    @abstractmethod
    def get_duration_since_last_input(self) -> int:
        pass

    @abstractmethod
    def get_is_active(self) -> str:
        pass

    @abstractmethod
    def get_windows_view(self) -> str:
        pass


class Window(ABC):
    @abstractmethod
    def get_path(self) -> str:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def get_is_active(self) -> bool:
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
    """Describes the state of a PC at a point of time."""

    timestamp: int
    """The time when the entry was recorded.
    """

    windows: Optional[list[WindowData]]
    """List of windows that are opened.
    """

    durationSinceLastUserInput: Optional[int]
    """Duration (in seconds) since the last user input.
    """
