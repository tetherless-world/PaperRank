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

    out_count = r.hlen('OUT')

    logging.info('Building out degree map for {0} IDs'.format(out_count))

    # Progress tracking
    count = 0
    last_check = 0

    # Iterating through every element
    for out in out_iterator:
        # Defining out degree
        out_degree = {
            out[0]: len(eval(out[1]))
        }
        # Add to database
        r.hmset('OUT_DEGREE', out_degree)
        # Increment count
        count += 1
        # Log every ~10%
        if (count - last_check) > (out_count / 10):
            last_check = count
            logging.info('Out degree map {0}% complete'.format(
                round(count / out_count, 3) * 10))

    logging.info('Finished building out degree map for {0} IDs'.format(
        r.hlen('OUT_DEGREE')))
