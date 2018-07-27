from ...util import config
from redis import StrictRedis
import numpy as np


def computeIterationScore(r: StrictRedis, id_list: np.array) -> np.array:
    """Function to compute and returnthe iteration PaperRank for a
    given list of IDs.
    
    Arguments:
        r {StrictRedis} -- StrictRedis object for database operations.
        id_list {np.array} -- List of IDs for PaperRank computation.
    
    Returns:
        np.array -- Array of scores, with position corresponding to
                    function input parameter id_list.
    """

    # Getting function variables
    N = id_list.size
    beta = config.compute['beta']

    scores = np.array([], dtype=float)

    # Iterate through IDs
    for paper_id in id_list:
        score = 0
        inbound_list = eval(r.hget('IN', paper_id))

        # Iterate through inbound citations
        for inbound in inbound_list:
            # Check if paperrank exists for inbound ID
            if r.hexists('PaperRank', inbound):
                # Getting PaperRank in outbound degree of inbound
                inbound_pr = float(r.hget('PaperRank', inbound))
                inbound_outdeg = float(r.hget('OUT_DEGREE', inbound))
                # Add to score
                score += (beta * (inbound_pr / inbound_outdeg))
            else:
                logging.warn('No PaperRank for {0} inbound ID {1}. Skipping...'
                             .format(paper_id, inbound))
        # Save score to database
        r.hmset('PaperRank', {paper_id: score})

        # Append score to score list
        scores = np.append(scores, score)
    
    # Redistribute leaked PaperRanks (from dangling papers)
    
    leaked_pr = 1 - np.sum(scores)

    if leaked_pr > 0:
        scores = scores + (leaked_pr / N)
    
    return scores
