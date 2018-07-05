from ..util import config, Database
from collections import OrderedDict
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
        self.pmids = pmids

        # Building request parameters
        request_paramters = self.__buildRequestParams()
        # Making request
        r = get(url=config.ncbi_api['url'], params=request_paramters)
        print(r.url)
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
            linkset = linkset_container.pop()
            citation_map = self.__parseResponse(linkset)
            # TODO: Spawn worker thread here with citation_map as input

    def __parseResponse(self, linkset: OrderedDict) -> dict:
        """Function to parse the response from the NCBI API, and return a
        structured dictionary that will be passed to a worker thread. This
        implementation is specific to the NCBI PubMed Entrez API.
        
        Arguments:
            linkset {OrderedDict} -- Response from the server, parsed into an
                                     OrderedDict with `xmltodict`.
        
        Returns:
            dict -- Structured dictionary with keys `id` <str>,
                    `inbound` <list> and `outbound` <list>.
        """

        output = {
            'inbound': [],
            'outbound': []
        }
        output['id'] = linkset['IdList']['Id']
        if type(linkset['LinkSetDb']) is list:
            for citation_direction in linkset['LinkSetDb']:
                output.update(self.__parseResponseHelper(citation_direction))
        else:
            output.update(self.__parseResponseHelper(linkset['LinkSetDb']))
        print(output)
        return output

    def __parseResponseHelper(self, citation_direction: OrderedDict) -> dict:
        """Helper function for `__parseResponse` to extract citations from the
        nested `OrderedDict` structure of the API call.
        
        Arguments:
            citation_direction {OrderedDict} -- `OrderedDict` response from
                                                the API.
        
        Returns:
            dict -- Dictionary with `inbound` or `outbound` key mapping
                    to a list with the relevant PubMed IDs.
        """

        output = dict()

        if citation_direction['LinkName'] == 'pubmed_pubmed_citedin':
            # Inbound citations
            output['inbound'] = [link['Id'] for link
                                 in citation_direction['Link']]
        elif citation_direction['LinkName'] == 'pubmed_pubmed_refs':
            # Outbound citations (i.e. references)
            output['outbound'] = [link['Id'] for link
                                  in citation_direction['Link']]
        
        return output

    def __failedRequestHandler(self):
        """Function to handle a failed request.
        """

        # Add failed PubMed IDs to log database
        db.addMultiple(database='L', data=self.pmids)
        # Logging warning
        logging.warn('Request failed for {0}'.format(self.pmids))
