import pytest

from .types import RangeView


class TestRangeView:
    def test_1(self):
        long_list = list(range(0, 10))
        dv = RangeView(3, 4, long_list)

        counter = 3
        for value in dv:
            assert value == counter
            counter += 1

        assert dv[0] == 3
        assert dv[3] == 6
        assert len(dv) == 4

        with pytest.raises(IndexError):
            dv[-1]
        with pytest.raises(IndexError):
            dv[4]

    def test_2_empty(self):
        long_list = list(range(0, 10))
        dv = RangeView(2, 0, long_list)

        assert len(dv) == 0

        with pytest.raises(IndexError):
            dv[0]
