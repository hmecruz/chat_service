import logging
import os

# Ensure the log directory exists (services logs will be stored here)
log_dir = os.path.join(os.path.dirname(__file__))
log_file_path = os.path.join(log_dir, 'services.log')

# Setup the service logger
services_logger = logging.getLogger("services_logger")
services_logger.setLevel(logging.DEBUG)  # Adjust level as needed (DEBUG, INFO, WARNING, etc.)
services_logger.propagate = True
services_logger.handlers.clear()

file_handler = logging.FileHandler(log_file_path, mode='a')  # Use append mode
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    'Module %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s - %(asctime)s'
)
file_handler.setFormatter(formatter)

services_logger.addHandler(file_handler)