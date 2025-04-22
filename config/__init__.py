import logging

config_logger = logging.getLogger(__name__)  # Logger for the entire config package
config_logger.setLevel(logging.WARNING)

# Prevent log messages from propagating to the root logger (which might print to console)
config_logger.propagate = False

# Remove any existing handlers (e.g., StreamHandler that might print to console)
config_logger.handlers.clear()

# Create file handler
file_handler = logging.FileHandler('config/config.log', mode='w')
file_handler.setLevel(logging.WARNING)

# Set formatter
formatter = logging.Formatter(
    'Module %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s - %(asctime)s'
)
file_handler.setFormatter(formatter)

# Add file handler to logger
config_logger.addHandler(file_handler)