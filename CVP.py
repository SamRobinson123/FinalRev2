import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

## Function To Create CVP table
def cvp_analysis_with_full_sliding_fee(services, sliding_fee_schedule, total_fixed_costs):
    """
    CVP Analysis with full sliding fee schedule for each service, including revenue breakdown per tier,
    and spreading fixed costs evenly across all services.

    Parameters:
    - services: List of dictionaries with 'service_name', 'volume', 'variable_cost_per_unit'
    - sliding_fee_schedule: Dict with fee tiers and prices specific to each service
    - total_fixed_costs: Total fixed costs for the clinic (to be evenly distributed across services)

    Returns:
    - DataFrame with detailed breakdown of revenues, costs, profits, and tier revenue details
    """

    service_data = []
    num_services = len(services)  # Get the number of services

    # Calculate fixed cost per service
    fixed_cost_per_service = total_fixed_costs / num_services

    for service in services:
        service_name = service['service_name']
        volume = service['volume']
        variable_cost_per_unit = service['variable_cost_per_unit']

        # Calculate revenue for each fee tier
        total_revenue = 0
        service_sliding_fee = sliding_fee_schedule[service_name]  # Get sliding fee for this service

        tier_revenues = {}  # Dictionary to store revenue for each tier

        for tier, values in service_sliding_fee.items():
            tier_volume = volume * values['percentage']  # Allocate volume to this tier
            tier_price = values['price']  # Price per unit in this tier
            tier_revenue = tier_volume * tier_price  # Calculate tier revenue
            total_revenue += tier_revenue  # Add tier revenue to total

            # Store tier revenue except for 'Full Charges'
            if tier != 'Full Charges':
                tier_revenues[tier] = tier_revenue

        # Calculate total variable costs
        total_variable_costs = variable_cost_per_unit * volume

        # Calculate total costs (variable + evenly spread fixed cost)
        total_costs = total_variable_costs + fixed_cost_per_service

        # Calculate profit
        profit = total_revenue - total_costs

        # Store the results, including tier revenues
        service_data.append({
            'Service': service_name,
            'Volume': volume,
            **tier_revenues,  # Unpack the tier revenue details
            'Total Revenue': total_revenue,
            'Total Variable Costs': total_variable_costs,
            'Fixed Costs': fixed_cost_per_service,  # Evenly distributed fixed cost per service
            'Total Costs': total_costs,
            'Profit': profit
        })

    # Convert results to a DataFrame
    results_df = pd.DataFrame(service_data)

    # Reorder columns: Move Slides to come right after Volume
    column_order = ['Service', 'Volume'] + list(tier_revenues.keys()) + ['Total Revenue', 'Total Variable Costs',
                                                                         'Fixed Costs', 'Total Costs', 'Profit']
    results_df = results_df[column_order]

    return results_df

## Function To Graph Results
def plot_profit_per_product(results_df):
    """
    Plot the profit for each product (service), improving readability.

    Parameters:
    - results_df: DataFrame containing the profit data for each service.
    """
    # Extract the services and their profits
    services = results_df['Service']
    profits = results_df['Profit']

    # Create a larger bar chart for readability
    plt.figure(figsize=(20, 10))  # Increased figure size for better readability
    plt.bar(services, profits, color='skyblue')

    plt.title('Profit per Product (Service)', fontsize=18)
    plt.xlabel('Product (Service)', fontsize=12)
    plt.ylabel('Profit ($)', fontsize=12)

    # Rotate x-axis labels slightly for readability
    plt.xticks(rotation=30, ha='right', fontsize=10)  # Adjusted rotation and font size
    plt.tight_layout()

    # Show the plot
    plt.show()

## Model Inputs
# Services Provided By the Clinic
services = [
    {'service_name': 'UPFH Medical Fee', 'volume': 1000, 'variable_cost_per_unit': 10},
    {'service_name': 'UPFH Counseling', 'volume': 500, 'variable_cost_per_unit': 5},
    {'service_name': 'UPFH Group Counseling', 'volume': 400, 'variable_cost_per_unit': 10},
    {'service_name': 'UPFH Psychiatric Services', 'volume': 200, 'variable_cost_per_unit': 10},
    {'service_name': 'MOBILE Medical *fees waived utilizing state & local grants', 'volume': 300, 'variable_cost_per_unit': 15},
    {'service_name': 'Inhouse Vision Exam', 'volume': 600, 'variable_cost_per_unit': 15},
    {'service_name': 'Replacement Glasses', 'volume': 150, 'variable_cost_per_unit': 10},
    {'service_name': 'MOBILE EYE Exam', 'volume': 700, 'variable_cost_per_unit': 10},
    {'service_name': 'MOBILE EYE - Single Lens Glasses', 'volume': 400, 'variable_cost_per_unit': 8},
    {'service_name': 'MOBILE EYE - Bifocal Lens Glasses', 'volume': 350, 'variable_cost_per_unit': 12},
    {'service_name': 'MVHC Pharmacy Fill Fee', 'volume': 450, 'variable_cost_per_unit': 5},
    {'service_name': 'MA Visit - Labs outside of 7 day global', 'volume': 500, 'variable_cost_per_unit': 8},
    {'service_name': 'MA Visit - VACCINES', 'volume': 800, 'variable_cost_per_unit': 10},
    {'service_name': 'Nuvaring', 'volume': 100, 'variable_cost_per_unit': 5},
    {'service_name': 'Sprintec', 'volume': 120, 'variable_cost_per_unit': 4},
    {'service_name': 'Loestrin', 'volume': 100, 'variable_cost_per_unit': 5},
    {'service_name': 'Ella', 'volume': 80, 'variable_cost_per_unit': 5},
    {'service_name': 'Depo-Provera', 'volume': 150, 'variable_cost_per_unit': 6},
    {'service_name': 'Nexplanon', 'volume': 90, 'variable_cost_per_unit': 7},
    {'service_name': 'Mirena', 'volume': 70, 'variable_cost_per_unit': 8},
    {'service_name': 'Liletta', 'volume': 60, 'variable_cost_per_unit': 7},
    {'service_name': 'Paragard (limited supply)', 'volume': 50, 'variable_cost_per_unit': 10},
    {'service_name': 'IUD Removal Fee', 'volume': 100, 'variable_cost_per_unit': 8},
    {'service_name': 'Implanon Removal', 'volume': 90, 'variable_cost_per_unit': 7},
    {'service_name': 'Vaccine Administration Fee', 'volume': 600, 'variable_cost_per_unit': 5},
    {'service_name': 'STD Testing PLUS OFFICE VISIT', 'volume': 400, 'variable_cost_per_unit': 12},
    {'service_name': 'Steroid Injection - Kenalog PLUS OFFICE VISIT', 'volume': 350, 'variable_cost_per_unit': 14},
    {'service_name': 'Hep A', 'volume': 200, 'variable_cost_per_unit': 6},
    {'service_name': 'Hep B', 'volume': 220, 'variable_cost_per_unit': 6},
    {'service_name': 'HIB', 'volume': 180, 'variable_cost_per_unit': 5},
    {'service_name': 'HPV', 'volume': 140, 'variable_cost_per_unit': 8},
    {'service_name': 'Influenza/Flu', 'volume': 700, 'variable_cost_per_unit': 4},
    {'service_name': 'Child Flu', 'volume': 500, 'variable_cost_per_unit': 3},
    {'service_name': 'Pneumovax', 'volume': 150, 'variable_cost_per_unit': 10},
    {'service_name': 'Prevnar 13', 'volume': 120, 'variable_cost_per_unit': 9},
    {'service_name': 'Adult Menactra', 'volume': 100, 'variable_cost_per_unit': 8},
    {'service_name': 'MMR', 'volume': 200, 'variable_cost_per_unit': 6},
    {'service_name': 'TD-Tetanus', 'volume': 250, 'variable_cost_per_unit': 5},
    {'service_name': 'Adult TDAP (Boostrix)', 'volume': 230, 'variable_cost_per_unit': 7},
    {'service_name': 'Polio/PV', 'volume': 180, 'variable_cost_per_unit': 6},
    {'service_name': 'TB', 'volume': 400, 'variable_cost_per_unit': 5},
    {'service_name': 'Adult Varicella', 'volume': 170, 'variable_cost_per_unit': 9},
    {'service_name': 'B-12', 'volume': 200, 'variable_cost_per_unit': 4},
    {'service_name': 'Wedge Toe nail removal (Global 10 days)', 'volume': 120, 'variable_cost_per_unit': 10},
    {'service_name': 'Toe Nail Removal', 'volume': 130, 'variable_cost_per_unit': 9},
    {'service_name': 'Endometrial Biopsy (Same Day) Add-on cost', 'volume': 90, 'variable_cost_per_unit': 8},
    {'service_name': 'Endometrial Biopsy (Follow-up visit)', 'volume': 80, 'variable_cost_per_unit': 7},
    {'service_name': 'Ear Lavage', 'volume': 300, 'variable_cost_per_unit': 5},
    {'service_name': 'PT/INR - outside the 14 day window', 'volume': 150, 'variable_cost_per_unit': 6}
]

# Sliding Fee Schedule with service-specific prices (from the image)
sliding_fee_schedule = {
    'UPFH Medical Fee': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 45, 'percentage': 0.15},
        'Slide C': {'price': 60, 'percentage': 0.25},
        'Slide D': {'price': 70, 'percentage': 0.20},
        'Slide E': {'price': 80, 'percentage': 0.15},
        'Full Charges': {'price': 80, 'percentage': 0.15}
    },
    'UPFH Counseling': {
        'Slide A': {'price': 20, 'percentage': 0.10},
        'Slide B': {'price': 25, 'percentage': 0.15},
        'Slide C': {'price': 35, 'percentage': 0.25},
        'Slide D': {'price': 40, 'percentage': 0.20},
        'Slide E': {'price': 50, 'percentage': 0.15},
        'Full Charges': {'price': 50, 'percentage': 0.15}
    },
    'UPFH Group Counseling': {
        'Slide A': {'price': 10, 'percentage': 0.10},
        'Slide B': {'price': 15, 'percentage': 0.15},
        'Slide C': {'price': 20, 'percentage': 0.25},
        'Slide D': {'price': 25, 'percentage': 0.20},
        'Slide E': {'price': 30, 'percentage': 0.15},
        'Full Charges': {'price': 30, 'percentage': 0.15}
    },
    'UPFH Psychiatric Services': {
        'Slide A': {'price': 40, 'percentage': 0.10},
        'Slide B': {'price': 50, 'percentage': 0.15},
        'Slide C': {'price': 60, 'percentage': 0.25},
        'Slide D': {'price': 70, 'percentage': 0.20},
        'Slide E': {'price': 80, 'percentage': 0.15},
        'Full Charges': {'price': 80, 'percentage': 0.15}
    },
    'MOBILE Medical *fees waived utilizing state & local grants': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 45, 'percentage': 0.15},
        'Slide C': {'price': 60, 'percentage': 0.25},
        'Slide D': {'price': 70, 'percentage': 0.20},
        'Slide E': {'price': 80, 'percentage': 0.15},
        'Full Charges': {'price': 80, 'percentage': 0.15}
    },
    'Inhouse Vision Exam': {
        'Slide A': {'price': 20, 'percentage': 0.10},
        'Slide B': {'price': 30, 'percentage': 0.15},
        'Slide C': {'price': 40, 'percentage': 0.25},
        'Slide D': {'price': 50, 'percentage': 0.20},
        'Slide E': {'price': 70, 'percentage': 0.15},
        'Full Charges': {'price': 70, 'percentage': 0.15}
    },
    'Replacement Glasses': {
        'Slide A': {'price': 5, 'percentage': 0.10},
        'Slide B': {'price': 8, 'percentage': 0.15},
        'Slide C': {'price': 11, 'percentage': 0.25},
        'Slide D': {'price': 14, 'percentage': 0.20},
        'Slide E': {'price': 17, 'percentage': 0.15},
        'Full Charges': {'price': 17, 'percentage': 0.15}
    },
    'MOBILE EYE Exam': {
        'Slide A': {'price': 5, 'percentage': 0.10},
        'Slide B': {'price': 7, 'percentage': 0.15},
        'Slide C': {'price': 8, 'percentage': 0.25},
        'Slide D': {'price': 10, 'percentage': 0.20},
        'Slide E': {'price': 15, 'percentage': 0.15},
        'Full Charges': {'price': 15, 'percentage': 0.15}
    },
    'MOBILE EYE - Single Lens Glasses': {
        'Slide A': {'price': 20, 'percentage': 0.10},
        'Slide B': {'price': 30, 'percentage': 0.15},
        'Slide C': {'price': 40, 'percentage': 0.25},
        'Slide D': {'price': 50, 'percentage': 0.20},
        'Slide E': {'price': 60, 'percentage': 0.15},
        'Full Charges': {'price': 60, 'percentage': 0.15}
    },
    'MOBILE EYE - Bifocal Lens Glasses': {
        'Slide A': {'price': 30, 'percentage': 0.10},
        'Slide B': {'price': 35, 'percentage': 0.15},
        'Slide C': {'price': 45, 'percentage': 0.25},
        'Slide D': {'price': 55, 'percentage': 0.20},
        'Slide E': {'price': 65, 'percentage': 0.15},
        'Full Charges': {'price': 65, 'percentage': 0.15}
    },
    'MVHC Pharmacy Fill Fee': {
        'Slide A': {'price': 3, 'percentage': 0.10},
        'Slide B': {'price': 5, 'percentage': 0.15},
        'Slide C': {'price': 7, 'percentage': 0.25},
        'Slide D': {'price': 8, 'percentage': 0.20},
        'Slide E': {'price': 9, 'percentage': 0.15},
        'Full Charges': {'price': 9, 'percentage': 0.15}
    },
    'MA Visit - Labs outside of 7 day global': {
        'Slide A': {'price': 20, 'percentage': 0.10},
        'Slide B': {'price': 25, 'percentage': 0.15},
        'Slide C': {'price': 30, 'percentage': 0.25},
        'Slide D': {'price': 30, 'percentage': 0.20},
        'Slide E': {'price': 35, 'percentage': 0.15},
        'Full Charges': {'price': 35, 'percentage': 0.15}
    },
    'MA Visit - VACCINES': {
        'Slide A': {'price': 20, 'percentage': 0.10},
        'Slide B': {'price': 20, 'percentage': 0.15},
        'Slide C': {'price': 20, 'percentage': 0.25},
        'Slide D': {'price': 20, 'percentage': 0.20},
        'Slide E': {'price': 20, 'percentage': 0.15},
        'Full Charges': {'price': 20, 'percentage': 0.15}
    },
    'Nuvaring': {
        'Slide A': {'price': 5, 'percentage': 0.10},
        'Slide B': {'price': 6, 'percentage': 0.15},
        'Slide C': {'price': 7, 'percentage': 0.25},
        'Slide D': {'price': 8, 'percentage': 0.20},
        'Slide E': {'price': 30, 'percentage': 0.15},
        'Full Charges': {'price': 30, 'percentage': 0.15}
    },
    'Sprintec': {
        'Slide A': {'price': 5, 'percentage': 0.10},
        'Slide B': {'price': 7, 'percentage': 0.15},
        'Slide C': {'price': 15, 'percentage': 0.25},
        'Slide D': {'price': 20, 'percentage': 0.20},
        'Slide E': {'price': 25, 'percentage': 0.15},
        'Full Charges': {'price': 25, 'percentage': 0.15}
    },
    'Loestrin': {
        'Slide A': {'price': 10, 'percentage': 0.10},
        'Slide B': {'price': 11, 'percentage': 0.15},
        'Slide C': {'price': 20, 'percentage': 0.25},
        'Slide D': {'price': 25, 'percentage': 0.20},
        'Slide E': {'price': 30, 'percentage': 0.15},
        'Full Charges': {'price': 30, 'percentage': 0.15}
    },
    'Ella': {
        'Slide A': {'price': 10, 'percentage': 0.10},
        'Slide B': {'price': 11, 'percentage': 0.15},
        'Slide C': {'price': 25, 'percentage': 0.25},
        'Slide D': {'price': 30, 'percentage': 0.20},
        'Slide E': {'price': 35, 'percentage': 0.15},
        'Full Charges': {'price': 35, 'percentage': 0.15}
    },
    'Depo-Provera': {
        'Slide A': {'price': 15, 'percentage': 0.10},
        'Slide B': {'price': 20, 'percentage': 0.15},
        'Slide C': {'price': 25, 'percentage': 0.25},
        'Slide D': {'price': 30, 'percentage': 0.20},
        'Slide E': {'price': 35, 'percentage': 0.15},
        'Full Charges': {'price': 35, 'percentage': 0.15}
    },
    'Nexplanon': {
        'Slide A': {'price': 50, 'percentage': 0.10},
        'Slide B': {'price': 60, 'percentage': 0.15},
        'Slide C': {'price': 100, 'percentage': 0.25},
        'Slide D': {'price': 125, 'percentage': 0.20},
        'Slide E': {'price': 150, 'percentage': 0.15},
        'Full Charges': {'price': 150, 'percentage': 0.15}
    },
    'Mirena': {
        'Slide A': {'price': 75, 'percentage': 0.10},
        'Slide B': {'price': 85, 'percentage': 0.15},
        'Slide C': {'price': 150, 'percentage': 0.25},
        'Slide D': {'price': 175, 'percentage': 0.20},
        'Slide E': {'price': 200, 'percentage': 0.15},
        'Full Charges': {'price': 200, 'percentage': 0.15}
    },
    'Liletta': {
        'Slide A': {'price': 75, 'percentage': 0.10},
        'Slide B': {'price': 85, 'percentage': 0.15},
        'Slide C': {'price': 150, 'percentage': 0.25},
        'Slide D': {'price': 175, 'percentage': 0.20},
        'Slide E': {'price': 200, 'percentage': 0.15},
        'Full Charges': {'price': 200, 'percentage': 0.15}
    },
    'Paragard (limited supply)': {
        'Slide A': {'price': 75, 'percentage': 0.10},
        'Slide B': {'price': 85, 'percentage': 0.15},
        'Slide C': {'price': 150, 'percentage': 0.25},
        'Slide D': {'price': 175, 'percentage': 0.20},
        'Slide E': {'price': 200, 'percentage': 0.15},
        'Full Charges': {'price': 200, 'percentage': 0.15}
    },
    'IUD Removal Fee': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 45, 'percentage': 0.15},
        'Slide C': {'price': 50, 'percentage': 0.25},
        'Slide D': {'price': 55, 'percentage': 0.20},
        'Slide E': {'price': 60, 'percentage': 0.15},
        'Full Charges': {'price': 60, 'percentage': 0.15}
    },
    'Implanon Removal': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 45, 'percentage': 0.15},
        'Slide C': {'price': 50, 'percentage': 0.25},
        'Slide D': {'price': 55, 'percentage': 0.20},
        'Slide E': {'price': 60, 'percentage': 0.15},
        'Full Charges': {'price': 60, 'percentage': 0.15}
    },
    'Vaccine Administration Fee': {
        'Slide A': {'price': 3, 'percentage': 0.10},
        'Slide B': {'price': 4, 'percentage': 0.15},
        'Slide C': {'price': 6, 'percentage': 0.25},
        'Slide D': {'price': 7, 'percentage': 0.20},
        'Slide E': {'price': 8, 'percentage': 0.15},
        'Full Charges': {'price': 8, 'percentage': 0.15}
    },
    'STD Testing PLUS OFFICE VISIT': {
        'Slide A': {'price': 85, 'percentage': 0.10},
        'Slide B': {'price': 86, 'percentage': 0.15},
        'Slide C': {'price': 87, 'percentage': 0.25},
        'Slide D': {'price': 88, 'percentage': 0.20},
        'Slide E': {'price': 89, 'percentage': 0.15},
        'Full Charges': {'price': 89, 'percentage': 0.15}
    },
    'Steroid Injection - Kenalog PLUS OFFICE VISIT': {
        'Slide A': {'price': 20, 'percentage': 0.10},
        'Slide B': {'price': 25, 'percentage': 0.15},
        'Slide C': {'price': 30, 'percentage': 0.25},
        'Slide D': {'price': 35, 'percentage': 0.20},
        'Slide E': {'price': 40, 'percentage': 0.15},
        'Full Charges': {'price': 40, 'percentage': 0.15}
    },
    'Hep A': {
        'Slide A': {'price': 45, 'percentage': 0.10},
        'Slide B': {'price': 46, 'percentage': 0.15},
        'Slide C': {'price': 47, 'percentage': 0.25},
        'Slide D': {'price': 48, 'percentage': 0.20},
        'Slide E': {'price': 49, 'percentage': 0.15},
        'Full Charges': {'price': 49, 'percentage': 0.15}
    },
    'Hep B': {
        'Slide A': {'price': 30, 'percentage': 0.10},
        'Slide B': {'price': 31, 'percentage': 0.15},
        'Slide C': {'price': 32, 'percentage': 0.25},
        'Slide D': {'price': 33, 'percentage': 0.20},
        'Slide E': {'price': 34, 'percentage': 0.15},
        'Full Charges': {'price': 34, 'percentage': 0.15}
    },
    'HIB': {
        'Slide A': {'price': 30, 'percentage': 0.10},
        'Slide B': {'price': 31, 'percentage': 0.15},
        'Slide C': {'price': 32, 'percentage': 0.25},
        'Slide D': {'price': 33, 'percentage': 0.20},
        'Slide E': {'price': 34, 'percentage': 0.15},
        'Full Charges': {'price': 34, 'percentage': 0.15}
    },
    'HPV': {
        'Slide A': {'price': 330, 'percentage': 0.10},
        'Slide B': {'price': 335, 'percentage': 0.15},
        'Slide C': {'price': 335, 'percentage': 0.25},
        'Slide D': {'price': 335, 'percentage': 0.20},
        'Slide E': {'price': 335, 'percentage': 0.15},
        'Full Charges': {'price': 335, 'percentage': 0.15}
    },
    'Influenza/Flu': {
        'Slide A': {'price': 18, 'percentage': 0.10},
        'Slide B': {'price': 19, 'percentage': 0.15},
        'Slide C': {'price': 20, 'percentage': 0.25},
        'Slide D': {'price': 21, 'percentage': 0.20},
        'Slide E': {'price': 22, 'percentage': 0.15},
        'Full Charges': {'price': 22, 'percentage': 0.15}
    },
    'Child Flu': {
        'Slide A': {'price': 18, 'percentage': 0.10},
        'Slide B': {'price': 19, 'percentage': 0.15},
        'Slide C': {'price': 20, 'percentage': 0.25},
        'Slide D': {'price': 21, 'percentage': 0.20},
        'Slide E': {'price': 22, 'percentage': 0.15},
        'Full Charges': {'price': 22, 'percentage': 0.15}
    },
    'Pneumovax': {
        'Slide A': {'price': 106, 'percentage': 0.10},
        'Slide B': {'price': 107, 'percentage': 0.15},
        'Slide C': {'price': 108, 'percentage': 0.25},
        'Slide D': {'price': 109, 'percentage': 0.20},
        'Slide E': {'price': 110, 'percentage': 0.15},
        'Full Charges': {'price': 110, 'percentage': 0.15}
    },
    'Prevnar 13': {
        'Slide A': {'price': 190, 'percentage': 0.10},
        'Slide B': {'price': 191, 'percentage': 0.15},
        'Slide C': {'price': 192, 'percentage': 0.25},
        'Slide D': {'price': 193, 'percentage': 0.20},
        'Slide E': {'price': 194, 'percentage': 0.15},
        'Full Charges': {'price': 194, 'percentage': 0.15}
    },
    'Adult Menactra': {
        'Slide A': {'price': 120, 'percentage': 0.10},
        'Slide B': {'price': 121, 'percentage': 0.15},
        'Slide C': {'price': 122, 'percentage': 0.25},
        'Slide D': {'price': 123, 'percentage': 0.20},
        'Slide E': {'price': 124, 'percentage': 0.15},
        'Full Charges': {'price': 124, 'percentage': 0.15}
    },
    'MMR': {
        'Slide A': {'price': 75, 'percentage': 0.10},
        'Slide B': {'price': 76, 'percentage': 0.15},
        'Slide C': {'price': 77, 'percentage': 0.25},
        'Slide D': {'price': 78, 'percentage': 0.20},
        'Slide E': {'price': 79, 'percentage': 0.15},
        'Full Charges': {'price': 79, 'percentage': 0.15}
    },
    'TD-Tetanus': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 36, 'percentage': 0.15},
        'Slide C': {'price': 37, 'percentage': 0.25},
        'Slide D': {'price': 38, 'percentage': 0.20},
        'Slide E': {'price': 39, 'percentage': 0.15},
        'Full Charges': {'price': 39, 'percentage': 0.15}
    },
    'Adult TDAP (Boostrix)': {
        'Slide A': {'price': 52, 'percentage': 0.10},
        'Slide B': {'price': 53, 'percentage': 0.15},
        'Slide C': {'price': 54, 'percentage': 0.25},
        'Slide D': {'price': 55, 'percentage': 0.20},
        'Slide E': {'price': 56, 'percentage': 0.15},
        'Full Charges': {'price': 56, 'percentage': 0.15}
    },
    'Polio/PV': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 36, 'percentage': 0.15},
        'Slide C': {'price': 37, 'percentage': 0.25},
        'Slide D': {'price': 38, 'percentage': 0.20},
        'Slide E': {'price': 39, 'percentage': 0.15},
        'Full Charges': {'price': 39, 'percentage': 0.15}
    },
    'TB': {
        'Slide A': {'price': 10, 'percentage': 0.10},
        'Slide B': {'price': 11, 'percentage': 0.15},
        'Slide C': {'price': 12, 'percentage': 0.25},
        'Slide D': {'price': 13, 'percentage': 0.20},
        'Slide E': {'price': 14, 'percentage': 0.15},
        'Full Charges': {'price': 14, 'percentage': 0.15}
    },
    'Adult Varicella': {
        'Slide A': {'price': 130, 'percentage': 0.10},
        'Slide B': {'price': 132, 'percentage': 0.15},
        'Slide C': {'price': 134, 'percentage': 0.25},
        'Slide D': {'price': 133, 'percentage': 0.20},
        'Slide E': {'price': 134, 'percentage': 0.15},
        'Full Charges': {'price': 134, 'percentage': 0.15}
    },
    'B-12': {
        'Slide A': {'price': 15, 'percentage': 0.10},
        'Slide B': {'price': 16, 'percentage': 0.15},
        'Slide C': {'price': 17, 'percentage': 0.25},
        'Slide D': {'price': 18, 'percentage': 0.20},
        'Slide E': {'price': 20, 'percentage': 0.15},
        'Full Charges': {'price': 20, 'percentage': 0.15}
    },
    'Wedge Toe nail removal (Global 10 days)': {
        'Slide A': {'price': 75, 'percentage': 0.10},
        'Slide B': {'price': 85, 'percentage': 0.15},
        'Slide C': {'price': 150, 'percentage': 0.25},
        'Slide D': {'price': 175, 'percentage': 0.20},
        'Slide E': {'price': 200, 'percentage': 0.15},
        'Full Charges': {'price': 200, 'percentage': 0.15}
    },
    'Toe Nail Removal': {
        'Slide A': {'price': 100, 'percentage': 0.10},
        'Slide B': {'price': 105, 'percentage': 0.15},
        'Slide C': {'price': 110, 'percentage': 0.25},
        'Slide D': {'price': 115, 'percentage': 0.20},
        'Slide E': {'price': 120, 'percentage': 0.15},
        'Full Charges': {'price': 120, 'percentage': 0.15}
    },
    'Endometrial Biopsy (Same Day) Add-on cost': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 45, 'percentage': 0.15},
        'Slide C': {'price': 60, 'percentage': 0.25},
        'Slide D': {'price': 70, 'percentage': 0.20},
        'Slide E': {'price': 80, 'percentage': 0.15},
        'Full Charges': {'price': 80, 'percentage': 0.15}
    },
    'Endometrial Biopsy (Follow-up visit)': {
        'Slide A': {'price': 35, 'percentage': 0.10},
        'Slide B': {'price': 45, 'percentage': 0.15},
        'Slide C': {'price': 60, 'percentage': 0.25},
        'Slide D': {'price': 70, 'percentage': 0.20},
        'Slide E': {'price': 80, 'percentage': 0.15},
        'Full Charges': {'price': 80, 'percentage': 0.15}
    },
    'Ear Lavage': {
        'Slide A': {'price': 15, 'percentage': 0.10},
        'Slide B': {'price': 16, 'percentage': 0.15},
        'Slide C': {'price': 17, 'percentage': 0.25},
        'Slide D': {'price': 18, 'percentage': 0.20},
        'Slide E': {'price': 20, 'percentage': 0.15},
        'Full Charges': {'price': 20, 'percentage': 0.15}
    },
    'PT/INR - outside the 14 day window': {
        'Slide A': {'price': 15, 'percentage': 0.10},
        'Slide B': {'price': 16, 'percentage': 0.15},
        'Slide C': {'price': 17, 'percentage': 0.25},
        'Slide D': {'price': 18, 'percentage': 0.20},
        'Slide E': {'price': 20, 'percentage': 0.15},
        'Full Charges': {'price': 20, 'percentage': 0.15}
    }
}

# Fixed Costs
fixed_costs = 60000

## Show Results
results_df = cvp_analysis_with_full_sliding_fee(services, sliding_fee_schedule, fixed_costs)
results_df.head()

## Graph Results
plot_profit_per_product(results_df)