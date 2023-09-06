from typing import Optional, Sequence


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

    def __init__(self, values: Optional[Sequence[str]] = None):
        """Constructs :class:`Dictionary`"""
        self._dict = {}
        if values:
            for value in values:
                self._dict[value] = self._size
                self._size += 1

    def use_value(self, value: str) -> int:
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

    @property
    def size(self) -> int:
        """Number of values in the dictionary."""
        return self._size


class DictionaryMapper:
    """Class to map the indexes of a dictionary to another dictionary.
    Useful when combining multiple dictionaries into one.
    """

    _source_values: Sequence[str]
    _target_dict: Dictionary
    _source_to_target: list[Optional[int]]

    def __init__(
        self, source_dictionary_values: Sequence[str], target_dictionary: Dictionary
    ):
        """
        Parameters
        ----------
        source_dictionary_values : Sequence[str]
            List of values of the source dictionary.
        target_dictionary : Dictionary
            Target dictionary.
        """
        self._source_values = source_dictionary_values
        self._target_dict = target_dictionary

        self._source_to_target = [None] * len(self._source_values)

    def source_to_target(self, i_source: int) -> int:
        """Maps the index for the source dictionary to the target dictionary.

        Parameters
        ----------
        i_source : int
            Index for the value in the source dictionary.

        Returns
        -------
        int
            Index for the value in the target dictionary.
        """
        if self._source_to_target[i_source] != None:
            return self._source_to_target[i_source]  # type: ignore

        self._source_to_target[i_source] = self._target_dict.use_value(
            self._source_values[i_source]
        )
        return self._source_to_target[i_source]  # type: ignore
