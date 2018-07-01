from abc import ABC, abstractmethod


class DatabaseAbstractClass(ABC):
    """Abstract class to describe the Database interface for the PaperRank
    application. Any database modules used in the application treat this
    as its superclass, and thus implement all of its methods.

    Raises:
        NotImplementedError -- Raised when not implemented.
    """

    @abstractmethod
    def __init__(self, *args):
        """Abstract class method for `__init__` function skeleton, which should
        be used to implement the database connection function. Arguments to
        this function are not defined, as they will be idiosyncratic to the
        specific database used.
        
        Raises:
            NotImplementedError -- Raised when not implemented.
        """

        raise NotImplementedError

    @abstractmethod
    def checkConnection(self) -> bool:
        """Abstract class method for `checkConnection` function skeleton, which
        should be used to implement a check connection function, to test that
        the database connection is workign correctly
        
        Raises:
            NotImplementedError -- Raised when not implemented
        
        Returns:
            bool -- True if connection is successful.
        """

        raise NotImplementedError

    @abstractmethod
    def addMultiple(self, database: str, data: object) -> bool:
        """Abstract class method for `addMultiple` function skeleton,
        which should be used to add multiple values/data with a given
        key and value to a database with a given name.
        
        Arguments:
            database {str} -- Database data should be added to.
            data {object} -- List if adding to Set, Dict if adding to HashMap.
        
        Raises:
            NotImplementedError -- Raised when not implemented.

        Returns:
            bool -- True if successful, false if not.
        """
        
        raise NotImplementedError

    @abstractmethod
    def removeMultiple(self, database: str, data: list) -> object:
        """Abstract class method for `removeAll` function skeleton, which should
        be implemented to remove data corresponding to given keys and
        database name.
        
        Arguments:
            database {str} -- Name of the database.
            data {list} -- Keys for the values to be removed.
        
        Raises:
            NotImplementedError -- Raised when not implemented.

        Returns:
            object -- Value that was removed.
        """

        raise NotImplementedError

    @abstractmethod
    def contains(self, database: str, key: str) -> bool:
        """Abstract class method for the `contains` function skeleton, which
        should be implemented to check if a value with a given key exists in a
        given database.
        
        Arguments:
            database {str} -- Name of the database.
            key {str} -- Key to be checked.
        
        Raises:
            NotImplementedError -- Raised when not implemented.
        
        Returns:
            bool -- True if value is contained in database, false if not.
        """

        raise NotImplementedError

    @abstractmethod
    def pop(self, database: str, n: int=1) -> list:
        """Abstract class method for the `pop` function skeleton, which should
        be implemented to remove and return `n` items from a set in the
        databse. The number of items is optional, with the default being one.
        
        Arguments:
            database {str} -- Name of the database.

        Keyword Arguments:
            n {int} -- Number of items to return (default: {1}).
        
        Raises:
            NotImplementedError -- Raised when not implemented.

        Returns:
            list -- List of popped items.
        """
        raise NotImplementedError
