import json
import gzip
import logging
from context import PaperRank
from PaperRank.update.citation.ncbi_citation import NCBICitation as Citation
import numpy as np
import sys
import pandas as pd
import csv


pathToData = './data/'
inputFiles = open(pathToData + sys.argv[1], 'r')

#setup variables and data structures to be used
id_map = {}
rev_id_map = {}
i = 0

inbound_map = {}
outbound_map = {}
seen_id = set()

for fileName in inputFiles:
    strippedFile = fileName.rstrip()
    print('Reading '+ strippedFile[:-3])

    for obj in gzip.GzipFile(pathToData + strippedFile, 'r'):
        x = json.loads(obj.decode('utf-8'))

        #create citation of loaded data
        cite = Citation(x)
        #print(cite.id)
        # or reconstitute it using hex(cite.id)[2:-1]
        cite.id = int(cite.id, 16)
        
        #map id to integer
        if cite.id in seen_id:
            continue
        seen_id.add(cite.id)
        
        #update inbound and outbound lists
        inbound_map[cite.id] = [int(x,16) for x in cite.inbound]
        outbound_map[cite.id] = [int(x,16) for x in cite.outbound]
        del cite
        del x
        del obj

# Setting up configuration
PaperRank.util.configSetup(override='base.json')
config = PaperRank.util.config

seen_id = np.array(list(seen_id))

# Creating manager
compute_engine = PaperRank.compute.Manager(r=outbound_map, r_in= inbound_map, seenset = seen_id)

# Run compute engine
output = compute_engine.start(export = True)

#write to csv file
#output_file = 'output.csv'
#pd.DataFrame.from_dict(data=output, orient='index').to_csv(output_file, header=False)

    

    
    
