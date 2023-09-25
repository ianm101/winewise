import logging
import sys

def setup_logger():
    # Create a logger object
    logger = logging.getLogger("wine-recommender")
    
    # Set the level of the logger. This is the threshold. Anything below this level will be ignored.
    logger.setLevel(logging.DEBUG)
    
    # Create a file handler object
    file_handler = logging.FileHandler("wine_recommender.log")
    
    # Create a stream handler object
    stream_handler = logging.StreamHandler(sys.stdout)
    
    # Set the level of the file and stream handler
    file_handler.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Set the formatter for the handlers
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger