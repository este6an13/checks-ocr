import re
from unidecode import unidecode
from dateutil import parser
from textract import in_top_left_corner

def extract_numbers(text):
    """
    Extract numbers from the given text using regular expressions.

    :param text: The details containing account numbers.
    :return: List of extracted numbers.
    """
    # Define the regex pattern to match numbers
    pattern = re.compile(r'\b\d+\b')

    # Find all matches in the text
    matches = pattern.findall(text)

    # Concatenate the matches into a single string
    result = ''.join(matches)

    return result

def extract_float_numbers(text):
    """
    Extract floating point numbers from the given text using regular expressions.

    :param text: The text containing numbers.
    :return: List of extracted float numbers.
    """
    # Define the regex pattern to match floating point numbers with both comma and dot as decimal separators
    pattern = re.compile(r'[-+]?\d*[.,]?\d+|\d+')

    # Find all matches in the text
    matches = pattern.findall(text)

    # Convert the matches to float numbers
    result = [float(match.replace(',', '.')) for match in matches]

    if len(result) > 0:
        result = result[0]
    else:
        result = 0

    return result

def clean_and_uppercase(text):
    """
    Clean and convert the given text to uppercase without special characters.

    :param text: The input details text.
    :return: The cleaned and uppercase text.
    """
    # Convert to uppercase
    text_uppercase = text.upper()

    # Remove special characters
    cleaned_text = re.sub(r'[^A-Z0-9\s]', '', unidecode(text_uppercase))

    return cleaned_text



def get_city_and_date(text):
    """
    Parse date from the text and clean the remaining details.

    :param text: The input text containing date and details.
    :return: Tuple of (formatted_date, cleaned_details).
    """
    # Define a regex pattern to match dates in various formats
    date_pattern = re.compile(r'\b\d{4}[-/]\d{2}[-/]\d{2}\b')

    # Find the first match of the date pattern
    date_match = date_pattern.search(text)

    if date_match:
        # Extract the matched date
        raw_date = date_match.group()

        # Parse and format the date as YYYY-MM-DD
        parsed_date = parser.parse(raw_date).strftime('%Y-%m-%d')
    else:
        parsed_date = None

    # Remove the date part from the text
    cleaned_text = re.sub(date_pattern, '', text).strip()

    # Clean and uppercase the remaining details
    city = clean_and_uppercase(cleaned_text)

    return parsed_date, city

def get_bank_code(BANK_CODES, blocks):
    for block in blocks:
        for bank_code in BANK_CODES:
            if bank_code in block['Text'].lower() and in_top_left_corner(block):
                return bank_code
    return None