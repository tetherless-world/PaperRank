from .....util import config

import numpy as np


def shiftData(data: np.array, shift: np.float=None) -> np.array:
    """Function to shift a set of data < 1 to be strictly positive. This is
    done by adding the absolute value of the minimum of the data to the entire
    dataset, and by adding an additional shift (set in configuration) to enfore
    strict positivity.
    Expressed mathematically; data + abs(min(data)) + shift.
    
    Arguments:
        data {np.array} -- Data to be shifted.
    
    Keyword Arguments:
        shift {np.float} -- Shift constant to be added to the data to enforce
                            strict positivity (default: {None}).
    
    Returns:
        np.array -- Shifted data.
    """

    if not shift:
        shift = config.trust['gamma_shift_constant']

    return data + np.absolute(np.min(data)) + shift
