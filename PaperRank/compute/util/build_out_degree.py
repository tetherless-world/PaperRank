from .helpers import logLoopProgress
from redis import StrictRedis
import logging
import numpy as np


def buildOutDegreeMap(r: StrictRedis):
    """Function to build the out degree map for the citations in the 'OUT'
    database in Redis.
    
    Arguments:
        r {StrictRedis} -- StrictRedis object for database operations.
    """

    # Check if out degree map refresh is necessary, if not return
    if r.hlen('OUT') == r.hlen('OUT_DEGREE'):
        logging.info('No difference found between OUT and OUT_DEGREE')
        return

    logging.info('Difference found between OUT and OUT_DEGREE, building map')

    logging.info('Copying OUT and OUT_DEGREE keys for comparison')

    # Get list of elements in OUT and OUT_DEGREE
    out_list = [i.decode('utf-8') for i in r.hkeys('OUT')]
    outdeg_list = [i.decode('utf-8') for i in r.hkeys('OUT_DEGREE')]

    # Isolate elements that do not have OUT_DEGREE
    missing = np.setdiff1d(out_list, outdeg_list)
    missing_count = missing.size

    logging.info('Building out degree map for {0} IDs'.format(missing_count))

    # Progress tracking
    count = 0
    last_check = 0

    # Iterating through every element
    for missing_id in missing:
        # Defining out degree
        out_degree = {
            missing_id: len(eval(r.hget('OUT', missing_id)))
        }
        # Add to database
        r.hmset('OUT_DEGREE', out_degree)
        # Increment count
        count += 1
        # Log every increment
        last_check = logLoopProgress(count, last_check, missing_count,
                                     'Outbound citation map')

    logging.info('Finished building out degree map for {0} IDs'.format(
        r.hlen('OUT_DEGREE')))
