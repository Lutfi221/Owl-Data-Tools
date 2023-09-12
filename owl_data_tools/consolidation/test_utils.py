from ..types import Entry, Window


PATHS: list[str] = [
    "/program/0.exe",
    "/program/1.exe",
    "/program/2.exe",
    "/program/3.exe",
]
TITLES: list[str] = ["Zero", "One", "Two", "Three"]


def window_mock(i: int, active=False) -> Window:
    return Window(PATHS[i], TITLES[i], active)


def compare_entry(a: Entry, b: Entry) -> bool:
    if not (
        a.duration_since_last_input == b.duration_since_last_input
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
