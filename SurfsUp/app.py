# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home page route
@app.route("/")
def home():
    # Printing list of available routes for home page
    return (
        f"Welcome to the Hawaii Weather API</br>"
        f"Available Routes:<br/>"
        f"Precipitation over the last year: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperatures from most active station: /api/v1.0/tobs<br/>"
        f"Min/Max/Avg temps from start date: /api/v1.0/start_date<br/>"
        f"Min/Max/Avg temps from date range: /api/v1.0/start_date/end_date")


# Precipitation route (returns date: precipitation dictionary)
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Setting year_ago date and constructing query
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    session.close()

    # Looping through query and creating date: precipitation dictionary
    precipitation_date = []
    for date, prcp in rain_data:
        dict = {}
        dict["precipitation"] = prcp
        dict["date"] = date
        precipitation_date.append(dict)
    return jsonify(precipitation_date)


# Station route (returns list of all stations that reported data)
@app.route("/api/v1.0/stations")
def stations():
    # Constructing query
    station_names = session.query(Station.station).all()
    session.close()
    
    # Converting tuple list into normal list 
    station_names = list(np.ravel(station_names))
    return jsonify(station_names)


# Temperature route (returns list of temps from most active station USC00519281)
@app.route("/api/v1.0/tobs")
def tobs():
    # Setting year_ago date and constructing query
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == 'USC00519281').\
                    filter(Measurement.date >= year_ago).all()
    session.close()
    
    # Converting tuple list into normal list 
    active_station = list(np.ravel(active_station))
    return jsonify(active_station)


# Start route (no end date provided, returns min/avg/max temp from start_date)
@app.route("/api/v1./<start>")
def start_date(start):
    # Constructing query
    date_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                filter(func.strftime("%Y-%m-%d",Measurement.date) >= start).all()
    session.close()

    # Converting tuple list into normal list   
    date_data = list(np.ravel(date_data))
    return jsonify(date_data)


# Start/End route (end date provided, returns min/avg/max temp between start_date & end_date)
@app.route ("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    # Constructing query
    start_end_data = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                filter(func.strftime("%Y-%m-%d",Measurement.date) >= start).\
                filter(func.strftime("%Y-%m-%d",Measurement.date) <= end).all()
    session.close()

    # Converting tuple list into normal list   
    start_end_data = list(np.ravel(start_end_data))
    return jsonify(start_end_data)


# Run API
if __name__ == "__main__":
    app.run()