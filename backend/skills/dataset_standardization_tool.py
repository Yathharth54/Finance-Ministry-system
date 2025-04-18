import json
import os
from skills.data_validation_tool import validate_data  # Import your validation tool

def standardize_data(file_path: str) -> dict:
    print(f"\n[DEBUG] Starting standardization for {file_path}")
    """
    Loads the JSON file at file_path and standardizes it by filling missing numeric fields:
      - For 'revenue' and 'expenditure', missing or invalid 'amount' values are filled with the mean amount.
      - For 'inflation' and 'gdp_growth', missing or invalid 'rate' values are filled with the mean rate.
    
    The function first checks the data using validate_data. If validation passes, no standardization is needed.
    It prints out messages explaining its actions and returns the updated data dictionary.
    """
    # Check file existence and load JSON data
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        return {}
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {file_path}")
        return {}
    
    # Validate the data using the data_validation_tool
    if validate_data(file_path):
        print("Data is valid. No standardization needed.")
        return data
    else:
        print("Data validation failed. Proceeding with data standardization...")

    # Define sections and their numeric fields to check
    sections = {
        "revenue": "amount",
        "expenditure": "amount",
        "inflation": "rate",
        "gdp_growth": "rate"
    }

    # For each section, compute mean and fill missing or invalid values
    for section, field in sections.items():
        if section in data and isinstance(data[section], list):
            # Collect values that are present and numeric
            present_values = [item[field] for item in data[section]
                              if field in item and isinstance(item[field], (int, float))]
            if present_values:
                mean_value = sum(present_values) / len(present_values)
            else:
                mean_value = 0  # Default if no valid numbers are present

            # Iterate through the section to standardize missing/invalid numeric fields
            for index, item in enumerate(data[section]):
                if field not in item or not isinstance(item[field], (int, float)):
                    print(f"Standardizing: In section '{section}', record {index} missing or invalid '{field}'. Filling with mean value {mean_value:.2f}.")
                    item[field] = mean_value
    
    return data

