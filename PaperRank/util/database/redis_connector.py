from .database_abstract import DatabaseAbstractClass
from functools import wraps
import logging
from redis.client import StrictRedis
import redis

# CONSTANTS
# ==========

# Abbreviation-key mapping
ABBR = {
    'O': 'OUT',
    'S': 'SEEN',
    'G': 'GRAPH',
    'E': 'EXPLORE',
    'I': 'INSTANCE',
    'N': 'NOT'
}


class _Decorators:
    @classmethod
    def verifyDatabase(cls, decorated):
        """Decorator to verify that the database being requested is valid,
        if so update with the full database name.
        """

        @wraps(decorated)
        def wrapper(*args, **kwargs):
            if kwargs['database'] not in ABBR.keys():
                raise RuntimeError('Unknown database name provided.')
            kwargs['database'] = ABBR[kwargs['database']]
            return decorated(*args, **kwargs)
        return wrapper


class Redis(DatabaseAbstractClass):

    def __init__(self, host: str, port: int, db: int):
        """Connect to the Redis database.
        
        Arguments:
            host {str} -- Hostname of the database.
            port {int} -- Port number of the database.
            db {int} -- Database number to connect to.
        
        Raises:
            RuntimeError -- Raised if the database connection failed.
        """

        # Mapping types
        self.db = {
            'OUT': self.RedisHashMap,
            'SEEN': self.RedisSet,
            'GRAPH': self.RedisSet,
            'EXPLORE': self.RedisSet,
            'INSTANCE': self.RedisSet,
            'NOT': self.RedisSet
        }

        # Connect to Redis
        self.r = redis.StrictRedis(host=host, port=port, db=db)
        self.checkConnection()

    def checkConnection(self) -> bool:
        """Check the Redis database connection.
        
        Raises:
            RuntimeError -- Raised if the database connection failed.
        
        Returns:
            bool -- True if connection is successful.
        """

        # Attempt ping
        try:
            return self.r.ping()
        except redis.exceptions.ConnectionError:
            logging.error('Redis database connection failed.')
            raise RuntimeError('Redis connection failed.')

    @_Decorators.verifyDatabase
    def contains(self, database: str, key: str) -> bool:
        """Check if a given key exists in the Redis database.
        
        Arguments:
            database {str} -- Name of the database.
            key {str} -- Key to be checked.
        
        Returns:
            bool -- True if it exists, false otherwise.
        """
        
        return self.db[database].contains(self.r, database, key)

    def add(self):
        pass

    def remove(self):
        pass

    def pop(self, n: int) -> list:
        pass

    def __getSubclass(self, database: str) -> object:
        pass

    class RedisSet:
        """Subclass for Redis Set datastructure operations.
        """

        @staticmethod
        def contains(redis: StrictRedis, database: str, key: str) -> bool:
            pass

    class RedisHashMap:
        """Subclass for Redis HashMap data structure operations.
        """

        @staticmethod
        def contains(redis: StrictRedis, database: str, key: str) -> bool:
            pass
