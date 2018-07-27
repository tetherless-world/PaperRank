from redis import StrictRedis
import logging


def buildOutDegreeMap(r: StrictRedis):
    """Function to build the out degree map for the citations in the 'OUT'
    database in Redis.
    
    Arguments:
        r {StrictRedis} -- StrictRedis object for database operations.
    """

    # Getting iterator for 'OUT'
    out_iterator = r.hscan_iter('OUT')

    # Iterating through every element
    for out in out_iterator:
        # Defining out degree
        out_degree = {
            out[0]: len(eval(out[1]))
        }
        # Add to database
        r.hmset('OUT_DEGREE', out_degree)
