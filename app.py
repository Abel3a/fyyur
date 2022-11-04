#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os
from sqlalchemy import MetaData
from re import search
import sys
from sqlalchemy import create_engine
from flask_migrate import Migrate
from sqlalchemy import create_engine  
from sqlalchemy import Column, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import datetime
from datetime import datetime
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
 



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=True)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.String(500))
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    
def __repr__(self):
     return f"<Venue {self.id} name: {self.name}>"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=True)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.String(500))
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True, cascade='all, delete')
       
    def __repr__(self):
          return f"<Artis {self.id} name: {self.name}>"

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='cascade'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='cascade'))
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
          return f"<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>"
     

with app.app_context():
  db.create_all()
  db.session.commit()
  
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
  data = []
  city_state_unit = set()
  results = Venue.query.all()
    
  for result in results:
        city_state_unit.add((result.city, result.state))
       
  for reservation in city_state_unit:
        # format each venue
        formatted_venues = []
        
        for result in results:
          if(result.state == reservation[1]) and (result.city == reservation[0]):
               upcoming_show_count =  db.session.query(Show).join(Venue).filter(Show.start_time>datetime.now()).all();
         
               formatted_venues.append({
               "id": result.id,
               "name": result.name,
               "num_upcoming_shows": upcoming_show_count
              
          })
        data.append(
          {
         "state": reservation[1],
         "city": reservation[0],
             "venues": formatted_venues
           }
          ) 
              
  
  return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get("search_term", "")
  venues=Venue.query.filter(
    Venue.name.ilike(f"%{search_term}%") |
    Venue.state.ilike(f"%{search_term}%") |
    Venue.city.ilike(f"%{search_term}%")
  ).all()
  response={}
  response["count"]=len(venues)
  response["data"]=[]
  if len(venues)>0:
        
        for venue in venues:
            venue_entity={
              "id":venue.id,
              "name":venue.name,
              "num_upcoming_shows":len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all())
            }
        response["data"].append(venue_entity)
        
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if not venue:
        return render_template('errors/404.html')
      
  past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  last_shows = []
  for show in past_shows:
        past = {}
        past["artist_id"] = show.artist.id
        past["artist_name"] = show.artist.name
        past["artist_image_link"] = show.artist.image_link
        past["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        last_shows.append(past)

  setattr(venue, "past_shows", last_shows)
  setattr(venue,"past_shows_count", len(past_shows))

  # Chow fucture

  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  next_shows = []
  for show in upcoming_shows:
      next = {}
      next["artist_id"] = show.artist.id
      next["artist_name"] = show.artist.name
      next["artist_image_link"] = show.artist.image_link
      next["start_time"] = show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      next_shows.append(next)

      setattr(venue, "upcoming_shows", next_shows)    
      setattr(venue,"upcoming_shows_count", len(upcoming_shows))
  return render_template('pages/show_venue.html', venue=venue)

 

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form=VenueForm(request.form)
  if form.validate():
    
    try:
      new_venue= Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=[].__add__(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
      )
      db.session.add(new_venue)
      db.session.commit()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
# TODO: modify data to be the data object returned from db insertion
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
       print("\n\n", form.errors)
       flash('Venue ' + request.form['name'] + ' could not be listed.')
       return redirect(url_for('create_venue_form'))
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue=Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash("Venue "+venue.name + "has been deleted with success")
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Venue hasn't been deleted with success.")
  finally:
    db.session.close()
 
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artiste=Artist.query.filter(
    Artist.name.ilike(f"%{search_term}%") |
    Artist.city.ilike(f"%{search_term}%") |
    Artist.state.ilike(f"%{search_term}%") 
  ).all()
  response={
    "count":len(artiste),
    "data":[]
  }
  if len(artiste)>0:

    for artist in artiste:
      artistes= {
        "id":artist.id,
        "name":artist.name,
        "upcoming_shows":len(db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()),
      }
    response["data"].append(artistes)
      
  return render_template('pages/search_artists.html', results=response, search_term=search_term)
  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
   artist=Artist.query.get(artist_id) 
   if not artist: 
    return render_template('errors/404.html')
      
   past_shows=db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
   last_shows=[]
   for show in past_shows:
    last={}
    last["venue_id"]=show.venue.id
    last["venue_name"]=show.venue.name
    last["venue_image_link"]=show.venue.image_link
    last["start_time"]=show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    last_shows.append(last)

    setattr(artist, "past_shows", last_shows)
    setattr(artist, "past_shows_count",len(past_shows))


  #upcomming_show
   
    upcoming_shows=db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
    next_shows=[]
    for show in upcoming_shows:
     next={}
    next["venue_id"]=show.venue.id
    next["venue_name"]=show.venue.name
    next["venue_image_link"]=show.venue.image_link
    next["start_time"]=show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    next_shows.append(next)

    setattr(artist, "upcoming_shows", next_shows)
    setattr(artist, "upcoming_shows_count", len(upcoming_shows))
    return render_template('pages/show_artist.html', artist=artist)
   

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  
  if artist: 
    form.name.data=artist.name
    form.city.data=artist.city
    form.state.data=artist.state
    form.phone.data=artist.phone
    form.genres.data=artist.genres
    form.facebook_link.data=artist.facebook_link
    form.image_link.data=artist.image_link
    form.website_link.data=artist.website_link
    form.seeking_venue.data=artist.seeking_venue
    form.seeking_description.data=artist.seeking_description
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
 form = ArtistForm(request.form)
 if form.validate():
    try:
      artist=Artist.query.get(artist_id)
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.genres=[].__add__(form.genres.data)
      artist.facebook_link=form.facebook_link.data
      artist.image_link=form.image_link.data
      artist.website_link=form.website_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data

      db.session.add(artist)
      db.session.commit()
      flash("Artist "+ artist.name + "has been updated with success!")
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Artist hasn't been updated with success.")  
    finally:
      db.session.close()
 else:
    print("\n\n", form.errors)
    flash("Artist hasn't been updated with success.") 
 return redirect(url_for('show_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.address.data=venue.address
  form.phone.data=venue.phone
  form.genres.data=venue.genres
  form.facebook_link.data=venue.facebook_link
  form.image_link.data=venue.image_link
  form.website_link.data=venue.website_link
  form.seeking_talent.data=venue.seeking_talent
  form.seeking_description.data=venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form=VenueForm(request.form)

  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.address=form.address.data
      venue.phone=form.phone.data
      venue.genres=[].__add__(form.genres.data)
      venue.facebook_link=form.facebook_link.data
      venue.image_link=form.image_link.data
      venue.website_link=form.website_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      
      db.session.add(venue)
      db.session.commit()

      flash("Venue "+ form.name.data +" has been updated with success")
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash("Venue wasn't updated with success")
    finally:
      db.session.close()
  else:
    print("\n\n", form.errors)
    flash("Venue wasn't updated with success")
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
 form=ArtistForm(request.form)
 if form.validate():

    try:
      new_artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=[].__add__(form.genres.data),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
      )
# TODO: modify data to be the data object returned from db insertion
      db.session.add(new_artist)
      db.session.commit()
# on successful db insert, flash success
      flash('Artist ' + form.name.data + ' was successfully listed!')
     
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
      return redirect(url_for('create_artist_form'))
    finally:
      db.session.close()
 else:
    print("\n\n",form.errors)
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    return redirect(url_for('create_artist_form'))
  
 return render_template('pages/home.html')
   
    
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = db.session.query(Show).join(Artist).join(Venue).all()
  
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
       # TODO: on unsuccessful db insert, flash an error instead.
       # called to create new shows in the db, upon submitting new ven listing form
  # TODO: insert form data as a new Show record in the db, instead
  form=ShowForm(request.form)
  if form.validate():
        
        try:
          new_show =Show(
          venue_id=form.venue_id.data,
          artist_id=form.artist_id.data,
          start_time=form.start_time.data
          )
      
          db.session.add(new_show)
          db.session.commit()
          flash('Show was successfully listed!')
        except:
          db.session.rollback()
          print(sys.exc_info())
          flash('An error occurred Show could not be listed')
    # TODO: modify data to be the data object returned from db insertion
        finally:
          db.session.close()
  else:
    print("\n\n",form.errors)
    flash(' Show could not be listed an error occurred')
 
  return redirect(url_for('index'))

  

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
