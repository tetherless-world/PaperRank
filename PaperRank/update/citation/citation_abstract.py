from abc import ABC, abstractmethod


class CitationAbstractClass(ABC):
    """Abstract class to describe the Citation interface for the `update`
    module. This class will be inherited by a subclass that implements API
    response parsing for the relevant response.

    Raises:
        NotImplementedError -- Raised when not implemented.
    """

    @abstractmethod
    def __init__(self):
        """Abstract class method for `__init__` function skeleton, which
        should be used to implement the logic for API response parsing,
        and to construct the final `Citation` object with the attributes
        `id`, `inbound`, and `outbound`.
        
        Raises:
            NotImplementedError -- Raised when not implemented.
        """

        raise NotImplementedError

    @property
    def id(self):
        """Abstract property `id`. This attribute will store the ID
        of the citation.
        
        Raises:
            NotImplementedError -- Raised when not implemented.
        """

        raise NotImplementedError

    @property
    def outbound(self):
        """Abstract property `outbound`. This attribute will store a list
        of outbound citations.
        
        Raises:
            NotImplementedError -- Raised when not implemented.
        """

        raise NotImplementedError

    @property
    def inbound(self):
        """Abstract propert `inbound`. This attribute will store a list of
        inbound citations.
        
        Raises:
            NotImplementedError -- Raised when not implemented.
        """

        raise NotImplementedError
