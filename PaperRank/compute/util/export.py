from .helpers import logLoopProgress
from ...util import config

from functools import wraps
from redis import StrictRedis
from scipy import sparse
import logging
import os
import pandas as pd
import numpy as np


class _Decorators:
    @classmethod
    def checkFolder(cls, decorated):
        """Decorator to verify that the output folder exists, and to create
        it if it does not.
        """

        @wraps(decorated)
        def wrapper(*args, **kwargs):
            if not os.path.exists(config.compute['output_folder']):
                os.makedirs(config.compute['output_folder'])
            return decorated(*args, **kwargs)
        return wrapper


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
    
    @_Decorators.checkFolder
    def toCSV(self):
        """Function to write the PaperRank dataframe to a csv file.
        """

        output_file = config.compute['output_folder'] + \
            config.compute['csv_file']

        logging.info('Writing PaperRanks to CSV file {0}'.format(output_file))

        self.pr_parsed.to_csv(output_file, index=False)
    
    @_Decorators.checkFolder
    def toExcel(self):
        """Function to write the PaperRank dataframe to a Microsoft Excel file.
        """

        output_file = config.compute['output_folder'] + \
            config.compute['excel_file']

        logging.info('Writing PaperRanks to Excel file {0}'
                     .format(output_file))

        # Check if folder exists, create if not
        if not os.path.exists('output'):
            os.makedirs('output')

        self.pr_parsed.to_excel(output_file, index=False)

    @_Decorators.checkFolder
    def toSerialized(self, transition_matrix: sparse.csr_matrix):
        """Function to write the PaperRank dataframe and the transition
        matrix (M) to pickle files.
        """

        pr_output_file = config.compute['output_folder'] + \
            config.compute['pickle_pr_file']
        m_output_file = config.compute['output_folder'] + \
            config.compute['pickle_m_file']

        logging.info('Writing PaperRank and Transition Matrix to pickle \
            {0} and {1}.'.format(pr_output_file, m_output_file))

        self.pr_parsed.to_pickle(pr_output_file)
        sparse.save_npz(m_output_file, transition_matrix)

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
