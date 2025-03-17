import os
import warnings
from typing import Optional


def get_env_variable(var_name: str, default_value: Optional[str] = None) -> str:
    """
    Fetch an environment variable.

    Args:
        var_name: The name of the environment variable.
        default_value: The default value to return if the variable is not set.

    Returns:
        The value of the environment variable, or the default value.

    Raises:
        ValueError: If the variable is not set and no default value is provided.
    """
    value = os.getenv(var_name)
    
    if value is None:
        if default_value is None:
            raise ValueError(f"Error: {var_name} is not set and no default is provided.")
        warnings.warn(f"Warning: {var_name} is not set. Using default: {default_value}")
        return default_value
    
    return value