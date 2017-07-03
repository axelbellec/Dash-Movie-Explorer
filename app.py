import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from get_data import all_movies, variable_labels

df = all_movies.copy()

app = dash.Dash()


app.layout = html.Div([
    html.H1('Movie Explorer'),
    html.H2('Dash: A web application framework for Python.'),
    html.Div([
        html.Label('Minimum number of reviews on Rotten Tomatoes'),
        dcc.Slider(
            id='nb-reviews-slider',
            min=df.Reviews.min(),
            max=df.Reviews.max(),
            marks={str(rvw): str(rvw) for rvw in range(int(df.Reviews.min()), len(df.Reviews.unique()), 30)},
            value=df.Reviews.min(),
            step=None
        ),
        html.Br(),
        html.Label('Year released'),
        dcc.Slider(
            id='year-released-slider',
            min=df.Year.min(),
            max=df.Year.max(),
            marks={str(y): str(y) for y in range(int(df.Year.min()), int(df.Year.max()), 5)},
            value=df.Year.min(),
            step=None
        ),
        html.Br(),
        html.Label('Minimum number of Oscar wins (all categories)'),
        dcc.Slider(
            id='oscars-won-slider',
            min=df.Oscars.min(),
            max=df.Oscars.max(),
            marks={str(o): str(o) for o in range(int(df.Oscars.min()), int(df.Oscars.max()), 1)},
            value=df.Oscars.min(),
            step=None
        ),
        html.Br()], style={'marginLeft': 25, 'marginRight': 25}
    ),
    html.Div([
        html.Label('Graph'),
        dcc.Graph(
            id='scatter-plot-graph',
            animate=True,
            figure={
                'data': [
                    go.Scatter(
                        x=df[df.has_oscar == True].Meter,
                        y=df[df.has_oscar == True].Reviews,
                        text=df[df.has_oscar == True].Title,
                        mode='markers',
                        opacity=0.5,
                        marker={
                            'color': 'orange',
                            'size': 10,
                            'line': {'width': 1, 'color': 'black'}
                        },
                        name='has_oscar: yes'
                    ),
                    go.Scatter(
                        x=df[df.has_oscar == False].Meter,
                        y=df[df.has_oscar == False].Reviews,
                        text=df[df.has_oscar == False].Title,
                        mode='markers',
                        opacity=0.5,
                        marker={
                            'color': 'gray',
                            'size': 10,
                            'line': {'width': 1, 'color': 'black'}
                        },
                        name='has_oscar: no'
                    )
                ],
                'layout': go.Layout(
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    xaxis={'title': 'Tomato Meter'},
                    yaxis={'title': 'Number of reviews'},
                    hovermode='closest'
                )
            }
        )
    ], style={'marginLeft': 25, 'marginRight': 25})
])


@app.callback(
    dash.dependencies.Output('scatter-plot-graph', 'figure'),
    [
        dash.dependencies.Input('nb-reviews-slider', 'value'),
        dash.dependencies.Input('year-released-slider', 'value'),
        dash.dependencies.Input('oscars-won-slider', 'value')
    ]
)
def update_scatter_plot(selected_nb_reviews, selected_year_released, selected_nb_oscars_won):

    print(selected_nb_reviews, selected_year_released, selected_nb_oscars_won)

    nb_reviews = selected_nb_reviews or df.Reviews.min()
    year_released = selected_year_released or df.Year.min()
    oscars_won = selected_nb_oscars_won or df.Oscars.min()

    filtered_df = (df.pipe(lambda df: df[df['Reviews'] >= nb_reviews])
                   .pipe(lambda df: df[df['Year'] >= year_released])
                   .pipe(lambda df: df[df['Oscars'] >= oscars_won]))

    return {
        'data': [
            go.Scatter(
                x=filtered_df[filtered_df.has_oscar == True].Meter,
                y=filtered_df[filtered_df.has_oscar == True].Reviews,
                text=filtered_df[filtered_df.has_oscar == True].Title,
                mode='markers',
                opacity=0.5,
                marker={
                    'color': 'orange',
                    'size': 10,
                    'line': {'width': 1, 'color': 'black'}
                },
                name='has_oscar: yes'
            ),
            go.Scatter(
                x=filtered_df[filtered_df.has_oscar == False].Meter,
                y=filtered_df[filtered_df.has_oscar == False].Reviews,
                text=filtered_df[filtered_df.has_oscar == False].Title,
                mode='markers',
                opacity=0.5,
                marker={
                    'color': 'gray',
                    'size': 10,
                    'line': {'width': 1, 'color': 'black'}
                },
                name='has_oscar: no'
            )
        ],
        'layout': go.Layout(
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            xaxis={
                'title': variable_labels['Meter'],
                'range': [
                    filtered_df.Meter.min() - 10,
                    filtered_df.Meter.max() + 10
                ]
            },
            yaxis={
                'title': variable_labels['Reviews'],
                'range': [
                    filtered_df.Reviews.min() - 10,
                    filtered_df.Reviews.max() + 10
                ]},
            hovermode='closest'
        )
    }


# Add a custom CSS stylesheet
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})


if __name__ == '__main__':
    app.run_server(debug=True)
