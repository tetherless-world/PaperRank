from context import PaperRank
import logging
import redis
import sys

########################
# LOGGING
########################

# Setting up formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - \
    %(levelname)s - %(message)s')

# Setting up base logger
root = logging.getLogger()
root.setLevel(logging.INFO)

# Adding stdout and log file
log_file = logging.FileHandler('compute_out.log')
log_stdout = logging.StreamHandler(sys.stdout)

# Setting formatter
log_file.setFormatter(formatter)
log_stdout.setFormatter(formatter)

# Adding handlers
root.addHandler(log_stdout)
root.addHandler(log_file)


########################
# PaperRank
########################

# Setting up configuration
PaperRank.util.configSetup(override='default.json')

config = PaperRank.util.config

# Creating redis-py connection
r = redis.StrictRedis(
    host=config.redis['host'],
    port=config.redis['port'],
    db=config.redis['db']
)

# Creating manager
manager = PaperRank.compute.Manager(r=r)

manager.start(cutoff=100)
