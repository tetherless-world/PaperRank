from .worker import worker
from ..util import config
from multiprocessing import Value, Lock
from collections import OrderedDict
from redis.client import StrictPipeline
from redis import ConnectionPool, StrictRedis
from requests import get
from xmltodict import parse
import logging


def Query(conn_pool: ConnectionPool, pmids: list, proc_count: Value,
          lock: Lock):
    
    logging.info('Spawned Query process with {0} PMIDs'.format(len(pmids)))

    # Temporary until redis-py multiprocessing is fixed
    if not conn_pool:
        conn_pool = ConnectionPool(
            host=config.redis['host'],
            port=config.redis['port'],
            db=config.redis['db']
        )

    db = StrictRedis(connection_pool=conn_pool)

    # Creating redis pipeline
    pipe = db.pipeline()

    # Building request parameters
    request_parameters = __buildRequestParams(pmids)

    # Making request
    r = get(url=config.ncbi_api['url'], params=request_parameters)

    # Check validity, handle appropriately
    if r.ok:
        pipe = __successfulRequestHandler(pipe=pipe,
                                          pmids=pmids,
                                          response_raw=r.text)
    else:
        pipe = __failedRequestHandler(pipe=pipe, pmids=pmids)

    # Execute database calls
    pipe.execute()  # Blocking

    # Acquire lock, decrement process counter, release lock
    lock.acquire()
    proc_count.value -= 1
    lock.release()


def __successfulRequestHandler(pipe: StrictPipeline,
                               pmids: list,
                               response_raw: str) -> StrictPipeline:
    # Parse XML
    response = parse(response_raw)

    # Parsing query results
    try:
        linkset_container = response['eLinkResult']['LinkSet']
    except KeyError:
        # Handle failed request
        pipe = __failedRequestHandler(pipe=pipe, pmids=pmids)
        return pipe
    
    if type(linkset_container) is list:
        # Multiple citations, queue operations for each ID
        for linkset in linkset_container:
            pipe = worker(pipe, linkset=linkset)
    else:
        # Single citation, list
        pipe = worker(pipe=pipe, linkset=linkset_container)
    
    return pipe


def __buildRequestParams(pmids: list) -> dict:
    """Function to build request parameter dictionary.
    
    Returns:
        dict -- Request parameters.
    """

    default_headers = {
        'dbfrom': 'pubmed',
        'linkname': 'pubmed_pubmed_citedin+pubmed_pubmed_refs',
        'tool': config.ncbi_api['tool'],
        'email': config.ncbi_api['email'],
        'api_key': config.ncbi_api['api_key'],
        'id': pmids
    }
    return default_headers


def __failedRequestHandler(pipe: StrictPipeline,
                           pmids: list) -> StrictPipeline:
    """Failed request handler. Removes the current PMIIDs from the list
    in 'INSTANCE', and adds the IDs back to 'EXPLORE' for retrying.
    
    Arguments:
        pipe {StrictPipeline} -- Pipeline for the database operations.
    
    Returns:
        StrictPipeline -- Pipeline with queued operations.
    """

    # Gracefully recover progress
    pipe.srem('INSTANCE', *pmids)
    pipe.sadd('EXPLORE', *pmids)

    logging.warn('Query failed for PMIDs {0}'.format(pmids))

    return pipe
