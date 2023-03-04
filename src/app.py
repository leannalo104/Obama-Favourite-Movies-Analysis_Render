#import libraries
from dash import Dash, html, dcc, Input, Output
from jupyter_dash import JupyterDash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc 
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns
import plotly.graph_objects as go



#import df
df_=pd.read_csv('finaldf_2023',index_col=0)
df_.head()

#Initialize Dash and style sheet
app=Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

year_dropdown = dcc.Dropdown(options=df_['year'].unique(),
                            value='2022')


#Customize your own Layout
app.layout = dbc.Container([
    html.H1("Obama's Favourite Movies Dashboard",style={'textAlign':'center'},className="fw-bold"), #header
    html.Hr(), 
    dbc.Row([
        dbc.Col(year_dropdown) #dropdown menu
    ],className='mb-3'),
    dbc.CardGroup(
        [dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Number of Movies", className="card-title"),
                    html.H4(id='total_movies', children="000"),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Average Critic Score", className="card-title"),
                    html.H4(id='avg_critic_score', children="000"),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Top 3 Movies (Critic Score)", className="card-title"),
                    html.H4(id='top3_score', children="000"),
                ]
            )
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H6("Top 3 Movies (Box Office)", className="card-title"),
                    html.H4(id='top3_boxoffice', children="000"),
                ]
            )
        ),
    ],className='mb-2'
),
    dbc.Row([ #row with bubble chart
        dbc.Col(dcc.Graph(id='graph_a')),
    ]),
    dbc.Row([ #row with two charts
       dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graph_b', figure={}, config={'displayModeBar': False}),
                ])
            ], color="light", outline=True),
        ], width=7),       
       dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='graph_c', figure={}, config={'displayModeBar': False}),
                ])
            ], color="light", outline=True),
        ], width=4),
    ],className='mb-4'), 
    html.H6("Powered by Plotly, Dash, and Python",style={'textAlign':'left'}),
    html.H6("Prepared in 2023 by Leanna Lo",style={'textAlign':'left'}),
], fluid=True)

@app.callback(
    Output(component_id='total_movies', component_property='children'),
    Output(component_id='avg_critic_score', component_property='children'),
    Output(component_id='top3_score', component_property='children'),
    Output(component_id='top3_boxoffice', component_property='children'),
    Input(component_id=year_dropdown, component_property='value'))
    
def update_cards(selected_year):
    filtered_movie = df_[df_['year'] == selected_year]
    totalmovies=len(filtered_movie)
    avgcriticscore=round(filtered_movie['tomatometerscore'].mean(),1)
    top3scorelist=list(filtered_movie.sort_values(by=['tomatometerscore'],ascending=False).head(3)['movies'])
    top3score = [html.Li(x) for x in top3scorelist]
    top3boxofficelist=list(filtered_movie.sort_values(by=['boxofficegross_inM'],ascending=False).head(3)['movies'])
    top3boxoffice= [html.Li(x) for x in top3boxofficelist]
    return totalmovies, avgcriticscore, top3score, top3boxoffice
    


@app.callback(
    Output(component_id='graph_a', component_property='figure'),
    Input(component_id=year_dropdown, component_property='value'))
                      
def update_graph(selected_year):
    filtered_movie = df_[df_['year'] == selected_year]
    fig = px.scatter(filtered_movie, x="release_month_theaters", 
                     y="tomatometerscore", 
                     size="boxofficegross",
                     color="genre0", 
                     hover_name="movies",hover_data={'year': False, 
                                                            'release_month_theaters': False,
                                                            'boxofficegross':False,
                                                            'genre0':False,
                                                           'director0':True,
                                                           'boxofficegross_inM':':.1f'},
                     title='Release Date & Box Office Gross',
                     labels={'tomatometerscore':'Critic score',
                                    'genre0':'Genre',
                                    'movies':'movie',
                                    'release_month_theaters':'Release month',
                                   'audiencescore':'Audience score',
                                   'director0':'Director',
                                   'boxofficegross_inM':'Box Office Gross'},
                                size_max=55, range_y=[70,110])
    fig.update_layout(
        title_x=0.5,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1))
    return fig

@app.callback(
    Output(component_id='graph_b', component_property='figure'),
    Input(component_id=year_dropdown, component_property='value'))

def update_graph_b(selected_year):
    filtered_movie = df_[df_['year'] == selected_year]
    desired_order = filtered_movie.sort_values('tomatometerscore',ascending=False)['movies'].to_list()
    figb = go.Figure(
        data=[
            go.Bar(name='Critic Score', x=filtered_movie['movies'], y=filtered_movie['tomatometerscore']),
            go.Bar(name='Audience Score', x=filtered_movie['movies'], y=filtered_movie['audiencescore'])
        ])
    figb.update_layout(barmode='group',
                 title='Critic Score vs Audience Score',title_x=0.5)
    figb.update_yaxes(range=[60, 100])
    figb.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1))
    figb.update_xaxes(categoryorder='array', categoryarray= desired_order)   
    return figb

@app.callback(
    Output(component_id='graph_c', component_property='figure'),
    Input(component_id=year_dropdown, component_property='value'))
    
def update_graph_c(selected_year):
    filtered_movie = df_[df_['year'] == selected_year]
    langdf = filtered_movie.groupby('orig_lang').count()[['movies']].reset_index()
    figc = px.pie(langdf, values='movies', names='orig_lang',
             title='Movies by Original Language',
                 hover_data={'orig_lang': False})
    figc.update_traces(textposition='inside', textinfo='percent+label')
    figc.update_layout(showlegend=False,title_x=0.5)
    return figc

if __name__ == '__main__':
     app.run_server(debug=True) #debug=True refreshes app when changes made
