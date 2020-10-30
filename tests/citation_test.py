import json
import gzip
from context import PaperRank
from PaperRank.update.citation.ncbi_citation import NCBICitation as Citation
import redis
import numpy as np

#Test to see if the modification to ncbi_citation.py works
data = []
for obj in gzip.GzipFile('/mnt/c/Users/huangv3/Documents/Research/PaperRank/data/sample-S2-records.gz', 'r'):
    data.append(json.loads(obj.decode('utf-8')))

# Setting up configuration
PaperRank.util.configSetup(override='base.json')
config = PaperRank.util.config

# Creating redis-py connection
r = redis.StrictRedis(
    host=config.redis['host'],
    port=config.redis['port'],
    db=config.redis['db']
)

#map each Citation id to an integer
id_map = {}
rev_id_map = {}
i = 0
for x in data:
    id_map[i] = Citation(x).id
    rev_id_map[Citation(x).id] = i
    i = i + 1

#setup inbound and outbound maps
inbound_map = {}
outbound_map = {}
seen = []
for x in data:
    inbounds = Citation(x).inbound
    outbounds = Citation(x).outbound
    int_inbound = []
    int_outbound = []
    if len(inbounds) != 0:
        for ins in inbounds:
            if not(ins in rev_id_map):
                id_map[i] = ins
                rev_id_map[ins] = i
                i = i+1
            int_inbound.append(rev_id_map[ins])
    
    if len(outbounds) != 0:
        for out in inbounds:
            if not(out in rev_id_map):
                id_map[i] = out
                rev_id_map[out] = i
                i = i+1
            int_outbound.append(rev_id_map[out])

    inbound_map[rev_id_map[Citation(x).id]] = int_inbound
    outbound_map[rev_id_map[Citation(x).id]] = int_outbound
    seen.append(rev_id_map[Citation(x).id])


# #setup inbound and outbound maps
# inbound_map = {}
# outbound_map = {}
# seen = []
# for x in data:
#     inbound_map[i] = Citation(x).inbound
#     outbound_map[i] = Citation(x).outbound
#     seen.append(i)
#     i = i+1
#     # inbound_map[Citation(x).id] = Citation(x).inbound
#     # outbound_map[Citation(x).id] = Citation(x).outbound
#     # seen.append(Citation(x).id)

# Flush db
r.flushdb()
r.hmset('IN', inbound_map)
r.hmset('OUT', outbound_map)
r.sadd('SEEN', *seen)


# Running util to set up out degree map
PaperRank.compute.util.buildOutDegreeMap(r=r)

# Creating manager
compute_engine = PaperRank.compute.Manager(r=r)

# Run compute engine
compute_engine.start()

