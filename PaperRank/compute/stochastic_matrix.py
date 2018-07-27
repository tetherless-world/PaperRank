from redis import StrictRedis
from scipy import sparse
import numpy as np
import logging


def constructStochasticMatrix(r: StrictRedis, seen: np.array) \
        -> sparse.csr_matrix:
    """Function to construct the Stochastic matrix for the PaperRank
    computation function. This function ensures that the columns of the
    matrix are column stochastic (with the exception of 0 columns).
    
    Arguments:
        r {StrictRedis} -- StrictRedis object for database operations.
        seen {np.array} -- Array of IDs to be iterated over.

    Returns:
        scipy.sparse.csr_matrix -- Stochastic matrix for citation graph.
    """

    N = seen.size
    log_increment_percent = 0.1
    log_increment = (N / 100) * log_increment_percent

    logging.info('Constructing stochastic matrix for {0} IDs'.format(N))

    # Creating stochastic matrix
    m = sparse.dok_matrix((N, N), dtype=np.float32)

    # Creating sparse matrix to hold mappings from IDs to indexes
    logging.info('Instantiating id_idx_map for {0} IDs'.format(N))
    max_id = np.amax(seen)
    id_idx_map = sparse.dok_matrix((max_id + 1, 1), dtype=np.int)
    # Building ID -> Index map to allow O(1) lookup in loop
    for i in range(N):
        id_idx_map[seen[i], 0] = i + 1  # Note: +1 is to flag empty pointers
    logging.info('Instantiated id_idx_map with {0} elements'
                 .format(id_idx_map.nnz))

    # counters
    last_check = 0

    logging.info('Beginning to build stochastic matrix')

    # Iterating over all of the IDs
    for i in range(N):
        # Isolate current ID
        paper_id = str(seen[i])

        # Getting inbound citations
        inbound_list = eval(r.hget('IN', paper_id))

        # Iterate through inbound citations
        for inbound in inbound_list:
            # Compute position in matrix (if exists)
            try:
                j = __getIdIndex(id_idx_map, inbound)
            except IndexError:
                # If the ID is not in seen, log and skip it
                logging.warn('Inbound citation {0} for paper {1} not indexed'
                             .format(inbound, paper_id))
                continue
            # Get out degree
            d = float(r.hget('OUT_DEGREE', inbound).decode('utf-8'))
            d = 1.0 if d == 0.0 else d  # Change 0 to 1 to avoid division by 0
            m[i, j] = 1 / d
        
        # Log progress
        last_check = __logProgress(N, log_increment, i,
                                   last_check, 'Build stochastic matrix')
    
    logging.info('Built unverified stochastic matrix with {0} elements'
                 .format(m.nnz))

    # Converting to compressed sparse column matrix
    m = m.tocsc()

    # Ensure column stochasticity (i.e. columns sum to 1, or 0)
    # See: https://bit.ly/2vdLqdM

    # counters
    last_check = 0

    logging.info('Beginning verification of stochastic matrix')

    # Iterate through columns
    for j in range(N):
        # Isolate column, compute magnitude
        col = m.getcol(j)
        magnitude = np.sum(col.data)

        # Change if magnitude less than 1, but not if 0
        if (magnitude < 1) and (magnitude != 0):
            count = col.nnz
            new_data = np.repeat((1 / count), count)
            col.data = new_data
            m[:, j] = col
        
        # Log progress
        last_check = __logProgress(N, log_increment, j,
                                   last_check, 'Column stochasticity')

    logging.info('Built verified stochastic matrix with {0} elements'
                 .format(m.nnz))

    # Casting to compressed sparse row matrix for
    # fast matrix vector multiplication
    m = m.tocsr()

    return m


def __getIdIndex(id_idx_map: sparse.dok_matrix, candidate_id: int) -> int:
    """Function to get the seen array index for a given ID in O(1).
    
    Arguments:
        id_idx_map {sparse.dok_matrix} -- ID -> Index mappings.
        candidate_id {int} -- Candidate ID to be searched.
    
    Raises:
        IndexError -- Raised when the ID is not found.
    
    Returns:
        int -- Corresponding index of the ID.
    """

    # Get index from map
    idx = id_idx_map[np.int(candidate_id), 0]  # Will raise IndexError

    # Empty pointer, raise exception
    if idx == 0:
        raise IndexError

    # Return idx - 1 because we added one at initialization
    return idx - 1


def __logProgress(N: int, log_increment: float, count: int, last_check: int,
                  iteration_name: str) -> int:
    """Function to log the progress of the constructStochasticMatrix function.
    
    Arguments:
        N {int} -- Total number of elements.
        log_increment {float} -- Increment at which logging is done.
        count {int} -- Current iteration count
        last_check {int} -- Last time logging was done.
        iteration_name {str} -- Name of the iteration to be used in log.
    
    Returns:
        int -- Updated last_check
    """

    if (count - last_check) > log_increment:
        percent_complete = round(count / N, 3) * 100
        logging.info('{0} iteration is {1}% complete'.format(
            iteration_name, percent_complete))
        return count
    return last_check
