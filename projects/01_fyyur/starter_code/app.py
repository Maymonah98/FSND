#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.sqltypes import ARRAY, DateTime
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database 
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model) :
  _tablename_= 'show'
  venue_id=db.Column(db.Integer,db.ForeignKey('venue.id'),primary_key=True)
  artist_id=db.Column(db.Integer,db.ForeignKey('artist.id'),primary_key=True)
  start_time=db.Column(db.DateTime, nullable=False,default=datetime.utcnow)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),)
    genres=db.Column(ARRAY(db.String()))
    website_link= db.Column(db.String(500),nullable=False)
    looking_for_talent= db.Column(db.Boolean,default=False)
    seeking_desc= db.Column(db.String())
    shows = db.relationship('Show',backref='venue',lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres=db.Column(ARRAY(db.String()))
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link= db.Column(db.String(500))
    looking_for_venues= db.Column(db.Boolean,default=False)
    seeking_desc= db.Column(db.String())
    shows = db.relationship('Show',backref='artist',lazy=True)


def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.image_link} {self.website_link} {self.seeking_desc}>'

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
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
  now = datetime.utcnow()
  venues= Venue.query.with_entities(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  data=[]
  for venue in venues:
    d= {
      "city": venue.city,
      "state": venue.state,
      "venues": []
      }
    venue1 = Venue.query.filter(Venue.city==venue.city).filter(Venue.state==venue.state).all()

    for v in venue1:
      num_shows= Show.query.filter(Show.venue_id==v.id).filter(Show.start_time>= now)
      v= {
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": num_shows,
      }
      d['venues'].append(v)
    data.append(d)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  now = datetime.utcnow()
  st=request.form.get('search_term', '')
  venues=Venue.query.filter(Venue.name.ilike('%'+st+'%')).all()
  response={
    "count": len(venues),
    "data": []
  }
  for venue in venues:
    num_shows= Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>= now)
    data={
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_shows,
    }
    response["data"].append(data)
  
  return render_template('pages/search_venues.html', results=response, search_term=st)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  now = datetime.utcnow()
  venues= Venue.query.filter_by(id=venue_id).all()
  for venue in venues:
    past_shows= Show.query.filter(Show.start_time <= now).filter(venue.id==Show.venue_id)
    upcoming_shows = Show.query.filter(Show.start_time>=now).filter(venue.id==Show.venue_id)
    data = {
      "id":venue.id,
      "name": venue.name,
      "genres":venue.genres,
      "address":venue.address,
      "city":venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "looking_for_talent": venue.looking_for_talent,
      "seeking_description": venue.seeking_desc,
      "image_link": venue.image_link,
      "past_shows": [],
      "upcoming_shows": [],
      "past_shows_count": past_shows.count(),
      "upcoming_shows_count": upcoming_shows.count(),
    }
    for past_show in past_shows:
      past_show={
        "artist_id": past_show.artist_id,
        "artist_name": past_show.artist.name,
        "artist_image_link": past_show.artist.image_link,
        "start_time": format_datetime(str(past_show.start_time))
      }
      data['past_shows'].append(past_show)
    for upcoming_show in upcoming_shows:
      upcoming_show={
        "artist_id": upcoming_show.artist_id,
        "artist_name": upcoming_show.artist.name,
        "artist_image_link": upcoming_show.artist.image_link,
        "start_time": format_datetime(str(upcoming_show.start_time))
      }
      data["upcoming_shows"].append(upcoming_show)

    
    
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
  try:
      name= request.form['name']
      city=request.form['city']
      state=request.form['state']
      address= request.form['address']
      phone=request.form['phone']
      genres=  request.form.getlist('genres')
      facebook_link=request.form['facebook_link']
      image_link=request.form['image_link']
      website_link=request.form['website_link']
      seeking_Talent=True if 'seeking_talent' in request.form else False
      seeking_description=request.form['seeking_description']
      data= Venue(name= name,city=city,state=state,address=address,phone=phone,genres=genres,facebook_link=facebook_link,
                  image_link=image_link,website_link=website_link,
                  looking_for_talent=seeking_Talent,
                  seeking_desc=seeking_description)
      db.session.add(data)
      db.session.commit()

  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
     db.session.rollback()
     print(sys.exc_info())
  # TODO: on unsuccessful db insert, flash an error instead.
     flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  finally:
     db.session.close()
  return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
  except:
        db.session.rollback()
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
  now = datetime.utcnow()
  st=request.form.get('search_term', '')
  artists=Artist.query.filter(Artist.name.ilike('%'+st+'%')).all()
  response={
    "count": len(artists),
    "data": []
  }
  for artist in artists:
    num_shows= Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time>= now)
    data={  
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_shows,
    }
    response['data'].append(data)
  
  return render_template('pages/search_artists.html', results=response, search_term=st)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data={}
  now = datetime.utcnow()
  artists= Artist.query.filter_by(id=artist_id).all()
  for artist in artists:
    past_shows=Show.query.filter(Show.start_time<=now).filter(artist.id==Show.artist_id)
    upcoming_shows = Show.query.filter(Show.start_time>=now).filter(artist.id==Show.artist_id)
    data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.looking_for_venues,
      "seeking_description": artist.seeking_desc,
      "image_link": artist.image_link,
      "past_shows": [],
      "upcoming_shows":[],
      "past_shows_count": past_shows.count(),
      "upcoming_shows_count": upcoming_shows.count(),
    }
    for past_show in past_shows:
      past_show={
        "venue_id": past_show.venue_id,
        "venue_name": past_show.venue.name,
        "venue_image_link": past_show.venue.image_link,
        "start_time": format_datetime(str(past_show.start_time))
      }
      data["past_shows"].append(past_show)
    for upcoming_show in upcoming_shows:
      upcoming_show= {
      "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.venue.name,
      "venue_image_link": upcoming_show.venue.image_link,
      "start_time": format_datetime(str(upcoming_show.start_time))
    }
      data["upcoming_shows"].append(upcoming_show)
    
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist=Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm(obj=artist)
  form.populate_obj(artist)
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=Artist.query.filter_by(id=artist_id).first()
  artist.name= request.form['name']
  artist.city=request.form['city']
  artist.state=request.form['state']
  artist.phone=request.form['phone']
  artist.genres= request.form.getlist('genres')
  artist.facebook_link=request.form['facebook_link']
  artist.image_link=request.form['image_link']
  artist.website_link=request.form['website_link']
  artist.seeking_venue=True if 'seeking_venue' in request.form else False
  artist.seeking_desc=request.form['seeking_description']
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue=Venue.query.filter_by(id=venue_id).first()
  form = VenueForm(obj=venue)
  form.populate_obj(venue)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue=Venue.query.filter_by(id=venue_id).first()

  venue.name= request.form['name']
  venue.city=request.form['city']
  venue.state=request.form['state']
  venue.address= request.form['address']
  venue.phone=request.form['phone']
  venue.genres=  request.form.getlist('genres')
  venue.facebook_link=request.form['facebook_link']
  venue.image_link=request.form['image_link']
  venue.website_link=request.form['website_link']
  venue.looking_for_talent=True
  venue.seeking_Talent=True if 'seeking_talent' in request.form else False
  venue.seeking_description=request.form['seeking_description']

  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  data={}
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      name= request.form['name']
      city=request.form['city']
      state=request.form['state']
      phone=request.form['phone']
      genres= request.form.getlist('genres')
      facebook_link=request.form['facebook_link']
      image_link=request.form['image_link']
      website_link=request.form['website_link']
      seeking_venue=True if 'seeking_venue' in request.form else False
      seeking_description=request.form['seeking_description']
      data= Artist(name= name,city=city,state=state,phone=phone,genres=genres,facebook_link=facebook_link,
                  image_link=image_link,website_link=website_link,
                  looking_for_venues=seeking_venue,
                  seeking_desc=seeking_description)
      db.session.add(data)
      db.session.commit()

  # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
     db.session.rollback()
     print(sys.exc_info())
  # TODO: on unsuccessful db insert, flash an error instead.
     flash('An error occurred. Artist could not be listed.')
  finally:
     db.session.close()
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows= Show.query.all() 
  data=[]
  for show in shows:
      d={
        "start_time": format_datetime(str(show.start_time)),
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
      }
      data.append(d)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    start_time= request.form['start_time']
    venue_id= request.form['venue_id']
    artist_id= request.form['artist_id']
    data=Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(data)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
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
