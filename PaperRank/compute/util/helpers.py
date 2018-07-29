from ...util import config

import logging


def logLoopProgress(count: int, last_check: int, N: int,
                    name: str) -> int:
    """Function to log the progress of loops through the a of size N.
    
    Arguments:
        count {int} -- Current iteration count.
        last_check {int} -- Last time logging was done.
        N {int} -- Number of elements being iterated over.
        name {str} -- Name of the iteration to be used in log.
    
    Returns:
        int -- Updated last_check.
    """
    
    # Computing log increment
    log_increment = (N / 100) * config.compute['log_freq']

    # Check if the current count has exceeded the increment
    if (count - last_check) > log_increment:
        # Compute completed percentage, log
        percent_complete = count / N * 100

        # Converting to string with 1 decimal point
        percent_complete = ('%.1f' % percent_complete)

        # regulate percentage length (i'm anal)
        if len(percent_complete) < 4:
            percent_complete = ' ' + percent_complete

        logging.info('{0} iteration is {1}% complete'
                     .format(name, percent_complete))

        return count  # Return this to update last_check to current count

    # If increment has not passed, return same last_check
    return last_check
