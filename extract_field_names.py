import csv
import json

def extract_field_names_from_log(log_string):
    """
    Extracts and returns a set of field names from a JSON-formatted log string.
    
    Args:
        log_string (str): A string containing JSON-formatted log data.
        
    Returns:
        set: A set of unique field names from the log data.
    """
    log_data = json.loads(log_string)
    return set(log_data.keys())

def process_csv(input_file, output_file):
    """
    Reads a CSV file containing JSON-formatted log data, extracts unique field names,
    and writes them to a TXT file.
    
    Args:
        input_file (str): The path to the input CSV file.
        output_file (str): The path to the output TXT file.
    """
    field_names = set()
    
    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            log_string = row[0]
            field_names.update(extract_field_names_from_log(log_string))

    with open(output_file, 'w') as outfile:
        for field_name in field_names:
            outfile.write(f"{field_name}\n")

if __name__ == "__main__":
    input_csv_file = 'input.csv'
    output_txt_file = 'output.txt'
    process_csv(input_csv_file, output_txt_file)
