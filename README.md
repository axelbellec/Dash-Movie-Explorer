## Movie Explorer app

A clone of the famous RStudio Shiny sample app.
Data is a subset of data from OBDb (IMDb + Rotten Tomatoes).

[[Demo]](https://dash-movie-explorer.herokuapp.com/)

### Usage

First, install python dependencies:

```
$ pip install -r requirements.txt
```

Then, launch Dash app:
```
$ python app.py
```

### Deployment using Heroku

You will need a new dependency, `gunicorn`, for deploying the app:
```
$ pip install gunicorn
```

You can deploy the Dash app by exposing the server variable like this:
```python
import dash

app = dash.Dash(__name__)

# Get the Flask app instance for gunicorn
server = app.server
```

Then, create a `Procfile`:
```
web: gunicorn app:server
```

Finally, initialize Heroku and deploy:
```
$ heroku create dash-movie-explorer
$ git push heroku master # deploy code to heroku
$ heroku ps:scale web=1  # run the app with a 1 heroku "dyno"
```
