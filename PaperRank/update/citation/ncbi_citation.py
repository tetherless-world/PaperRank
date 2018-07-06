from .citation_abstract import CitationAbstractClass
from ...util import Database
from collections import OrderedDict
import logging


class NCBICitation(CitationAbstractClass):

    def __init__(self, query_raw: OrderedDict):
        """Construct a NCBICitation object, given the raw response
        from the NCBI Entrez API. This method extracts the citation `id`,
        and constructs the `outbound` and `inbound` lists.
        
        Arguments:
            query_raw {OrderedDict} -- Raw response from the NCBI API.
        """

        # Setting default values for inbound, outbound, and error
        self.outbound = []
        self.inbound = []

        # Extracting ID
        self.id = str(query_raw['IdList']['Id'])

        # Setting `error` to True if the ID is 0 (i.e. not found) and return
        if self.id is '0':
            self.error = True
            return

        try:
            if type(query_raw['LinkSetDb']) is list:
                # Both inbound and outbound exist, iterate through
                for citation_direction in query_raw['LinkSetDb']:
                    self.__parseResponseHelper(citation_direction)
            else:
                # Only inbound or outbound exists
                self.__parseResponseHelper(query_raw['LinkSetDb'])
        except Exception:
            # No input or output links found, log ID
            logging.warn('No inbound or outbound citations found for {0}'
                         .format(self.id))

    def __parseResponseHelper(self, citation_direction: OrderedDict):
        """Helper function for `__init__` to extract citations from the
        nested `OrderedDict` structure of the API call.
        
        Arguments:
            citation_direction {OrderedDict} -- `OrderedDict` response from
                                                the API.
        """

        if citation_direction['LinkName'] == 'pubmed_pubmed_citedin':
            # Inbound citations
            self.inbound = [link['Id'] for link
                            in citation_direction['Link']]
        elif citation_direction['LinkName'] == 'pubmed_pubmed_refs':
            # Outbound citations (i.e. references)
            self.outbound = [link['Id'] for link
                             in citation_direction['Link']]

    def outbound(self) -> list:
        """Return the `outbound` citations.
        
        Returns:
            list -- List of outbound citation IDs.
        """

        return self.outbound

    def inbound(self) -> list:
        """Return the `inbound` citations.
        
        Returns:
            list -- List of inbound citation IDs.
        """

        return self.inbound

    def id(self) -> str:
        """Return the `id` of the citation.
        
        Returns:
            str -- ID of the citation stored by this object.
        """

        return self.id

    def error(self) -> bool:
        """Return the `error` flag of the citation.
        
        Returns:
            bool -- True if there is an error, False otherwise.
        """

        return self.error
