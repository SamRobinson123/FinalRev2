import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
from Revenue_App.RevenueModel2 import CVP
from Revenue_App.RevenueModel2.CVP import cvp_analysis_with_full_sliding_fee, plot_profit_per_product, services

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Function to create labeled input fields for each service
def create_service_inputs(service):
    return html.Div([
        html.H4(service['service_name']),
        html.Div([
            html.Label("Volume:"),
            dcc.Input(id=f'{service["service_name"]}-volume', type='number', value=service['volume'],
                      placeholder="Volume", style={'width': '80px', 'margin-right': '10px', 'padding': '5px'}),

            html.Label("Variable Cost per Unit:"),
            dcc.Input(id=f'{service["service_name"]}-cost', type='number', value=service['variable_cost_per_unit'],
                      placeholder="Variable Cost", style={'width': '80px', 'margin-right': '10px', 'padding': '5px'})
        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}),

        # Inputs for sliding fee tiers
        html.Label("Sliding Fee Tier Values:"),
        html.Div([
            html.Div([
                html.Label(f'{tier} Price:', style={'width': '100px', 'display': 'inline-block'}),
                dcc.Input(id=f'{service["service_name"]}-{tier}-price', type='number', value=values['price'],
                          placeholder="Price", style={'width': '80px', 'margin-right': '10px', 'padding': '5px'}),
                html.Label(f'{tier} Percentage:', style={'width': '120px', 'display': 'inline-block'}),
                dcc.Input(id=f'{service["service_name"]}-{tier}-percentage', type='number', value=values['percentage'],
                          placeholder="Percentage", style={'width': '80px', 'padding': '5px'})
            ], style={'margin-bottom': '5px'}) for tier, values in CVP.sliding_fee_schedule[service['service_name']].items()
        ])
    ], style={'border': '1px solid #ccc', 'padding': '15px', 'border-radius': '10px', 'margin-bottom': '20px'})


# Create input fields dynamically for each service
service_inputs = []
for service in services:
    service_inputs.append(create_service_inputs(service))

# Layout for the entire app (Inputs, KPI, and Graph on one page)
app.layout = html.Div([
    html.H1("CVP Analysis Dashboard", style={'text-align': 'center'}),

    # Fixed Cost input aligned and positioned better
    html.Div([
        html.Label("Fixed Costs:", style={'margin-right': '10px'}),
        dcc.Input(id='fixed-cost-input', type='number', value=500000, placeholder="Fixed Costs",
                  style={'width': '150px', 'padding': '5px', 'font-size': '16px'}),
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'flex-start', 'margin-bottom': '20px'}),

    # Dynamic inputs for all services
    html.Div(service_inputs,
             style={'max-height': '30vh', 'overflow-y': 'auto', 'border': '1px solid #ccc', 'padding': '15px',
                    'border-radius': '10px', 'margin-left': '50px', 'margin-right': '50px'}),

    # Button to update the graph
    html.Button('Update Graph', id='update-graph-button', n_clicks=0,
                style={'margin-top': '20px', 'display': 'block', 'margin': 'auto'}),

    # KPI for Total Profitability
    html.Div([
        html.H3("Total Profitability:"),
        html.H2(id='total-profitability', style={'color': 'green', 'text-align': 'center', 'font-size': '28px'})
    ], style={'margin-top': '30px', 'text-align': 'center'}),

    # Larger Profit graph
    dcc.Graph(id='profit-graph', style={'height': '60vh', 'width': '80vw', 'margin': 'auto'}),
], style={'position': 'relative', 'padding': '20px'})


# Callback to generate the graph and calculate total profitability
@app.callback(
    [Output('profit-graph', 'figure'),
     Output('total-profitability', 'children')],  # Add output for the total profitability KPI
    [Input('update-graph-button', 'n_clicks')],
    [State(f'{service["service_name"]}-volume', 'value') for service in CVP.services] +
    [State(f'{service["service_name"]}-cost', 'value') for service in CVP.services] +
    [State(f'{service["service_name"]}-{tier}-price', 'value') for service in CVP.services for tier in
     CVP.sliding_fee_schedule[service['service_name']].keys()] +
    [State(f'{service["service_name"]}-{tier}-percentage', 'value') for service in CVP.services for tier in
     CVP.sliding_fee_schedule[service['service_name']].keys()] +
    [State('fixed-cost-input', 'value')]  # Added fixed cost input state
)
def update_graph(n_clicks, *args):
    if n_clicks == 0:
        return dash.no_update, dash.no_update  # Prevent updating the graph and KPI if the button has not been clicked yet

    # Update the services dictionary with new input values (volume, cost, and sliding fees)
    arg_index = 0
    for service in CVP.services:
        service['volume'] = args[arg_index]
        service['variable_cost_per_unit'] = args[len(CVP.services) + arg_index]
        arg_index += 1

    # Update sliding fee schedule with new inputs
    for i, service in enumerate(CVP.services):
        for j, (tier, values) in enumerate(CVP.sliding_fee_schedule[service['service_name']].items()):
            CVP.sliding_fee_schedule[service['service_name']][tier]['price'] = args[
                2 * len(CVP.services) + i * len(CVP.sliding_fee_schedule[service['service_name']]) + j]
            CVP.sliding_fee_schedule[service['service_name']][tier]['percentage'] = args[
                2 * len(CVP.services) + len(CVP.services) * len(
                    CVP.sliding_fee_schedule[service['service_name']]) + i * len(
                    CVP.sliding_fee_schedule[service['service_name']]) + j]

    # Extract the updated fixed cost value
    fixed_costs = args[-1]

    # Recalculate the DataFrame
    results_df = CVP.cvp_analysis_with_full_sliding_fee(CVP.services, CVP.sliding_fee_schedule, fixed_costs)

    # Calculate the total profitability
    total_profitability = results_df['Profit'].sum()

    # Create the bar chart using Plotly Express
    fig = px.bar(results_df, x='Service', y='Profit', title='Profit Per Product (Service)', height=800, width=1500)

    # Return the figure and the total profitability value for the KPI
    return fig, f"${total_profitability:,.2f}"

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)