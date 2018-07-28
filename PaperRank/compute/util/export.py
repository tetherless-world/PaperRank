from .helpers import logLoopProgress
from ...util import config
from redis import StrictRedis
import logging
import os
import pandas as pd
import numpy as np


class Export:
    def __init__(self, r: StrictRedis, paperrank: np.array, seen: np.array):
        """Initialization logic for the Export module.
        
        Arguments:
            r {StrictRedis} -- StrictRedis object for database operations.
            paperrank {np.array} -- PaperRanks to be exported.
            seen {np.array} -- List of IDs corresponding to the PaperRanks.
        """

        # Storing input parameters
        self.r = r
        self.paperrank = paperrank
        self.seen = seen
        self.N = self.seen.size

        # Parsing PaperRank
        self.__parsePaperRank()
    
    def toRedis(self):
        """Function to store the parsed PaperRanks in Redis.
        """

        # counter
        last_check = 0

        for i in range(self.N):
            # Isolating row of dataframe
            row = self.pr_parsed.iloc[i]

            # Extracting PubMed ID and corresponding PaperRank
            pmid = row['PubMed ID']
            pr = row['PaperRank']

            # Add to PaperRank redis database
            self.r.hmset('PaperRank', {pmid: pr})

            # Log progress
            last_check = logLoopProgress(i, last_check, self.N,
                                         'PaperRank redis insertion')
    
    def toCSV(self):
        """Function to write the PaperRank dataframe to a csv file.
        """

        output_file = 'output/' + config.compute['csv_file']

        logging.info('Writing PaperRanks to CSV file {0}'.format(output_file))
        
        if not os.path.exists('output'):
            os.makedirs('output')

        self.pr_parsed.to_csv(output_file, index=False)

    def __parsePaperRank(self):
        """Function to parse the PaperRank scores, and build a DataFrame
        with PubMed ID in one column, and PaperRank in another.
        """

        logging.info('Parsing PaperRank vector into a Pandas DataFrame')

        aggregate_data = np.column_stack((self.seen.astype(np.str),
                                         self.paperrank))

        pr_parsed = pd.DataFrame(aggregate_data)
        pr_parsed.columns = ['PubMed ID', 'PaperRank']
        
        logging.info('Created Pandas DataFrame with dimesions {0}'
                     .format(pr_parsed.shape))

        # Assign to class variable
        self.pr_parsed = pr_parsed
