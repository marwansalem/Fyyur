#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
import sys
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db, compare_type=True)

#app.config['SQLALCHEMY_DATABASE_URI'] = app.config.getSQLALCHEMY_DATABASE_URI

#print(app.config.SQLALCHEMY_DATABASE_URI)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

Show = db.Table('Show', \
db.Column('id', db.Integer, primary_key=True), \
db.Column('artist', db.Integer, db.ForeignKey('Artist.id'), nullable=False),\
db.Column('venue', db.Integer, db.ForeignKey('Venue.id'), nullable=False), \
db.Column('start_time', db.String))

#changed start_time from a datetime column to string column so it can work with the included date filter

class Venue(db.Model):
    __tablename__ = 'Venue'
    # TODO change to  lower case

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    #upcoming_shows_count = db.Column(db.Integer, default=0) 
    # can be computed using a join no need to add a column
    #past_shows_count = db.Column(db.Integer, default=0)
    genres = db.Column(db.String(120))




    artists = db.relationship('Artist', secondary=Show, backref=db.backref('artists', lazy=True))
    #shows = db.relationship('Show', backref='shows', lazy=True)

    #is this overkill too much relations among tables
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    #wanted to change to a lower case name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    #shows = db.relationship('Show', backref='shows', lazy=True)
    #no need for shows column, you can get them using a join


# TODO: implement any missing fields, as a database migration using Flask-Migrate
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


# 
def get_past_upcoming_shows(shows_list, format='%Y-%m-%d %H:%M:%S'):
  """ This function receives a list of shows that were queried from "Show" relation,
  it classifies them according to start_time attribute/column , comparing the start_time,
  to the current time, it returns two lists, upcoming shows and past shows respectively """
  now = datetime.datetime.now()
  upcoming = []
  past = []
  for s in shows_list:
    dt = datetime.datetime.strptime(s.start_time, format)
    if dt < now:
      past.append(s)
    else:
      upcoming.append(s)
  return past, upcoming
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  """ This function generates a list of all distinct areas where venues are present according to state and city,
  and for each area it generates the list of venues present int it."""
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  try:
    # get the distinct areas (state,city) of Venues
    areas = db.session.query(Venue.state, Venue.city).distinct(Venue.state, Venue.city).all()

    for area in areas:
      area_dict = {}
      state, city = area
      venues_in_area = Venue.query.filter_by(state=state, city=city).all()
      area_dict['state'] = state
      area_dict['city'] = city
      area_dict['venues'] = venues_in_area
      data.append(area_dict)


  except:
    print(sys.exc_info())

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')

  query_res = Venue.query.filter(Venue.name.ilike('%' + search_term +'%'))
  venues = query_res.all()
  count = query_res.count()
  response = {}

  response['count'] = count
  response['data'] = venues


  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    venue = Venue.query.get(venue_id)
    shows = db.session.query(Show).filter_by(venue=venue_id).join(Venue).all()

    data = venue.__dict__
    past , upcoming = get_past_upcoming_shows(shows)
    past_shows_count = len(past)
    upcoming_shows_count = len(upcoming)
    data['past_shows_count'] = past_shows_count
    data['upcoming_shows_count'] = upcoming_shows_count
    data['past_shows'] = past
    data['upcoming_shows'] = upcoming
    
  except:
    err = True
    flash('Error unknown venue')
    data = []
    print(sys.exc_info())
    

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """Receive data from a form, and validates it, if it is not valid the session will rollback,
  other wise a new venues is created and committed to the database"""
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  err = False
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']

    genres = request.form.getlist('genres')
    venue.genres = ','.join(genres)
  #if the checkbox is marked the request.form will have a 'seeking_talent' key with value = 'y' , otherwise there will be no key
    if request.form.get('seeking_talent', 'N') == 'y':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
      venue.seeking_description = request.form['seeking_description']
      db.session.add(venue)
      db.session.commit()
  except:
    err = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  if not err:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue_to_delete = Venue.query.get(venue_id)
    db.session.delete(venue_to_delete)
  except:
    db.session.close()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  """ This function queries all artist and filters them such that the search term 
  is a case-insensitive substring of the name of the artist,
  The output of the query is formatted to show the count and the results."""
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  

  search_term = request.form.get('search_term', '')

  query_res = Artist.query.filter(Artist.name.ilike('%' + search_term +'%'))
  artists = query_res.all()
  count = query_res.count()
  response = {}

  response['count'] = count
  response['data'] = artists
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """ This endpoint gets an artist from the database, and reformats the output of the query; adding necessary fields
  so it a specific template can be rendered."""
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  shows = db.session.query(Show).filter_by(artist=artist_id).join(Artist).all()
  ## need to get show
  

  data = artist.__dict__
  past , upcoming = get_past_upcoming_shows(shows)
  past_shows_count = len(past)
  upcoming_shows_count = len(upcoming)
  data['past_shows_count'] = past_shows_count
  data['upcoming_shows_count'] = upcoming_shows_count
  data['past_shows'] = past
  data['upcoming_shows'] = upcoming
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  #artist has the following fields: id,name,genres, city,state,phone,website,facebook_link,seeking_venue,seeking_description, image_link
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  """ This endpoint receives data from the form, validates it, then cleans it if there are no exceptions or invalidations,
  then it updates the specified artist and commits changes to database, if any errors were found the session rollbacks"""
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  err = False
  try:
    artist_to_edit = Artist.query.get(artist_id)
    #get the edited fields
    artist_to_edit.name = request.form['name']
    artist_to_edit.city = request.form['city']
    artist_to_edit.state = request.form['state']
    artist_to_edit = request.form['phone']
    artist_to_edit.facebook_link = request.form['facebook_link']
    artist_to_edit.image_link = request.form['image_link']
    artist_to_edit.website = request.form['website']

    if request.form.get('seeking_venue', 'N') == 'y':
      artist_to_edit.seeking_venue = True
    else:
      artist_to_edit.seeking_venue = False
    artist_to_edit.seeking_description = request.form['seeking_description']
    genres = request.form.getlist('genres')
    artist_to_edit.genres = ','.join(genres)
    
    #do not have to add the edited artist to session or else it will create a record
    db.session.commit()
  except:
    err = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

    if err:
      flash('Cannot edit, artist does not exist')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>

  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  """Takes the data that was submitted through the form, validates it, if it is valid
    it then updates the Venue with the id = venue_id, and commits changes to the database."""
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  err = False
  try:
    venue = Venue.query.get(venue_id)

    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue = request.form['phone']
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    #venue.seeking_talent = request.form['seeking_talent']
    genres = request.form.getlist('genres')
    venue.genres = ','.join(genres)
    if request.form.get('seeking_talent', 'N') == 'y':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    venue.seeking_description = request.form['seeking_description']
    
    #commit the changes then close the session
    db.session.commit()
    db.session.close()
  except:
    err = True
    db.session.rollback()
  else:
    flash('Venue does not exist!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():

  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  """ This function receives data from the create artist form and validates the data,
  and inserts the clean data to the Artist Table """
  
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new artist record in the db, instead
  err = False
  
  try:
    new_artist = Artist()
    new_artist.name = request.form['name']
    new_artist.city = request.form['city']
    new_artist.state = request.form['state']
    new_artist.phone = request.form['phone']
    new_artist.facebook_link = request.form['facebook_link']
    new_artist.image_link = request.form['image_link']
    new_artist.website = request.form['website']

    if request.form.get('seeking_venue', 'N') == 'y':
      new_artist.seeking_venue = True
    else:
      new_artist.seeking_venue = False
    new_artist.seeking_description = request.form['seeking_description']

    genres = request.form.getlist('genres')
    new_artist.genres = ','.join(genres)

    db.session.add(new_artist)
    db.session.commit()
  except:
    err = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
 


  # TODO: modify data to be the data object returned from db insertion
  if not err:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred, Artist ' + request.form['name'] + ' already listed!')
 
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.


  #shows = Venue.query.join(Artist).filter(venue_id)
  #need to write a query to get the shows
  shows = db.session.query(Show).all()
  print(shows)
      

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """This function is responsible for accepting data from a form,
  it then validates the data, and inserts a new record in the Relation 'Show' .
  If there are any errors in the data, the database session will be rollbacked to ensure the 
  validity of the data"""
  # called to create new shows in the db, upon submitting new show listing form

  err = False

  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']
    #db.session.add()
    
    #venue = Venue.query.get(venue_id)
    #artist = Artist.query.get(artist_id)
    #venue.artists.append[artist]
    insert_statement = Show.insert().values(artist=artist_id, venue=venue_id, start_time=start_time)
    db.session.execute(insert_statement)
    db.session.commit()
  except:
    err = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  if not err:
    flash('Show was successfully listed!')
  else:
    flash('An error occurred. Show could not be listed.')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
