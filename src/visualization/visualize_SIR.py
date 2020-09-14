import pandas as pd
import numpy as np

import dash
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

import plotly.graph_objects as go

import os
print(os.getcwd())

#SIR=np.array([S0,I0,R0])

df_input_large=pd.read_csv('../data/processed/COVID_final_set.csv',sep=';')


fig = go.Figure()

app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''
    #  Susceptible-Infected-Recovered (SIR) - Dynamic dashboard

    The main goal of this dashboard is to enable the user to visualize the implementation of SIR model,
    and the provide options to user to modify the initial time period, time period for introducing measures,
    holding time period after measures and relaxing time period. Also the minimum and maximum infection rate and
    recovery rate of a particular country can be modified. S,I,R curve can be fitted individually by adjusting
    these parameters and cofirmed cases also included in the figure for easy understanding.

    ## Assumptions:
    a) The population of the country is not available in the John-Hopkins data. Globally 3-4% popupation
    of a country is affected by COVID 19. This will help in visualize the dashboard
    ##
    b)Starting value of minimum infected people is set to 35 to have smooth curve

    '''),

    dcc.Markdown('''
    ## Multi-Select Country for visualization
    '''),

    dcc.Dropdown(
        id='country_drop_down',
        options=[ {'label': each,'value':each} for each in df_input_large['country'].unique()],
        value=['US'], # which are pre-selected
        multi=True
    ),

    dcc.Markdown('''
        ## SIR Parameters
        '''),

    dcc.Markdown('''
    ##
    ## Initial period----------------------Measures Introduced----------Hold Period----------------------Relaxation period
    '''),
    dcc.Input(
            id="t_initial", type="number", placeholder="number",
            value=21,min=0, max=10000,
            step=1,debounce=True,style = dict(
            width = '20%',
            display = 'table-cell'  ),
    ),

    dcc.Input(
            id="t_intro_measures", type="number", placeholder="number",
            value=14,min=0, max=10000,
            step=1,debounce=True,style = dict(
            width = '20%',
            display = 'table-cell'  ),
    ),

    dcc.Input(
            id="t_hold", type="number", placeholder="number",
            value=21,min=0, max=10000,
            step=1,debounce=True,style = dict(
            width = '20%',
            display = 'table-cell' ),
    ),

    dcc.Input(
            id="t_relax", type="number", placeholder="number",
            value=21,min=0, max=10000,
            step=1,debounce=True,style = dict(
            width = '20%',
            display = 'table-cell'),

    ),

     dcc.Markdown('''
    ## Maximum infection rate---------Maximum infection rate--------Recovery Rate
    '''),
     dcc.Input(
             id="beta_max", type="number", placeholder="number",
             value=0.4,min=0, max=100,
             debounce=True,
             style = dict(
            width = '20%',
            display = 'table-cell',
            ),

    ),
     dcc.Input(
             id="beta_min", type="number", placeholder="number",
             value=0.11,min=0, max=100,
             debounce=True,style = dict(
            width = '20%',
            display = 'table-cell',
            ),
    ),
     dcc.Input(
             id="gamma", type="number", placeholder="number",
             value=0.1,min=0, max=100,
             debounce=True,style = dict(
            width = '20%',
            display = 'table-cell',
            ),
    ),
      dcc.Markdown('''
    ## Susceptible-Infected-Recovered (SIR) Dropdown
    '''),
    dcc.Dropdown(
        id='SIR_drop_down',
        options=[{'label': 'Susceptible','value':'susceptible'},
                 {'label': 'Infected','value':'infected'},
                 {'label': 'Recovered','value':'recovered'}

                ],
        value=('infected'), # which are pre-selected
        multi=False
    ),

    dcc.Graph(figure=fig, id='main_window_slope')
]
    )


@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('country_drop_down', 'value'),
    Input('t_initial', component_property='value'),
    Input('t_intro_measures',component_property= 'value'),
    Input('t_hold',component_property= 'value'),
    Input('t_relax',component_property= 'value'),
    Input('beta_max',component_property= 'value'),
    Input('beta_min', component_property='value'),
    Input('gamma', component_property='value'),
    Input('SIR_drop_down', 'value')]
)

def update_figure(country_list,t_init,t_intro,t_hold,t_relax,bmax,bmin,gamma,SIR_list):

    traces =[]

    print(gamma)
    print(SIR_list)

    for each in country_list:

        df_plot=df_input_large[df_input_large['country']==each]
        df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.mean).reset_index()
        df_plot=df_plot['confirmed'][df_plot['confirmed']>35].reset_index(drop=True)


        ydata=df_plot
        xdata= np.arange(len(df_plot))

        traces.append(dict(
                                x=xdata,
                                y=ydata,
                                type='bar',
                                opacity=0.9,
                                visible=True,
                                name=each+'_Confirmed'
                          )
                     )

        pd_beta=np.concatenate((np.array(t_init*[bmax]),
                               np.linspace(bmax,bmin,t_intro),
                               np.array(t_hold*[bmin]),
                               np.linspace(bmin,bmax,t_relax),
                               ))

        I0=df_plot[0]
        N0=np.array(df_plot)[-1]/0.04
        S0=N0-I0
        R0=0


        SIR=np.array([S0,I0,R0])


        propagation_rates=pd.DataFrame(columns={'susceptible':S0,
                                            'infected':I0,
                                            'recoverd':R0})

        for each_beta in pd_beta:

            new_delta_vec=SIR_model(SIR,each_beta,gamma,N0)

            SIR=SIR+new_delta_vec

            propagation_rates=propagation_rates.append({'susceptible':SIR[0],
                                                        'infected':SIR[1],
                                                        'recovered':SIR[2]}, ignore_index=True)


        traces.append(dict(
                                x=propagation_rates.index,
                                y=propagation_rates[SIR_list],
                                mode='markers+lines',
                                legend_title="Legend Title",
                                opacity=0.9,
                                visible=True,
                                name=each+'_'+SIR_list+'(SIR)'

                          )
                     )



    return {
                        'data': traces,
                        'layout': dict (
                            width=1280,
                            height=720,
                            title= 'Scenario SIR simulations ',

                            xaxis={'title':'Time in days',
                                    'tickfont':dict(size=14,color="#7f7f7f"),
                                  },
                             yaxis={'title':'Confirmed infected people (Source: John Hopkins,log-scale)',
                                    'tickfont':dict(size=14,color="#7f7f7f"),
                                    'type':"log"
                                  },
                            updatemenus=[
                                dict(
                                    type="buttons",
                                    direction="right",
                                    buttons=list([
                                        dict(
                                            args=[{'yaxis.type': 'log'}],
                                            label="Log Scale",
                                            method="relayout"
                                            ),
                                        dict(
                                            args=[{'yaxis.type': 'Linear'}],
                                            label="Linear Scale",
                                            method="relayout"
                                            )],
                                        )
                                    )
                                ],
                            shapes= [
                                    {
                                'type': "rect",
                                'x0': 0,'x1': t_init,
                                'y0': 1,'y1': N0,
                                'fillcolor':'PaleTurquoise','opacity':0.3,
                                'line': {'width': 2,'color': 'RoyalBlue'},
                                    },
                                     {
                                'type': "rect",
                                'x0': t_init,'x1': t_init+t_intro,
                                'y0': 1,'y1': N0,
                                'fillcolor':'PaleTurquoise','opacity':0.3,
                                'line': {'width': 2,'color': 'MediumPurple'},
                                     },
                                {
                                'type': "rect",
                                'x0': t_init+t_intro,'x1': t_init+t_intro+t_hold,
                                'y0': 1,'y1': N0,
                                'fillcolor':'PaleTurquoise','opacity':0.3,
                                'line': {'width': 2,'color': 'Crimson'},
                                     },
                                {
                                'type': "rect",
                                'x0': t_init+t_intro+t_hold,'x1': t_init+t_intro+t_hold+t_relax,
                                'y0': 1,'y1': N0,
                                'fillcolor':'PaleTurquoise','opacity':0.3,
                                'line': {'width': 2,'color': 'LightSeaGreen'},
                                     },

                                    ],

                            )


        }



if __name__ == '__main__':

    app.run_server(debug=True, use_reloader=False)
