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
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Weather API</br>"
        f"Available Routes:<br/>"
        f"Precipitation over the last year: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperatures from most active station: /api/v1.0/tobs<br/>"
        f"Min/Max/Avg temps from start date: /api/v1.0/<start><br/>"
        f"Min/Max/Avg temps from date range: /api/v1.0/<start>/<end>")


@app.route("/api/v1.0/precipitation")
def precipitation():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    session.close()

    precipitation_date = []
    for date, prcp in data:
        dict = {}
        dict["precipitation"] = prcp
        dict["date"] = date
        precipitation_date.append(dict)
    return jsonify(precipitation_date)


@app.route("/api/v1.0/stations")
def stations():
    station_names = session.query(Station.station).all()
    session.close()
    station_names = list(np.ravel(station_names))
    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == 'USC00519281').\
                    filter(Measurement.date >= year_ago).all()
    session.close()
    active_station = list(np.ravel(active_station))
    return jsonify(active_station)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def date_data(start=None, end=None):
    date_data = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]           

    if not end: 

        results = session.query(*date_data).\
        filter(Measurement.date <= start).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps)


    results = session.query(*date_data).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == "__main__":
    app.run()