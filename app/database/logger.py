import logging
import os

# Get absolute path to the current file's directory (app/database/)
log_dir = os.path.dirname(__file__)
log_file_path = os.path.join(log_dir, 'database.log')

# Setup logger
database_logger = logging.getLogger("database_logger")
database_logger.setLevel(logging.DEBUG)
database_logger.propagate = False
database_logger.handlers.clear()

file_handler = logging.FileHandler(log_file_path, mode='w')  # Use append mode
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    'Module %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s - %(asctime)s'
)
file_handler.setFormatter(formatter)

database_logger.addHandler(file_handler)