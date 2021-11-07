import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Set up Flask
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data"""
    # Query all stations
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    precipitations = []
    for date, prcp in results:
        precipitation = {}
        precipitation["date"] = date
        precipitation["prcp"] = prcp
        precipitations.append(precipitation)

    return jsonify(precipitations)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data for the most active station last year"""
    # Query all temperature data for most active station last year
    statement = session.query(Measurement.station, func.count(Measurement.id)).\
                        group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).limit(1).statement
    station_df = pd.read_sql_query(statement, session.bind)
    most_active_station_id = station_df['station'][0]

    result = session.query(func.max(Measurement.date)).all()
    # to_date = result[0][0]
    to_date = datetime.strptime(result[0][0], '%Y-%m-%d')
    from_date = to_date - relativedelta(months=+12)


    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > from_date).\
                filter(Measurement.date < to_date).filter(Measurement.station == most_active_station_id)
    

    session.close()

    temperatures = []
    for date, tobs in results:
        temperature = {}
        temperature["date"] = date
        temperature["tobs"] = tobs
        temperatures.append(temperature)

    return jsonify(temperatures)

@app.route("/api/v1.0/<startdate>")
def stats_per_startdate(startdate):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return min temperature, avg, temperature and max temperature for given start date"""
    # Query min temperature, avg, temperature and max temperature for given start date
    # Get min and max date to help the user choose
    min_date = session.query(func.min(Measurement.date)).all()
    min_date = min_date[0][0]
    max_date = session.query(func.max(Measurement.date)).all()
    max_date = max_date[0][0]

    # check if the date passed is in the dataset
    date_there = bool(session.query(Measurement).filter_by(date=startdate).first())

    if date_there == True:
        results = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= startdate).all()
    else:
        date_error = f"This date is not in the dataset. Please choose a date between {min_date} and {max_date}"
        return jsonify({f"error": date_error}), 404

    session.close()

    temp_stats = []
    for result in results:
        temp_dict = {"TMAX":[], "TMIN":[], "TAVG":[]}
        temp_dict["TMAX"] = result[0]
        temp_dict["TMIN"] = result[1]
        temp_dict["TAVG"] = result[2]
        temp_stats.append(temp_dict)

    return jsonify(temp_stats)


@app.route("/api/v1.0/<startdate>/<enddate>")
def stats_between_dates(startdate, enddate):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return min temperature, avg, temperature and max temperature between start and end date"""
    # Query min temperature, avg, temperature and max temperature between start and end date
    # Get min and max date to help the user choose
    min_date = session.query(func.min(Measurement.date)).all()
    min_date = min_date[0][0]
    max_date = session.query(func.max(Measurement.date)).all()
    max_date = max_date[0][0]

    # check if the date passed is in the dataset
    startdate_there = bool(session.query(Measurement).filter_by(date=startdate).first())
    enddate_there = bool(session.query(Measurement).filter_by(date=enddate).first())

    if startdate_there == True and enddate_there == True:
        results = session.query(func.max(Measurement.tobs), func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= startdate).all()
    else:
        date_error = f"One or both of these dates is not in the dataset. Please choose dates between {min_date} and {max_date}"
        return jsonify({f"error": date_error}), 404

    session.close()

    temp_stats_period = []
    for result in results:
        temp_dict = {"TMAX":[], "TMIN":[], "TAVG":[]}
        temp_dict["TMAX"] = result[0]
        temp_dict["TMIN"] = result[1]
        temp_dict["TAVG"] = result[2]
        temp_stats_period.append(temp_dict)

    return jsonify(temp_stats_period)









if __name__ == '__main__':
    app.run(debug=True)


