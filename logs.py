import logging

# logs to file
format = '%(asctime)s - %(filename)s (%(lineno)s) - %(levelname)s - %(message)s'
logging.basicConfig(filename='.log', format=format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
