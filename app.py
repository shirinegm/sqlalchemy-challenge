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
        f"/api/v1.0/2017-08-23<br/>"
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



if __name__ == '__main__':
    app.run(debug=True)
