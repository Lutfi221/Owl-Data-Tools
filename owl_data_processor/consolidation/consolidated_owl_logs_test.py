import pytest
from .consolidated_owl_logs import ConsolidatedOwlLogs
from ..types import Entry, Window


paths: list[str] = [
    "/program/0.exe",
    "/program/1.exe",
    "/program/2.exe",
    "/program/3.exe",
]
titles: list[str] = ["Zero", "One", "Two", "Three"]


def window_mock(i: int, active=False) -> Window:
    return Window(paths[i], titles[i], active)


def compare_entry(a: Entry, b: Entry) -> bool:
    if not (
        a.duration_since_last_input == b.duration_since_last_input
        and a.is_user_afk == b.is_user_afk
        and a.timestamp == b.timestamp
        and len(a.windows_view) == len(b.windows_view)
    ):
        return False

    for i in range(0, len(a.windows_view)):
        w_a = a.windows_view[i]
        w_b = b.windows_view[i]
        if not (
            w_a.is_active == w_b.is_active
            and w_a.path == w_b.path
            and w_a.title == w_b.title
        ):
            return False

    return True


def test_compare_entry():
    assert not compare_entry(
        Entry(10010, [window_mock(0, True)]), Entry(10010, [window_mock(0, False)])
    )


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
            Entry(10020, [], 70, True),
            Entry(
                10030,
                [
                    window_mock(1),
                    window_mock(2),
                    window_mock(3, True),
                ],
            ),
        ]

    col = ConsolidatedOwlLogs(create_mock_entries(), paths, titles)

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

    col = ConsolidatedOwlLogs(create_mock_entries(), paths, titles)

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
