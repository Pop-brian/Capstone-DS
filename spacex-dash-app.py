# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# --- Start of Task 1 Specifics: Prepare Dropdown Options ---
# Get unique launch site names from the DataFrame
launch_sites = spacex_df['Launch Site'].unique()

# Create the options list for the dropdown, including the 'All Sites' option
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})
# --- End of Task 1 Specifics ---

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,  # Use the dynamically generated options
        value='ALL',               # Default value to 'ALL'
        placeholder="Select a Launch Site here", # Placeholder text
        searchable=True            # Enable search functionality
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000, # Min, Max, and Step values as specified
        marks={i: str(i) for i in range(0, 10001, 1000)}, # Generate marks from 0 to 10000 with 1000 intervals
        value=[min_payload, max_payload] # Initial range set to min and max payload from data
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2: Add a callback function to render success-pie-chart based on selected site dropdown
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # If 'ALL' sites are selected, calculate total success launches for all sites
        # 'class' column indicates success (1) or failure (0)
        fig = px.pie(spacex_df,
                     values='class',
                     names='Launch Site', # Group by Launch Site to show total success by site
                     title='Total Success Launches By Site (All Sites)')
        return fig
    else:
        # If a specific launch site is selected, filter the dataframe
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success (1) vs failed (0) launches for the selected site
        # Use value_counts() to get counts of 0 and 1 in 'class' column
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count'] # Rename columns for plotly
        
        fig = px.pie(success_counts,
                     values='count',
                     names='class', # Names will be 0 (Failed) and 1 (Success)
                     title=f'Total Success vs. Failed Launches for {entered_site}',
                     color='class', # Assign colors based on 'class'
                     color_discrete_map={0: 'red', 1: 'green'} # Optional: custom colors
                    )
        return fig


# TASK 4: Add a callback function to render the success-payload-scatter-chart scatter plot
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    # Filter the DataFrame based on the selected payload range
    low, high = payload_range
    # Ensure 'Payload Mass (kg)' is between the selected range
    filtered_payload_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site == 'ALL':
        # If 'ALL' sites are selected, show scatter plot for all data within payload range
        fig = px.scatter(filtered_payload_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category', # Color points by Booster Version
                         title='Correlation between Payload and Success for All Sites')
        return fig
    else:
        # If a specific launch site is selected, filter by site AND payload range
        filtered_site_payload_df = filtered_payload_df[
            filtered_payload_df['Launch Site'] == entered_site
        ]
        fig = px.scatter(filtered_site_payload_df,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category', # Color points by Booster Version
                         title=f'Correlation between Payload and Success for {entered_site}')
        return fig


# Run the app
if __name__ == '__main__':
    app.run( debug=True, port=8051) # Use debug=True for easier development and auto-reloading
