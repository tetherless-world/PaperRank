from redis import StrictRedis
import logging
import numpy as np


def buildIdList(r: StrictRedis, cutoff: int) -> np.array:
    # Isolating number of IDs to be extracted
    seen_count = r.scard('SEEN')

    logging.info('Initializing copy of {0} IDs from SEEN db'
                 .format(seen_count))
    
    # Extracting IDs, casting to numpy array for easier handling
    seen_raw = np.array(list(r.smembers('SEEN')), dtype=np.int)

    # Sorting (NOTE: This sorting heuristic is specific to PubMed IDs)
    # PubMedIDs are sequential. Reversing orders them from newest to oldest
    seen = np.sort(seen_raw)[::-1]

    logging.info('Successfully extracted and sorted {0} IDs from SEEN db'
                 .format(seen.size))
    
    if cutoff:
        logging.info('Cutoff set at {0}'.format(cutoff))
        # Reducing seen to match cutoff
        seen = seen[0:cutoff]
        logging.info('Reducing list list to {0} IDs from {1}'
                     .format(cutoff, seen_count))
    
    return seen

