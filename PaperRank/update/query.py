from ..util import config, Database
from requests import get
from xmltodict import parse
import json
import logging
import threading


class Query:
    def __init__(self, db: Database, pmids: list):
        """Query class initialization. Makes request and delegates worker
        threads with response data.
        
        Arguments:
            pmids {list} -- List of PubMed IDs to be queried.
            db {Database} -- Database to be used for data transactions.
        """

        self.db = db

        # Building request parameters
        request_paramters = self.__buildRequestParams(pmids)
        # Making request
        r = get(url=config.ncbi_api['url'], params=request_paramters)

        if r.ok:
            self.__successfulRequestHandler(response_raw=r.text)
        else:
            self.__failedRequestHandler(pmids=pmids)

    def __buildRequestParams(self, pmids: list) -> dict:
        """Function to build request parameter dictionary.
        
        Arguments:
            pmids {list} -- List of PubMed IDs to be queried.
        
        Returns:
            dict -- Request parameters.
        """

        default_headers = {
            'dbfrom': 'pubmed',
            'linkname': 'pubmed_pubmed_citedin+pubmed_pubmed_refs',
            'tool': config.ncbi_api['tool'],
            'email': config.ncbi_api['email'],
            'api_key': config.ncbi_api['api_key'],
            'id': pmids
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
        print(json.dumps(response))

    def __failedRequestHandler(self, pmids: list):
        """Function to handle a failed request.
        
        Arguments:
            pmids {list} -- List of PubMed IDs that failed.
        """

        # Add failed PubMed IDs to log database
        db.addMultiple(database='L', data=pmids)
        # Logging warning
        logging.warn('Request failed for {0}'.format(pmids))
