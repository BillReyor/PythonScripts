import json

def process_json_file(input_file, output_file):
    """
    Process a JSON file by removing 'additional_fields' and entries with None values.

    Args:
        input_file (str): The path to the input JSON file.
        output_file (str): The path to the output JSON file.
    """
    # Open and read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

    processed_data = []
    # Iterate through the items in the input JSON data
    for item in data:
        # Select items that are not None
        if item is not None:
            # Remove 'additional_fields' key from the item
            if 'additional_fields' in item:
                del item['additional_fields']

            # Remove entries with None values
            item = {k: v for k, v in item.items() if v is not None}

            # Add the processed item to the processed_data list
            if item:
                processed_data.append(item)

    # Write the processed data to the output JSON file
    with open(output_file, 'w') as f:
        json.dump(processed_data, f, indent=2)

if __name__ == "__main__":
    # Ask the user for the input file name
    input_file = input("Enter the input file name: ")
    output_file = "output.json"

    # Process the JSON file and save the output
    process_json_file(input_file, output_file)
    print(f"Output saved to {output_file}")
