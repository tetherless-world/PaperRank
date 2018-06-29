from abc import ABC, abstractmethod
import logging
import redis


class DatabaseConnector(ABC):
    """Abstract class to describe the Database interface for the PaperRank
    application. Any database modules used in the application treat this
    as its superclass, and thus implement all of its methods.

    Raises:
        NotImplementedError -- Raised when not implemented.
    """

    @abstractmethod
    def connect(self, *args) -> bool:
        """Abstract class method for `connect` function skeleton, which should
        be used to implement the database connection function. Arguments to
        this function are not defined, as they will be idiosyncratic to the
        specific database used.
        
        Raises:
            NotImplementedError -- Raised when not implemented.
        
        Returns:
            bool -- True if successful, false otherwise.
        """

        raise NotImplementedError

    @abstractmethod
    def add(self, database: str, key: str, value: object) -> bool:
        """Abstract class method for `add` function skeleton, which should
        be used to add a data value with a given key and value to a database
        with a given name.
        
        Arguments:
            database {str} -- Name of the database.
            key {str} -- Key for the value to be added.
            value {object} -- Data to be added with the given key.
        
        Raises:
            NotImplementedError -- Raised when not implemented.

        Returns:
            bool -- True if successful, false if not.
        """

        raise NotImplementedError

    @abstractmethod
    def remove(self, database: str, key: str) -> object:
        """Abstract class method for `remove` function skeleton, which should
        be implemented to remove data corresponding to a given key and
        database name.
        
        Arguments:
            database {str} -- Name of the database.
            key {str} -- Key for the value to be removed.
        
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


class Redis(DatabaseConnector):
    def __init__(self):
        pass

    def connect(self, host: str, port: int, db: int) -> bool:
        """Connect to the Redis database.
        
        Arguments:
            host {str} -- Hostname of the database.
            port {int} -- Port number of the database.
            db {int} -- Database number to connect to.
        
        Raises:
            RuntimeError -- Raised when the database connection fails.

        Returns:
            bool -- True if connection is successful.
        """

        # Connect to Redis
        self.r = redis.StrictRedis(host=host, port=port, db=db)
        try:
            # Attempt ping
            return self.r.ping()
        except redis.exceptions.ConnectionError:
            logging.error('Redis database connection failed.')
            raise RuntimeError('Redis connection failed.')

    def contains(self):
        pass

    def add(self):
        pass

    def remove(self):
        pass
