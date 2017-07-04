import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from get_data import all_movies, variable_labels, genres

# TODO: add Flask-Caching using Redis as backend db

# Access data
df = all_movies.copy()

# Init Dash app
app = dash.Dash()

# Set app layout
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
        dcc.RangeSlider(
            id='year-released-range-slider',
            min=df.Year.min(),
            max=df.Year.max(),
            marks={str(y): str(y) for y in range(int(df.Year.min()), int(df.Year.max()), 5)},
            value=[df.Year.min(), df.Year.max()]
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
        html.Br(),
        html.Label('Dollars at Box Office (millions)'),
        dcc.RangeSlider(
            id='dollars-boxoffice-range-slider',
            min=0,
            max=800,
            marks={str(y): str(y) for y in range(0, 800, 20)},
            value=[0, 800],
        ),
        html.Br(),
        html.Label('Genre (a movie can have multiple genres)'),
        dcc.Dropdown(
            id='genre-dropdown',
            options=[
                {'label': genre.upper(), 'value': genre} for genre in genres
            ],
            multi=False
        ),
        html.Br(),
        html.Label('Director name contains (e.g., Miyazaki)'),
        dcc.Input(id='director-input', value='', type='text'),
        html.Br(),
        html.Label('Cast names contains (e.g. Tom Hanks)'),
        dcc.Input(id='cast-input', value='', type='text'),
        html.Br(),
    ], style={'marginLeft': 25, 'marginRight': 25}
    ),
    html.Div([
        html.Br(),
        html.Label('X-axis variable'),
        dcc.Dropdown(
            id='x-axis-dropdown',
            options=[
                {'label': label, 'value': value} for value, label in variable_labels.items()
            ],
            multi=False,
            value='Meter'
        ),
        html.Br(),
        html.Label('Y-axis variable'),
        dcc.Dropdown(
            id='y-axis-dropdown',
            options=[
                {'label': label, 'value': value} for value, label in variable_labels.items()
            ],
            multi=False,
            value='Reviews'
        ),
        html.Br(),
        html.P('''
        Note: The Tomato Meter is the proportion of positive reviews (as judged by the Rotten Tomatoes staff),
        and the Numeric rating is a normalized 1-10 score of those reviews which have star ratings (for example,
        3 out of 4 stars).
        '''),
        html.Br()
    ], style={'marginLeft': 25, 'marginRight': 25}),
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
        ),
        html.Br(),
        html.P('Number of rows selected: {}'.format(len(df.index)), id='dataset-rows-p')
    ], style={'marginLeft': 25, 'marginRight': 25})
])


@app.callback(
    dash.dependencies.Output('scatter-plot-graph', 'figure'),
    [
        dash.dependencies.Input('nb-reviews-slider', 'value'),
        dash.dependencies.Input('year-released-range-slider', 'value'),
        dash.dependencies.Input('oscars-won-slider', 'value'),
        dash.dependencies.Input('dollars-boxoffice-range-slider', 'value'),
        dash.dependencies.Input('genre-dropdown', 'value'),
        dash.dependencies.Input('director-input', 'value'),
        dash.dependencies.Input('cast-input', 'value'),
        dash.dependencies.Input('x-axis-dropdown', 'value'),
        dash.dependencies.Input('y-axis-dropdown', 'value')
    ]
)
def update_scatter_plot(selected_nb_reviews, selected_years_released, selected_nb_oscars_won,
                        selected_dollars_boxoffice, selected_genre, input_director, input_cast,
                        x_axis_var, y_axis_var):

    nb_reviews = selected_nb_reviews or df.Reviews.min()
    year_released_start, year_released_end = selected_years_released or (df.Year.min(), df.Year.max())
    oscars_won = selected_nb_oscars_won or df.Oscars.min()
    dollars_boxoffice_min, dollars_boxoffice_max = (amount * 1e6 for amount in selected_dollars_boxoffice) or \
        (df.BoxOffice.min(), df.BoxOffice.max())
    movie_genre = selected_genre or None
    director = input_director.strip() or None
    cast_name = input_cast.strip() or None
    x_axis = x_axis_var or 'Meter'
    y_axis = y_axis_var or 'Reviews'

    filtered_df = (
        df.pipe(lambda df: df[df['Reviews'] >= nb_reviews])
        .pipe(lambda df: df[(df['Year'] >= year_released_start) & (df['Year'] <= year_released_end)])
        .pipe(lambda df: df[df['Oscars'] >= oscars_won])
        .pipe(lambda df: df[(df['BoxOffice'] >= dollars_boxoffice_min) & (df['BoxOffice'] <= dollars_boxoffice_max)])
        .pipe(lambda df: df[df['Genre'].str.contains(movie_genre)] if movie_genre else df)
        .pipe(lambda df: df[df['Director'].str.contains(director)] if director else df)
        .pipe(lambda df: df[df['Cast'].str.contains(cast_name)] if cast_name else df)
    )

    return {
        'data': [
            go.Scatter(
                x=filtered_df[filtered_df.has_oscar == True][x_axis],
                y=filtered_df[filtered_df.has_oscar == True][y_axis],
                text=filtered_df[filtered_df.has_oscar == True]['Title'],
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
                x=filtered_df[filtered_df.has_oscar == False][x_axis],
                y=filtered_df[filtered_df.has_oscar == False][y_axis],
                text=filtered_df[filtered_df.has_oscar == False]['Title'],
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
                'title': variable_labels[x_axis],
                'range': [
                    filtered_df[x_axis].min(),
                    filtered_df[x_axis].max()
                ]
            },
            yaxis={
                'title': variable_labels[y_axis],
                'range': [
                    filtered_df[y_axis].min(),
                    filtered_df[y_axis].max()
                ]},
            hovermode='closest'
        )
    }


@app.callback(
    dash.dependencies.Output('dataset-rows-p', 'children'),
    [
        dash.dependencies.Input('nb-reviews-slider', 'value'),
        dash.dependencies.Input('year-released-range-slider', 'value'),
        dash.dependencies.Input('oscars-won-slider', 'value'),
        dash.dependencies.Input('dollars-boxoffice-range-slider', 'value'),
        dash.dependencies.Input('genre-dropdown', 'value'),
        dash.dependencies.Input('director-input', 'value'),
        dash.dependencies.Input('cast-input', 'value'),
        dash.dependencies.Input('x-axis-dropdown', 'value'),
        dash.dependencies.Input('y-axis-dropdown', 'value')
    ]
)
def update_nb_rows_selected(selected_nb_reviews, selected_years_released, selected_nb_oscars_won,
                            selected_dollars_boxoffice, selected_genre, input_director, input_cast,
                            x_axis_var, y_axis_var):
    nb_reviews = selected_nb_reviews or df.Reviews.min()
    year_released_start, year_released_end = selected_years_released or (df.Year.min(), df.Year.max())
    oscars_won = selected_nb_oscars_won or df.Oscars.min()
    dollars_boxoffice_min, dollars_boxoffice_max = (amount * 1e6 for amount in selected_dollars_boxoffice) or \
        (df.BoxOffice.min(), df.BoxOffice.max())
    movie_genre = selected_genre or None
    director = input_director.strip() or None
    cast_name = input_cast.strip() or None
    x_axis = x_axis_var or 'Meter'
    y_axis = y_axis_var or 'Reviews'

    filtered_df = (
        df.pipe(lambda df: df[df['Reviews'] >= nb_reviews])
        .pipe(lambda df: df[(df['Year'] >= year_released_start) & (df['Year'] <= year_released_end)])
        .pipe(lambda df: df[df['Oscars'] >= oscars_won])
        .pipe(lambda df: df[(df['BoxOffice'] >= dollars_boxoffice_min) & (df['BoxOffice'] <= dollars_boxoffice_max)])
        .pipe(lambda df: df[df['Genre'].str.contains(movie_genre)] if movie_genre else df)
        .pipe(lambda df: df[df['Director'].str.contains(director)] if director else df)
        .pipe(lambda df: df[df['Cast'].str.contains(cast_name)] if cast_name else df)
    )

    return 'Number of rows selected: {}'.format(len(filtered_df.index))

# Add a custom CSS stylesheet
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})


if __name__ == '__main__':
    app.run_server(debug=True)
