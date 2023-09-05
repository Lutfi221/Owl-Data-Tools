from typing import Callable, Generator, Sequence

from .types import T


def find(elements: Sequence[T], key: Callable[[T], bool]) -> Generator[T, None, None]:
    return (elem for elem in elements if key(elem))


def find_first(elements: Sequence[T], key: Callable[[T], bool]) -> T | None:
    return next(find(elements, key), None)
