import json
import os

def validate_data(file_path: str) -> bool:
    """
    Validates the structure of the financial data JSON file.
    Returns True if valid, False otherwise.
    """
    # 1. Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        return False

    # 2. Load the JSON data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)  
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {file_path}")
        return False

    # 3. Rest of your validation logic below...
    required_keys = {
        "revenue": ["name", "amount"],
        "expenditure": ["name", "amount"],
        "inflation": ["year", "rate"],
        "gdp_growth": ["year", "rate"]
    }

    for key, required_fields in required_keys.items():
        if key not in data:
            print(f"Error: Missing required field: '{key}'")
            return False

        if not isinstance(data[key], list):
            print(f"Error: The field '{key}' should be a list.")
            return False

        for index, item in enumerate(data[key]):
            if not isinstance(item, dict):
                print(f"Error: Item {index} in '{key}' is not a JSON object.")
                return False

            for field in required_fields:
                if field not in item:
                    print(f"Error: Missing field '{field}' in item {index} of '{key}'.")
                    return False
                
                if field == "amount" and not isinstance(item[field], (int, float)):
                    print(f"Error: Field 'amount' in item {index} of '{key}' must be numeric.")
                    return False
                if field == "rate" and not isinstance(item[field], (int, float)):
                    print(f"Error: Field 'rate' in item {index} of '{key}' must be numeric.")
                    return False
                if field == "year" and not isinstance(item[field], str):
                    print(f"Error: Field 'year' in item {index} of '{key}' must be a string.")
                    return False

    print("Validation succeeded! The input data structure is correct.")
    return True