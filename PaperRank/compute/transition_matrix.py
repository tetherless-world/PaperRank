from .util import buildReverseIdxMap, getSeenIndex, logLoopProgress

from scipy import sparse
import numpy as np
import logging


class MarkovTransitionMatrix:
    def __init__(self, r_out: map, r_in: map, seen: np.array,
                 id_idx_map: sparse.dok_matrix):
        """Initialization logic for the MarkovTransitionMatrix submodule.
        
        Arguments:
            r {StrictRedis} -- StrictRedis object for database operations.
            seen {np.array} -- Array of IDs to be iterated over.
            id_idx_map {sparse.dok_matrix} -- ID -> Index map with O(1) lookup.
        """

        # Storing input parameters
        self.r_out = r_out
        self.r_in = r_in
        self.seen = seen
        self.N = self.seen.size
        self.id_idx_map = id_idx_map

    def construct(self) -> sparse.csr_matrix:
        """Function to construct the Markov matrix for the PaperRank
        computation function. This function ensures that the columns of the
        matrix are column stochastic (with the exception of 0 columns).

        Returns:
            scipy.sparse.csr_matrix -- Stochastic matrix for citation graph.
        """
        # Creating transition matrix
        logging.info('Initializing {0}x{0} transition matrix'.format(self.N))
        M = sparse.dok_matrix((self.N, self.N), dtype=np.float)

        # Computing unadjusted transition matrix
        M = self.__buildUnadjustedMatrix(M)

        # Casting to sparse.csc_matrix (compressed sparse column matrix)
        # for increased efficiency of column operations
        M = M.tocsc()

        # Adjusting transition matrix
        M = self.__adjustTransitionMatrix(M)

        # Casting to sparse.csr_matrix (compressed sparse row matrix)
        # for increased efficiency of matrix/vector products
        M = M.tocsr()

        return M

    def __buildUnadjustedMatrix(self, M: sparse.dok_matrix) \
            -> sparse.dok_matrix:
        """Function to build the unadjusted transition matrix. That is, it
        builds a transition matrix but does not guarantee that it is
        column stochastic.
        
        Returns:
            sparse.dok_matrix -- Unadjusted Markov transition matrix.
        """

        logging.info('Building unadjusted transition matrix')

        # counter
        last_check = 0

        for i in range(self.N):
            # Isolate current ID
            paper_id = self.seen[i]

            #print(self.r_in)

            # Getting inbound citations
            inbound_list = eval(str(self.r_in[paper_id]))

            # Iterate throug inbound citations
            for inbound in inbound_list:
                # Compute position in matrix (if exists)
                try:
                    j = getSeenIndex(self.id_idx_map, inbound)
                except IndexError:
                    # If the ID is not seen, log and skip it
                    logging.warn('Inbound citation {0} for paper {1} not \
                        indexed'.format(inbound, paper_id))
                    continue
                #print(self.r_out)
                # Get out degree
                d = float(len(self.r_out[inbound]))
                # Set d = 1 if out degree is 0, to avoid division by 0
                d = 1.0 if d == 0.0 else d
                
                # Set value in transition matrix
                M[i, j] = 1 / d
            
            # Log progress
            last_check = logLoopProgress(i, last_check, self.N,
                                         'Unadjusted transition matrix')

        logging.info('Built unadjusted Markov transition matrix with {0} \
            elements'.format(M.nnz))
        
        return M
    
    def __adjustTransitionMatrix(self, M: sparse.csc_matrix) \
            -> sparse.csc_matrix:
        """Function to compute the adjusted Markov transition matrix, given the
        unadjusted matrix. This method enforces column stochastic behavior.
        
        Returns:
            sparse.csc_matrix -- Adjusted Markov transition matrix.
        """

        logging.info('Building adjusted transition matrix')

        # counter
        last_check = 0

        logging.info('Computing sum of columns of M')
        magnitues = M.sum(axis=0)

        logging.info('Iterating through each column, rebalancing')

        # Iterate through each column
        for i in range(self.N):
            # Isolating magnitude
            magnitude = magnitues[0, i]

            # If criteria are satisfied, redistribute probabilities
            if (magnitude < 1.0) and (magnitude != 0):
                count = M[:, i].nnz

                # Isolate nonzero indezes
                nonzero_idx = M[:, i].nonzero()[0]

                # Update indexes with balanced probabilities
                for idx in nonzero_idx:
                    M[idx, i] = 1 / count
        
            # Log progress
            last_check = logLoopProgress(i, last_check, self.N,
                                         'Stable transition matrix')
        
        logging.info('Built adjusted Markov transition matrix with {0} \
            elements'.format(M.nnz))
        
        return M
