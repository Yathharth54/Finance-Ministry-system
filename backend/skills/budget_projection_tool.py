import json
import os
import numpy as np

def project_budget(file_path: str) -> dict:
    """
    Loads the JSON file at file_path and performs projections:
      - For 'revenue': Each category is projected with a fixed 5% growth rate.
      - For 'expenditure': Each category is projected with a fixed 3% growth rate.
      - For 'inflation': A linear regression is applied to the year-rate series to predict next year's inflation rate.
      - For 'gdp_growth': A linear regression is applied to the year-rate series to predict next year's GDP growth rate.
    
    Prints details about the projection process and returns a dictionary with projected values.
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file: {file_path}")
        return {}
    
    projections = {}

    # 1. Project revenue: Use a fixed growth rate of 5%
    revenue_data = data.get("revenue", [])
    projected_revenue = []
    revenue_growth_rate = 0.05
    for item in revenue_data:
        projected_item = item.copy()
        current_amount = item.get("amount", 0)
        projected_item["projected_amount"] = current_amount * (1 + revenue_growth_rate)
        projected_revenue.append(projected_item)
        print(f"Revenue '{item.get('name', 'Unknown')}' projected from {current_amount} to {projected_item['projected_amount']:.2f}.")
    projections["projected_revenue"] = projected_revenue

    # 2. Project expenditure: Use a fixed growth rate of 3%
    expenditure_data = data.get("expenditure", [])
    projected_expenditure = []
    expenditure_growth_rate = 0.03
    for item in expenditure_data:
        projected_item = item.copy()
        current_amount = item.get("amount", 0)
        projected_item["projected_amount"] = current_amount * (1 + expenditure_growth_rate)
        projected_expenditure.append(projected_item)
        print(f"Expenditure '{item.get('name', 'Unknown')}' projected from {current_amount} to {projected_item['projected_amount']:.2f}.")
    projections["projected_expenditure"] = projected_expenditure

    # 3. Project inflation using linear regression to predict next year's rate
    inflation_data = data.get("inflation", [])
    if inflation_data and len(inflation_data) >= 2:
        years, rates = [], []
        for item in inflation_data:
            try:
                years.append(int(item.get("year")))
                rates.append(float(item.get("rate")))
            except (ValueError, TypeError):
                continue
        if len(years) >= 2:
            m, c = np.polyfit(years, rates, 1)  # Linear regression: rate = m * year + c
            next_year = max(years) + 1
            projected_inflation_rate = m * next_year + c
            projections["projected_inflation"] = {"year": str(next_year), "rate": round(projected_inflation_rate, 2)}
            print(f"Inflation projected for year {next_year} is {projected_inflation_rate:.2f} using linear regression.")
        else:
            avg_rate = np.mean(rates) if rates else 0
            next_year = max(years) + 1 if years else "Unknown"
            projections["projected_inflation"] = {"year": str(next_year), "rate": round(avg_rate, 2)}
            print(f"Not enough data for regression. Using average inflation rate {avg_rate:.2f} for year {next_year}.")
    else:
        print("Insufficient inflation data for projection.")
        projections["projected_inflation"] = {}

    # 4. Project GDP Growth using linear regression to predict next year's rate
    gdp_growth_data = data.get("gdp_growth", [])
    if gdp_growth_data and len(gdp_growth_data) >= 2:
        years, rates = [], []
        for item in gdp_growth_data:
            try:
                years.append(int(item.get("year")))
                rates.append(float(item.get("rate")))
            except (ValueError, TypeError):
                continue
        if len(years) >= 2:
            m, c = np.polyfit(years, rates, 1)
            next_year = max(years) + 1
            projected_gdp_growth_rate = m * next_year + c
            projections["projected_gdp_growth"] = {"year": str(next_year), "rate": round(projected_gdp_growth_rate, 2)}
            print(f"GDP Growth projected for year {next_year} is {projected_gdp_growth_rate:.2f} using linear regression.")
        else:
            avg_rate = np.mean(rates) if rates else 0
            next_year = max(years) + 1 if years else "Unknown"
            projections["projected_gdp_growth"] = {"year": str(next_year), "rate": round(avg_rate, 2)}
            print(f"Not enough data for regression. Using average GDP growth rate {avg_rate:.2f} for year {next_year}.")
    else:
        print("Insufficient GDP growth data for projection.")
        projections["projected_gdp_growth"] = {}
    
    print("Budget projection completed.")
    print(projections)
    return projections