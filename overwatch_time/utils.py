import os

def resource_path(relative_path):
    """
    Get the absolute path to a resource within the package.
    
    Parameters:
        relative_path (str): The relative path within the package directory.
    
    Returns:
        str: The absolute path to the resource.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))  # Path to utils.py
    resource_path = os.path.join(base_path, 'resources')
    return os.path.join(resource_path, relative_path)

def data_path(relative_path):
    """
    Get the absolute path to a data file within the user's AppData directory.
    
    Parameters:
        relative_path (str): The relative path within the data directory.
    
    Returns:
        str: The absolute path to the data file.
    """
    base_data_path = os.path.join(os.getenv('APPDATA'), 'OverwatchTimeData')
    
    # Ensure the base data path exists
    if not os.path.exists(base_data_path):
        os.makedirs(base_data_path)

    return os.path.join(base_data_path, relative_path)



def format_duration(seconds):
    """
    Convert seconds into a human-readable duration format.

    Parameters:
        seconds (float): Duration in seconds.

    Returns:
        str: Formatted duration string.
    """
    days, seconds = divmod(seconds, 86400)  # 86400 seconds in a day
    hours, seconds = divmod(seconds, 3600)  # 3600 seconds in an hour
    minutes, seconds = divmod(seconds, 60)  # 60 seconds in a minute

    duration_parts = []
    if days > 0:
        duration_parts.append(f"{int(days)} days")
    if hours > 0:
        duration_parts.append(f"{int(hours)} hours")
    if minutes > 0:
        duration_parts.append(f"{int(minutes)} mins")
    if seconds > 0 or not duration_parts:
        duration_parts.append(f"{int(seconds)} seconds")

    return ", ".join(duration_parts)
