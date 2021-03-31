from .paperrank import StablePaperRank
from .util import buildOutDegreeMap, buildIdList, buildReverseIdxMap, Export
from .transition_matrix import MarkovTransitionMatrix
from ..util import config

import logging
import numpy as np


class Manager: #build r from fileIndex
    def __init__(self, r: map, r_in: map, seenset: set, cutoff: int=None):
        """Manager class initialization. Loads configuration variables,
        and recovers gracefully from a crash by default.
        
        Arguments:
            r {StrictRedis} -- StrictRedis object for database operations.
        
        Keyword Arguments:
            cutoff {int} -- ID number limit. (default: {None})
        """

        # Class variables
        self.r = r
        self.r_in = r_in

        # Intializing SEEN ID list
        print('Initializing with {0} IDs in SEEN'
                .format(seenset.size))
        #self.seen = buildIdList(seenset, cutoff=cutoff)
        self.seen = seenset
        self.N = self.seen.size
        

        # # Building out degree map
        # logging.info('Building out degree map')
        # buildOutDegreeMap(r=self.r)

        # Building reverse index map for O(1) index lookup
        #print('Buidling reverse index map')
        #self.id_idx_map = buildReverseIdxMap(seen=self.seen)

        # Logging frequency configuration
        self.log_increment = (self.N / 100) * config.compute['log_freq']

    def start(self, export: bool=True):
        """Function to start the PaperRank computation.

        Keyword Arguments:
            export {bool} -- Toggle exporting paperrank. (default: {True})
        """

        # Startup
        print('Starting PaperRank computation for {0} IDs'
                     .format(self.N))

        markov_matrix = MarkovTransitionMatrix(r_out=self.r,
                                                r_in = self.r_in,
                                               seen=self.seen)
        
        M = markov_matrix.construct()

        # Initializing StablePaperRank objecti
        print('Creating stablepaperrank object')
        compute_engine = StablePaperRank(M, self.N)
        # Computing PaperRanks
        paperrank = compute_engine.calculate()

        print('Computed PaperRanks for {0} IDs'.format(self.N))
    
        #{test_keys[i]: test_values[i] for i in range(len(test_keys))} 
        # If no export, return
        if not export:
            return dict(zip(self.seen, paperrank))

        # Initialize export manager
        export_manager = Export(r=self.r, paperrank=paperrank, seen=self.seen)
        
        # Export to Redis, CSV and Excel
        #export_manager.toRedis()
        export_manager.toCSV()
        #export_manager.toExcel()
        #export_manager.toSerialized(transition_matrix=M)

        return paperrank
