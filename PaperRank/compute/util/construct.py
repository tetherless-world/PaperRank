from redis import StrictRedis
from scipy import sparse
import numpy as np
import logging


def constructStochasticMatrix(r: StrictRedis, seen_sorted: np.array) \
        -> sparse.dok_matrix:

    N = seen_sorted.size

    # Creating stochastic matrix
    m = sparse.dok_matrix((N, N), dtype=np.float32)

    for i in range(N):
        paper_id = seen_sorted[i]
        inbound_list = eval(r.hget('IN', paper_id))
        for inbound in inbound_list:
            j = np.where(seen_sorted == inbound)[0][0]
            d = float(r.hget('OUT_DEGREE', inbound).decode('utf-8'))
            if d == 0.0:
                d = 1.0
            m[i, j] = 1 / d

    # Converting to compressed sparse column matrix
    m = m.tocsc()

    # Ensure column stochasticity (i.e. columns sum to 1, or 0)
    # See: https://bit.ly/2vdLqdM
    
    for j in range(N):
        col = m.getcol(j)
        magnitude = sum(col)
        if (magnitude < 1) and (magnitude != 0):
            count = col.count_nonzero()
            new_data = np.repeat((1 / count), count)
            col.data = new_data
            m[:, j] = col

    # Casting to compressed sparse row matrix for
    # fast matrix vector multiplication
    m = m.tocsr()

    return m
