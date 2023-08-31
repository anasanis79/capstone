# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites_list = spacex_df.groupby(['Launch Site'], as_index=False).first()['Launch Site'].to_list()
launch_site_dicts = [{'label': 'All', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites_list]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=launch_site_dicts,
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=500,
                                                marks={val: str(val) for val in range(0, 10000, 500)},
                                                value=[min_payload, max_payload]),
                                                
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', names='Launch Site', title='Success Rate of All Launch Sites')
        return fig
    else:
        data_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        data_df = data_df.groupby(['Launch Site', 'class']).size().reset_index(name='class count')
        fig = px.pie(data_df, values='class count', names='class', title='Total Success Launched for site: ' + entered_site)
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload):
    low, high = payload
    data_df = spacex_df[(spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)]       
    if entered_site == 'ALL':
        fig = px.scatter(data_df, x='Payload Mass (kg)', y='class', 
        color='Booster Version Category',
        title='Success rate depending on Payload for all Sites')
        return fig
    else:
        fig = px.scatter(data_df[data_df['Launch Site'] == entered_site],
        x='Payload Mass (kg)', y='class',
        color='Booster Version Category',
        title='Success rate depending on Payload for Site: ' + entered_site)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
