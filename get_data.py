import itertools as it
import sqlite3

import pandas as pd

# Read SQLite results into a Pandas DataFrame
with sqlite3.connect('movies.db') as con:
    omdb = pd.read_sql_query('SELECT * FROM omdb', con)
    tomatoes = pd.read_sql_query('SELECT * FROM tomatoes', con)

# Join tables, filtering out those with <10 reviews, and select specified columns
all_movies = pd.merge(omdb, tomatoes, how='inner', on='ID')\
    .pipe(lambda df: df[df['Reviews'] >= 10])\
    .assign(has_oscar=lambda row: row.Oscars >= 1)

# Fill NaN values with empty string for categorical variables and
# with 0. for numerical variable
all_movies['Genre'].fillna(value='', inplace=True)
all_movies['Director'].fillna(value='', inplace=True)
all_movies['Cast'].fillna(value='', inplace=True)
all_movies['BoxOffice'].fillna(value=.0, inplace=True)

# Unique Genre values
genres = set(list(it.chain.from_iterable([g.split(', ') for g in all_movies.Genre if g])))

# Mapping between variables and labels for dropdown selection
variable_labels = {
    'Meter': 'Tomato Meter',
    'Rating_y': 'Numeric Rating',
    'Reviews': 'Number of reviews',
    'BoxOffice': 'Dollars at box office',
    'Year': 'Year',
    'Runtime': 'Length (minutes)'
}
