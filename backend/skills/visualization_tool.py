import os
import uuid
import json
import matplotlib
# Force matplotlib to use a non-interactive backend that doesn't require a GUI
matplotlib.use('Agg')  # Add this line before importing pyplot
import matplotlib.pyplot as plt

def create_visual_plots(data: dict, output_dir: str = "visual plots") -> None:
    """
    Creates visualizations for:
      1. Revenues (pie chart)
      2. Expenditure (bar plot)
      3. GDP Growth (scatter plot)
      4. Inflation (scatter plot)
    
    Saves each image in the 'output_dir' with a unique filename.
    """
    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # 1. Pie chart for revenues
    revenue_data = data.get("revenue", [])
    if revenue_data:
        labels = [item.get("name", "Unknown") for item in revenue_data]
        sizes = [item.get("amount", 0) for item in revenue_data]
        plt.figure()
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Revenues")
        pie_file = os.path.join(output_dir, f"pie_chart_revenues_{uuid.uuid4().hex}.png")
        plt.savefig(pie_file)
        plt.close()
        print(f"Saved pie chart for revenues as: {pie_file}")
    else:
        print("No revenue data available for visualization.")

    # 2. Bar plot for expenditure
    expenditure_data = data.get("expenditure", [])
    if expenditure_data:
        labels = [item.get("name", "Unknown") for item in expenditure_data]
        amounts = [item.get("amount", 0) for item in expenditure_data]
        plt.figure()
        plt.bar(labels, amounts, color='skyblue')
        plt.xlabel("Expenditure Category")
        plt.ylabel("Amount")
        plt.title("Expenditure")
        plt.xticks(rotation=45, ha="right")
        bar_file = os.path.join(output_dir, f"bar_plot_expenditure_{uuid.uuid4().hex}.png")
        plt.tight_layout()
        plt.savefig(bar_file)
        plt.close()
        print(f"Saved bar plot for expenditure as: {bar_file}")
    else:
        print("No expenditure data available for visualization.")

    # 3. Scatter plot for GDP Growth
    gdp_growth_data = data.get("gdp_growth", [])
    if gdp_growth_data:
        years = [item.get("year", "Unknown") for item in gdp_growth_data]
        rates = [item.get("rate", 0) for item in gdp_growth_data]
        plt.figure()
        plt.scatter(years, rates, color='green')
        plt.xlabel("Year")
        plt.ylabel("GDP Growth Rate")
        plt.title("GDP Growth")
        scatter_gdp_file = os.path.join(output_dir, f"scatter_plot_gdp_growth_{uuid.uuid4().hex}.png")
        plt.savefig(scatter_gdp_file)
        plt.close()
        print(f"Saved scatter plot for GDP growth as: {scatter_gdp_file}")
    else:
        print("No GDP growth data available for visualization.")

    # 4. Scatter plot for Inflation
    inflation_data = data.get("inflation", [])
    if inflation_data:
        years = [item.get("year", "Unknown") for item in inflation_data]
        rates = [item.get("rate", 0) for item in inflation_data]
        plt.figure()
        plt.scatter(years, rates, color='red')
        plt.xlabel("Year")
        plt.ylabel("Inflation Rate")
        plt.title("Inflation")
        scatter_inflation_file = os.path.join(output_dir, f"scatter_plot_inflation_{uuid.uuid4().hex}.png")
        plt.savefig(scatter_inflation_file)
        plt.close()
        print(f"Saved scatter plot for Inflation as: {scatter_inflation_file}")
    else:
        print("No inflation data available for visualization.")

def create_visual_plots_from_json(file_path: str = "input_data.json", output_dir: str = "visual plots") -> None:
    """
    Reads a JSON file, converts it into a dictionary, and then passes it to create_visual_plots().
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        print(f"Loaded data from {file_path}")
        create_visual_plots(data, output_dir)
    except Exception as e:
        print(f"Error: {e}")