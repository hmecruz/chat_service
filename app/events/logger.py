import logging
import os

# Get absolute path to the current file's directory (app/events/)
log_dir = os.path.dirname(__file__)
log_file_path = os.path.join(log_dir, 'events.log')

# Setup logger for events
events_logger = logging.getLogger("events_logger")
events_logger.setLevel(logging.DEBUG)
events_logger.propagate = False
events_logger.handlers.clear()

# Create a file handler to store logs in 'events.log'
file_handler = logging.FileHandler(log_file_path, mode='w')  # Use 'w' for overwriting, 'a' for append
file_handler.setLevel(logging.DEBUG)

# Define the format for the log entries
formatter = logging.Formatter(
    'Module %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s - %(asctime)s'
)
file_handler.setFormatter(formatter)

# Add the file handler to the logger
events_logger.addHandler(file_handler)

# Optionally, you can also add a console handler to see logs on the terminal (useful during development)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set this to INFO or ERROR for terminal output
console_handler.setFormatter(formatter)
events_logger.addHandler(console_handler)
