class OwlError(Exception):
    """Base class for owl data processor exceptions."""

    _msg: str

    def __init__(self, msg=""):
        self._msg = msg

    def __str__(self):
        return repr(self._msg)
