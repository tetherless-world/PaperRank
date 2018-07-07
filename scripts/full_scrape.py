from context import PaperRank
import logging
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
log_file = logging.FileHandler('out.log')
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

# Connecting to database
db = PaperRank.util.Database(
    host=config.redis['host'],
    port=config.redis['port'],
    db=config.redis['db']
)

manager = PaperRank.update.Manager(db=db)

# Adding some IDs to the EXPLORE set for initialization, if empty
if db.isEmpty(database='E'):
    db.addMultiple(database='E', data=[21876761, 21876726])

manager.start()
