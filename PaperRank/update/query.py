from ..util import config, Database
import logging
import requests
import threading


class Query:
    def __init__(self, db: Database, pmids: list):
        """Query class initialization. Makes request and delegates worker
        threads with response data.
        
        Arguments:
            pmids {list} -- List of PubMed IDs to be queried.
            db {Database} -- Database to be used for data transactions.
        """

        # Building request parameters
        request_paramters = self.__buildRequestParams(pmids)
        # Making request
        r = requests.get(url=config.ncbi_api['url'], params=request_paramters)

        if r.ok:
            # do stuff
            pass
        else:
            # do stuff
            pass        

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
