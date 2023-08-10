import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from dateutil.relativedelta import relativedelta

# Database Setup

engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
session.query(Measurement.date).order_by(Measurement.date.desc()).first()
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
session.close()

#Flask Setup

app = Flask(__name__)

# Flask Routes

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App Home Page!<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_end"
    )

@app.route("/api/v1.0/precipitation")
def precip():

    # Query all precipitation
    previous_year = dt.date(2017,8,23)- dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).\
                order_by(Measurement.date).all()
    result_dict = dict(results)
    session.close()
    return jsonify(result_dict)

@app.route("/api/v1.0/stations")
def stations():

    # Query all stations
    stations = session.query(Measurement.station, func.count(Measurement.id)).\
            group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()

    stations_dict = dict(stations)
    session.close()
    return jsonify(stations_dict)

@app.route("/api/v1.0/tobs")
def tobs():

    # Query all tobs
    max_temp_tobs = session.query(Measurement.station, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').all()

    tobs_dict = dict(max_temp_tobs)
    session.close()
    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start_date>")
def start_date(start_date):

    # Query all tobs
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()

    session.close()

    # Create a list

    start_date_tobs = []

    for min, avg, max in results:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min_temp"] = min
        start_date_tobs_dict["avg_temp"] = avg
        start_date_tobs_dict["max_temp"] = max
        start_date_tobs.append(start_date_tobs_dict) 
    return jsonify(start_date_tobs)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):

    # Query all tobs
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)
    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)