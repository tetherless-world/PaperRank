from .citation.ncbi_citation import NCBICitation as Citation

from collections import OrderedDict
from redis.client import StrictPipeline


def worker(pipe: StrictPipeline, linkset: OrderedDict) -> StrictPipeline:
    """Worker function. Queues actions in the `StrictPipeline` object to add
    tuples to GRAPH, maps outbound citations in OUT, adds unseen IDs to EXPLORE
    and removes current ID from INSTANCE.
    
    Arguments:
        pipe {StrictPipeline} -- Pipeline for the database operations.
        linkset {OrderedDict} -- Raw response from the NCBI API.
    
    Returns:
        StrictPipeline -- Pipeline with queued operations.
    """

    # Create citation object
    citation = Citation(query_raw=linkset)

    if citation.error:
        # Escape, return unmodified pipe if there is an error
        return pipe
    
    # Adding to 'SEEN'
    pipe.sadd('SEEN', citation.id)

    # Building inbound and outbound tuples
    out_tuples = ['("{0}","{1}")'.format(citation.id, i)
                  for i in citation.outbound]
    in_tuples = ['("{0}","{1}")'.format(i, citation.id)
                 for i in citation.inbound]

    # Saving inbound, outbound lists and outbound degree (even if empty)
    pipe.hmset('OUT', {citation.id: citation.outbound})
    pipe.hmset('IN', {citation.id: citation.inbound})
    pipe.hmset('OUT_DEGREE', {citation.id: len(citation.outbound)})

    if (len(out_tuples) + len(in_tuples)) > 0:
        # Check if inbound or outbound citations exist

        # Adding tuples to `GRAPH`
        pipe.sadd('GRAPH', *in_tuples, *out_tuples)

        # Add all inbound and outbound IDs to EXPLORE
        pipe.sadd('EXPLORE',
                  *citation.inbound, *citation.outbound)
        # Store the difference of `EXPLORE`` and `SEEN` in `EXPLORE`
        # NOTE: Temporarily commented out, this takes too long
        # pipe.sdiffstore('EXPLORE', 'EXPLORE', 'SEEN')
    else:
        # No inbound or outbound citations; add to `DANGLING`
        pipe.sadd('DANGLING', citation.id)

    # Return pipe object with new instructions
    return pipe
