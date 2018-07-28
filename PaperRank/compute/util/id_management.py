from .helpers import logLoopProgress
from redis import StrictRedis
from scipy import sparse
import logging
import numpy as np


def buildIdList(r: StrictRedis, cutoff: int) -> np.array:
    """Function to build a list of IDs to be used by the compute module.
    
    Arguments:
        r {StrictRedis} -- StrictRedis object for database operations.
        cutoff {int} -- ID number limit.
    
    Returns:
        np.array -- Sorted list of IDs used by the compute module.
    """

    # Isolating number of IDs to be extracted
    seen_count = r.scard('SEEN')

    logging.info('Initializing copy of {0} IDs from SEEN'
                 .format(seen_count))
    
    # Extracting IDs, casting to numpy array for easier handling
    seen_raw = np.array(list(r.smembers('SEEN')), dtype=np.int)

    # Sorting (NOTE: This sorting heuristic is specific to PubMed IDs)
    # PubMedIDs are sequential. Reversing orders them from newest to oldest
    seen = np.sort(seen_raw)[::-1]

    logging.info('Successfully extracted and sorted {0} IDs from SEEN'
                 .format(seen.size))
    
    if cutoff:
        logging.info('Cutoff set at {0}'.format(cutoff))
        # Reducing seen to match cutoff
        seen = seen[0:cutoff]
        logging.info('Reducing list list to {0} IDs from {1}'
                     .format(cutoff, seen_count))

    return seen


def buildReverseIdxMap(seen: np.array) -> sparse.dok_matrix:
    """Function to build a reverse map, creating a mapping from the ID of a
    paper to its index in the seen array. This provides O(1) index lookup
    for any given ID.
    
    NOTE: Due to the fact that sparse arrays define unassigned values to be 0,
          we have incremented every index by +1, to use 0 as a flag. Because of
          this, -1 must be added before using these values.
    
    Arguments:
        seen {np.array} -- Array of IDs for which reverse map is computed.
    
    Returns:
        sparse.dok_matrix -- ID -> Index mapping with O(1) lookup.
    """

    # Isolating number of IDs
    N = seen.size

    logging.info('Instatiating reverse ID map for {0} IDs'.format(N))
    
    # NOTE: This creation heuristic is specific to PubMed IDs sequential nature
    max_id = np.amax(seen)

    # Defining matrix dimensions
    matrix_dim = (max_id + 1, 1)  # max_id +1 is because IDs start at 1, not 0

    # Instatiating sparse.dok_matrix column vector
    id_idx_map = sparse.dok_matrix((max_id + 1, 1), dtype=np.int)

    # counter
    last_check = 0

    # Building ID -> Index map to allow O(1) lookup
    for i in range(N):
        # i + 1 is so we can use 0 as a indicator for being empty
        # sparse.dok_matrix elements are 0 if not explicitly defined
        # When using this value, always subtract 1 first
        id_idx_map[seen[i], 0] = i + 1
    
        # Log progress
        last_check = logLoopProgress(i, last_check, N, 'Reverse ID map')

    logging.info('Instantiated reverse ID map with {0} elements'
                 .format(id_idx_map.nnz))

    return id_idx_map


def getSeenIndex(id_idx_map: sparse.dok_matrix, candidate_id: str) -> int:
    """Function to get the seen array index for a given ID in O(1).
    
    Arguments:
        id_idx_map {sparse.dok_matrix} -- ID -> Index map with O(1) lookup.
        candidate_id {str} -- Candidate ID to be searched.
    
    Raises:
        IndexError -- Raised when the ID is not found.
    
    Returns:
        int -- Corresponding index of the ID.
    """

    # Get index from map
    idx = id_idx_map[np.int(candidate_id), 0]   # Will raise IndexError

    # If empty pointer, raise exception
    if idx == 0:
        raise IndexError
    
    # Return idx - 1 because we added 1 at initialization
    return idx - 1
