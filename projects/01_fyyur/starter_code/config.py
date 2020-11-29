import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
## connection url with username as postgres and password 1234
DB_USER = os.getenv('DB_USER', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'fyyur') 
DB_PASSWORD = os.getenv('DB_PASSWORD', '1234') 


SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}' 
#'<Put your local database url>'

