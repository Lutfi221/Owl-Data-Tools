from .exceptions import OwlError


def test_str():
    e = OwlError("message")
    assert str(e) == repr("message")
