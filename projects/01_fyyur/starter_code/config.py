import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
## connection url with username as postgres and password 1234
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/fyyur' 
#'<Put your local database url>'

##app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/fyyur'
