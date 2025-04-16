# config/__init__.py
import logging

config_logger = logging.getLogger(__name__)  # Logger for the entire config package
config_logger.setLevel(logging.WARNING)

file_handler = logging.FileHandler('config/config.log', mode='w')
file_handler.setLevel(logging.WARNING)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('Module %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s - %(asctime)s')

file_handler.setFormatter(formatter)
config_logger.addHandler(file_handler)