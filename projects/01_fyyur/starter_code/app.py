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
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }

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
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  #data = list(filter(lambda d: d['id'] == artist_id, Artist.query.all()))[0]
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
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>

  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
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
