from ..util import config, Database
from .citation.ncbi_citation import NCBICitation as Citation
from collections import OrderedDict
from requests import get
from xmltodict import parse
import logging
import threading


class Query:
    def __init__(self, db: Database, pmids: list, suppress_worker: bool=False):
        """Query class initialization. Makes request and delegates worker
        threads with response data.
        
        Arguments:
            pmids {list} -- List of PubMed IDs to be queried.
            db {Database} -- Database to be used for data transactions.
        """

        self.db = db
        self.pmids = pmids

        # Building request parameters
        request_paramters = self.__buildRequestParams()
        # Making request
        r = get(url=config.ncbi_api['url'], params=request_paramters)
        if r.ok:
            self.__successfulRequestHandler(response_raw=r.text)
        else:
            self.__failedRequestHandler()

    def __buildRequestParams(self) -> dict:
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
            'id': self.pmids
        }
        return default_headers

    def __successfulRequestHandler(self, response_raw: str):
        """Function to handle a successful request response. This function
        spawns worker threads for each response item.
        
        Arguments:
            response_raw {str} -- Response raw text.
        """

        # Parse XML
        response = parse(response_raw)

        # Parsing query results
        try:
            linkset_container = response['eLinkResult']['LinkSet']
        except KeyError:
            self.__failedRequestHandler()

        while len(linkset_container) is not 0:
            linkset = linkset_container.pop()   # Removing next element
            # Creating citation object
            citation = Citation(db=self.db, query_raw=linkset)
            # TODO: Spawn worker thread here with citation_map as input

    def __failedRequestHandler(self):
        """Function to handle a failed request.
        """

        # Add failed PubMed IDs to log database
        db.addMultiple(database='L', data=self.pmids)
        # Logging warning
        logging.warn('Request failed for {0}'.format(self.pmids))
