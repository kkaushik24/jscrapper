import logging

# initialize logger
logger = logging.getLogger(__name__)

# set level for the logger
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('process_log.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
