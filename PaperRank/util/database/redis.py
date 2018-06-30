from .database import DatabaseAbstractClass
import redis


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

    def contains(self, key: str) -> bool:
        """Check if a given key exists in the Redis database.
        
        Arguments:
            key {str} -- Key to be checked.
        
        Returns:
            bool -- True if it exists, false otherwise.
        """

        try:
            return self.r.exists(key)
        except Exception:
            logging.warn('Key lookup operation failed')

    def setContainsValue(self, set_key: str, value: str) -> bool:
        try:
            return self.r.sismember(name=set_key, value=value)
        except Exception:
            logging.warn('Set lookup operation failed.')

    def add(self):
        pass

    def remove(self):
        pass
