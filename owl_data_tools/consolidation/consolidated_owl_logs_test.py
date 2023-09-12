import pytest

from .test_utils import PATHS, TITLES, compare_entry, window_mock
from .consolidated_owl_logs import ConsolidatedOwlLogs
from ..types import Entry


def test_1():
    def create_mock_entries() -> list[Entry]:
        return [
            Entry(
                10010,
                windows_view=[
                    window_mock(0, True),
                    window_mock(1),
                    window_mock(2),
                ],
            ),
            Entry(10020, [], 70),
            Entry(
                10030,
                [
                    window_mock(1),
                    window_mock(2),
                    window_mock(3, True),
                ],
            ),
        ]

    col = ConsolidatedOwlLogs(create_mock_entries(), PATHS, TITLES)

    assert col.get_size() == 3
    assert col.get_time_range() == (10010, 10030)

    entries_view = col.get_entries_view(10010, 10030)
    entries_original = create_mock_entries()

    assert len(entries_view) == 3

    for i in range(0, len(entries_view)):
        assert compare_entry(entries_original[i], entries_view[i])

    assert not compare_entry(entries_original[0], entries_view[2])


def test_2_get_entries_view():
    def create_mock_entries() -> list[Entry]:
        return [
            Entry(10010),
            Entry(10020),
            Entry(10030),
            Entry(10031),
            Entry(10032),
            Entry(10040),
        ]

    entries_original = create_mock_entries()

    col = ConsolidatedOwlLogs(create_mock_entries(), PATHS, TITLES)

    #
    entries_view = col.get_entries_view(10008, 10009)
    assert len(entries_view) == 0

    #
    entries_view = col.get_entries_view(10010, 10010)
    assert len(entries_view) == 1
    assert compare_entry(entries_view[0], entries_original[0])

    #
    entries_view = col.get_entries_view(10031, 10040)
    entries_view_2 = col.get_entries_view(10031, 99999)
    assert len(entries_view) == 3
    assert len(entries_view_2) == 3

    for i in range(0, len(entries_view)):
        assert compare_entry(entries_original[i + 3], entries_view[i])
        assert compare_entry(entries_view[i], entries_view_2[i])

    entries_view = col.get_entries_view(10041, 10099)
    assert len(entries_view) == 0


def test_3_empty():
    col = ConsolidatedOwlLogs([], [], [])
    assert col.get_size() == 0
    assert len(col.get_entries_view(0, 99999)) == 0

    with pytest.raises(IndexError):
        col.get_time_range()
