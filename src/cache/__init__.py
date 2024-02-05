import os
import json
from utils import get_id

def check_if_cached(filename, cache_folder):
    """
    Check if a file with the same name (without extension) exists in the cache folder.
    If the cache folder doesn't exist, it will be created.

    :param filename: The full filename including extension.
    :param cache_folder: The name of the cache folder (default is '../../cache').
    :return: True if a matching file is found, False otherwise.
    """
    try:
        # Extract the filename without the extension
        id = get_id(filename)

        # Check if the cache folder exists, create it if not
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        # Check if a matching file exists in the cache folder
        cache_file_path = os.path.join(cache_folder, f"{id}.json")
        return os.path.exists(cache_file_path)
    except Exception as e:
        print(f"Error: Unable to check cache for file. {e}")
        return False
    

def read_cache(filename, cache_folder):
    """
    Load JSON data from a cache file with the same name (without extension) as the provided filename.

    :param filename: The full filename including extension.
    :param cache_folder: The name of the cache folder (default is 'cache').
    :return: The loaded JSON data as a Python object if the file exists, None otherwise.
    """
    try:
        # Extract the filename without the extension
        id = get_id(filename)

        # Check if a matching JSON file exists in the cache folder
        cache_file_path = os.path.join(cache_folder, f"{id}.json")

        if os.path.exists(cache_file_path):
            # Load JSON data from the file
            with open(cache_file_path, 'r') as json_file:
                data = json.load(json_file)
            return data
        else:
            print(f"Error: Cache file '{cache_file_path}' not found.")
            return None
    except Exception as e:
        print(f"Error: Unable to load data from cache. {e}")
        return None


def write_to_cache(res, id, cache_folder):
    """
    Write JSON data to a cache file with the specified ID.

    :param res: The JSON data to write.
    :param id: The ID for naming the cache file.
    :param cache_folder: The name of the cache folder (default is 'cache').
    :return: True if the write is successful, False otherwise.
    """
    try:
        # Create the cache folder if it doesn't exist
        os.makedirs(cache_folder, exist_ok=True)

        # Create the cache file path
        cache_file_path = os.path.join(cache_folder, f"{id}.json")

        # Write JSON data to the cache file
        with open(cache_file_path, 'w') as json_file:
            json.dump(res, json_file, indent=2)

        return True
    except Exception as e:
        print(f"Error: Unable to write data to cache. {e}")
        return False