from typing import Optional


class Dictionary:
    """A wrapper of a dictionary intended to store values and
    their index. This class is used to reduce redundant data
    being stored in memory/file.

    It provides a :meth:`use_value` method that takes a value
    as input, and returns a unique number representing it.

    In order to get the value represented by a number, you will
    need to get the list of values in the dictionary by calling
    :meth:`generate_values_list`, and using the unique number
    as index for the list. See the examples below for more
    clarity.

    Examples
    --------
    >>> limb_dict = ConsolidatorDictionary()
    >>> limbs = []
    >>> limbs.append(limb_dict.use_value("head"))
    >>> limbs.append(limb_dict.use_value("arm"))
    >>> limbs.append(limb_dict.use_value("arm"))
    >>> limbs.append(limb_dict.use_value("leg"))
    >>> limbs.append(limb_dict.use_value("leg"))
    >>> print(limbs)
    [0, 1, 1, 2, 2]
    >>> limbs_list = limb_dict.generate_values_list()
    >>> print(limb_list[limbs[2]])
    arm
    """

    _dict: dict[str, int]
    _size = 0

    def __init__(self):
        """Constructs :class:`Dictionary`"""
        self._dict = {}

    def use_value(self, value: Optional[str]) -> int:
        """Gets or creates the unique dictionary index
        for `value`.

        Parameters
        ----------
        value : str
            Value to be referenced from the dictionary.

        Returns
        -------
        int
            The dictionary index for `value`
        """
        if value == None:
            value = ""

        if value in self._dict:
            return self._dict[value]

        self._dict[value] = self._size
        self._size += 1

        return self._dict[value]

    def generate_values_list(self) -> list[str]:
        """Generates a list of values that has been used.

        Returns
        -------
        list[str]
            List of values
        """
        values = [""] * self._size
        for value, index in self._dict.items():
            values[index] = value

        return values
