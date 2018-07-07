from .worker import Worker
from ..util import config, Database
from .citation.ncbi_citation import NCBICitation as Citation
from collections import OrderedDict
from multiprocessing import Process
from requests import get
from xmltodict import parse
import logging


class Query:
    def __init__(self, db: Database, pmids: list):
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

        if type(linkset_container) is list:
            # Multiple citations, spawn workers for each
            [self.__spawnWorker(linkset=i) for i in linkset_container]
        else:
            # Single citation
            self.__spawnWorker(linkset=linkset_container)

    def __spawnWorker(self, linkset: OrderedDict):
        """Function to create a Citation object and spawn a Worker thread.
        
        Arguments:
            linkset {OrderedDict} -- Raw response from the NCBI API.
        """

        # Create citation object
        citation = Citation(query_raw=linkset)
        # Spawn worker, start thread
        t = Process(target=Worker, kwargs={
            'db': self.db,
            'citation': citation
        })
        t.start()

    def __failedRequestHandler(self):
        """Function to handle a failed request.
        """

        # Add failed PubMed IDs to log database
        db.addMultiple(database='L', data=self.pmids)
        # Logging warning
        logging.warning('Request failed for {0}'.format(self.pmids))
