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


def computeLocation(data: np.array, data_shifted: np.array,
                    shift: np.float=None) -> np.float:
    """Computes the location parameter, given data, shifted data, and the shift
    parameter. The location parameter is the value by which the data is shifted
    before being passed into the Gamma distribution function. It is set equal
    to the following (also equivalent to min(data) - shift):
    loc = min(shifted data) - abs(min(data)) - (2 * shift)
    
    Arguments:
        data {np.array} -- Original data.
        data_shifted {np.array} -- Shifted data.
    
    Keyword Arguments:
        shift {np.float} -- Shift constant added to the data to enforce
                            strit positivity  (default: {None}).
    
    Returns:
        np.float -- Location parameter for the Gamma distribution.
    """

    # If data and data_shifted are equal, location is 0
    if np.array_equal(data, data_shifted):
        return 0

    if not shift:
        shift = config.trust['gamma_shift_constant']
    
    # Compute and return location
    return np.min(data_shifted) - np.absolute(np.min(data)) \
        - (2 * shift_constant)
