def load_territories(file_path):
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