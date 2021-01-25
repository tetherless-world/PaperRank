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
seen = []

for fileName in inputFiles:
    strippedFile = fileName.rstrip()
    print('Reading '+ strippedFile[:-3])

    data = []
    for obj in gzip.GzipFile(pathToData + strippedFile, 'r'):
        data.append(json.loads(obj.decode('utf-8')))

    #map each Citation id to an integer for Markov Matrix to work
    for x in data:
        id_map[i] = Citation(x).id
        rev_id_map[Citation(x).id] = i
        i = i + 1

    #setup inbound and outbound maps
    for x in data:
        inbounds = Citation(x).inbound
        outbounds = Citation(x).outbound
        int_inbound = set()
        int_outbound = set()
        if len(inbounds) != 0:
            for ins in inbounds:
                if not(ins in rev_id_map):
                    id_map[i] = ins
                    rev_id_map[ins] = i
                    i = i+1
                int_inbound.add(rev_id_map[ins])
        
        if len(outbounds) != 0:
            for out in inbounds:
                if not(out in rev_id_map):
                    id_map[i] = out
                    rev_id_map[out] = i
                    i = i+1
                int_outbound.add(rev_id_map[out])

        inbound_map[rev_id_map[Citation(x).id]] = int_inbound
        outbound_map[rev_id_map[Citation(x).id]] = int_outbound
        seen.append(rev_id_map[Citation(x).id])

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

    

    
    
