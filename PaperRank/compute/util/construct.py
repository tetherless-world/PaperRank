from redis import StrictRedis
from scipy import sparse
import numpy as np
import logging


def constructStochasticMatrix(r: StrictRedis, seen_sorted: np.array) \
        -> sparse.csr_matrix:
    """Function to construct the Stochastic matrix for the PaperRank
    computation function. This function ensures that the columns of the
    matrix are column stochastic (with the exception of 0 columns).
    
    Returns:
        scipy.sparse.csr_matrix -- Stochastic matrix for citation graph.
    """

    N = seen_sorted.size
    log_increment_percent = 0.1
    log_increment = (N / 100) * log_increment_percent

    # Creating stochastic matrix
    m = sparse.dok_matrix((N, N), dtype=np.float32)

    # counters
    last_check = 0

    # Iterating over all of the IDs
    for i in range(N):
        # Isolate current ID
        paper_id = seen_sorted[i]

        # Getting inbound citations
        inbound_list = eval(r.hget('IN', paper_id))
        # Iterate through inbound citations
        for inbound in inbound_list:
            # Compute position in matrix
            j = np.where(seen_sorted == inbound)[0][0]
            # Get out degree
            d = float(r.hget('OUT_DEGREE', inbound).decode('utf-8'))
            d = 1 if d == 0 else d  # Change 0 to 1 to avoid division by 0
            m[i, j] = 1 / d
        
        # Log progress
        last_check = __logProgress(N, log_increment, i,
                                   last_check, 'Build stochastic matrix')
    # Converting to compressed sparse column matrix
    m = m.tocsc()

    # Ensure column stochasticity (i.e. columns sum to 1, or 0)
    # See: https://bit.ly/2vdLqdM

    # counters
    last_check = 0

    # Iterate through columns
    for j in range(N):
        # Isolate column, compute magnitude
        col = m.getcol(j)
        magnitude = sum(col)

        # Change if magnitude less than 1, but not if 0
        if (magnitude < 1) and (magnitude != 0):
            count = col.count_nonzero()
            new_data = np.repeat((1 / count), count)
            col.data = new_data
            m[:, j] = col
        
        # Log progress
        last_check = __logProgress(N, log_increment, j,
                                   last_check, 'Column stochasticity')

    # Casting to compressed sparse row matrix for
    # fast matrix vector multiplication
    m = m.tocsr()

    return m


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
