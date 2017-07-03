import pandas as pd
import sqlite3

# Read SQLite results into a Pandas DataFrame
with sqlite3.connect('movies.db') as con:
    omdb = pd.read_sql_query('SELECT * FROM omdb', con)
    tomatoes = pd.read_sql_query('SELECT * FROM tomatoes', con)

# Join tables, filtering out those with <10 reviews, and select specified columns
all_movies = pd.merge(omdb, tomatoes, how='inner', on='ID')\
    .pipe(lambda df: df[df['Reviews'] >= 10])\
    .assign(has_oscar=lambda row: row.Oscars == 1)


variable_labels = {
    'Meter': 'Tomato Meter',
    'Rating': 'Numeric Rating',
    'Reviews': 'Number of reviews',
    'BoxOffice': 'Dollars at box office',
    'Year': 'Year',
    'Runtime': 'Length (minutes)'
}
