# In order to run the test of this library, just execute ">>> python ./utils.py" in a command shell

import operator
from functools import reduce
from numpy import cumsum, array


def conjunction(lst):
    """ Returns the conjunction of several boolean vectors
        >>> a = array([True, False, True])
        >>> b = array([True, True, False])
        >>> conjunction([a,b])
        array([ True, False, False], dtype=bool)
    """
    return reduce(operator.and_, lst)


def get_first_percent(lst, percentage):
    """ Returns the smallest index of elements that contain as much as some percentage of lst's weight.
        >>> get_first_percent([4,3,1,5,2], 0.5)
        1
        >>> get_first_percent([4,3,1,5,2], 1)
        4
        >>> get_first_percent([4,3,1,5,2], 0)
        0
    """
    lst = array(sorted(lst, reverse=True))
    cum_lst = cumsum(lst/lst.sum())
    if not 0 <= percentage <= 1:
        raise ValueError("Invalid Percentage")
    index = next(idx for idx, value in enumerate(cum_lst) if value >= percentage)
    return index


if __name__ == "__main__":
    import doctest
    doctest.testmod()
