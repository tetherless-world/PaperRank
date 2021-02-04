import json
import gzip
import logging
from context import PaperRank
from PaperRank.update.citation.ncbi_citation import NCBICitation as Citation
import numpy as np
import sys
import pandas as pd
import csv


pathToData = './data/SemanticScholar/'
inputFiles = open(pathToData + sys.argv[1], 'r')

#setup variables and data structures to be used
id_map = {}
rev_id_map = {}
i = 0

inbound_map = {}
outbound_map = {}
seen_id = set()
seen = []

for fileName in inputFiles:
    strippedFile = fileName.rstrip()
    print('Reading '+ strippedFile[:-3])

    for obj in gzip.GzipFile(pathToData + strippedFile, 'r'):
        x = json.loads(obj.decode('utf-8'))
        
        #create citation of loaded data
        cite = Citation(x)
        
        #map id to integer
        seen_id.add(cite.id)
        id_map[i] = cite.id
        rev_id_map[cite.id] = i
        i = i+1

        inbounds = cite.inbound
        outbounds = cite.outbound

        int_inbound = []
        int_outbound = []

        if len(inbounds) != 0:
            for ins in inbounds:
                if not(ins in seen_id):
                    seen_id.add(ins)
                    id_map[i] = ins
                    rev_id_map[ins] = i
                    i = i+1
                int_inbound.append(rev_id_map[ins])
        
        if len(outbounds) != 0:
            for out in inbounds:
                if not(out in seen_id):
                    seen_id.add(out)
                    id_map[i] = out
                    rev_id_map[out] = i
                    i = i+1
                int_outbound.append(rev_id_map[out])
        
        #update inbound and outbound lists
        inbound_map[rev_id_map[cite.id]] = int_inbound
        outbound_map[rev_id_map[cite.id]] = int_outbound
        seen.append(rev_id_map[cite.id])

# Setting up configuration
PaperRank.util.configSetup(override='base.json')
config = PaperRank.util.config

# Creating manager
compute_engine = PaperRank.compute.Manager(r=outbound_map, r_in= inbound_map, seenset = seen)

# Run compute engine
output = compute_engine.start(export = False)

idToVal = {}
for key in output:
    idToVal[id_map[key]] = output[key]

#write to csv file
output_file = './output/output.csv'
pd.DataFrame.from_dict(data=output, orient='index').to_csv(output_file, header=False)

    

    
    
