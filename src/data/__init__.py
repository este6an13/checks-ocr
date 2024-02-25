import os

def load_territories(file_path='data/data/territories.txt'):
    words_list = []
    with open(file_path, 'r') as file:
        for line in file:
            word = line.strip()
            words_list.append(word)
    return words_list

def is_in_territories(city, TERRITORIES):
    words = city.split()
    words = [w.lower() for w in words]
    if all([w in TERRITORIES for w in words]):
        return True
    return False

def setup_data():
    # Define the file paths
    territories_file = "data/data/territories.txt"
    client_names_file = "data/data/client_names.txt"
    account_names_file = "data/data/account_names.txt"

    # Create the 'data' directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Create the 'territories.txt' file if it doesn't exist
    with open(territories_file, 'a'):
        os.utime(territories_file, None)

    # Create the 'client_names.txt' file if it doesn't exist
    with open(client_names_file, 'a'):
        os.utime(client_names_file, None)

    # Create the 'account_names.txt' file if it doesn't exist
    with open(account_names_file, 'a'):
        os.utime(account_names_file, None)
