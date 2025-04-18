import os

def create_tax_slabs(projections: dict) -> list:
    """
    Creates tax slabs based on the projected revenue values from budget_projection_tool.
    The logic used is:
      - Calculate total projected revenue from the 'projected_revenue' list.
      - Define three slabs:
          Slab 1: 0 to 20% of total revenue, tax rate = 10%
          Slab 2: 20% to 70% of total revenue, tax rate = 20%
          Slab 3: Above 70% of total revenue, tax rate = 30%
    
    Prints the computed total revenue and details for each slab.
    
    Returns a list of dictionaries representing each tax slab.
    """
    revenue_items = projections.get("projected_revenue", [])
    if not revenue_items:
        print("No projected revenue data available to create tax slabs.")
        return []

    total_revenue = sum(item.get("projected_amount", 0) for item in revenue_items)
    print(f"Total Projected Revenue: {total_revenue:.2f}")

    # Define slab limits based on total projected revenue
    slab1_limit = total_revenue * 0.2
    slab2_limit = total_revenue * 0.7

    # Create tax slabs
    slabs = [
        {"slab": 1, "range": f"0 - {slab1_limit:.2f}", "tax_rate": "10%"},
        {"slab": 2, "range": f"{slab1_limit:.2f} - {slab2_limit:.2f}", "tax_rate": "20%"},
        {"slab": 3, "range": f"Above {slab2_limit:.2f}", "tax_rate": "30%"}
    ]

    print("Tax slabs created:")
    for slab in slabs:
        print(f"Slab {slab['slab']}: Range: {slab['range']}, Tax Rate: {slab['tax_rate']}")

    return slabs