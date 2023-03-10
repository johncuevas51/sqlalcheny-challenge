import numpy as np
import re
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################
# Database Setup
#################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(autoload_with=engine)

#save the reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################
# Flask Setup
#################################
app = Flask(__name__)


#################################
#Flask Routes
#################################

@app.route("/")
def Welcome():
    """List all available API routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"

    )

@app.route("/api/v1.0/precipitation") #Convert query results to a dictionary using `date` as the key and `prcp` as the value
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Measurement
    session.query(measurement.date).order_by(measurement.date.desc()).first()

    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()

    
    session.close()

    # Create a dictionary
    precipitation_date_prcp = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["prcp"] = each_row.prcp
        precipitation_date_prcp.append(dt_dict)

    return jsonify(precipitation_date_prcp)



@app.route("/api/v1.0/stations") #Return a JSON list of stations from the dataset
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Stations
    results = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    # Query all temperature from most active station
    results = session.query(measurement.date, measurement.tobs).filter(
        measurement.station == "USC00519281").filter(measurement.date > '2016-08-23').all()

    session.close()

    # list of temp observations of most active station
    active_station = []
    for date, tobs in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["tobs"] = tobs
        active_station.append(precipitation_dict)

    return jsonify(active_station)


@app.route("/api/v1.0/<start>")
def single_date(start):
    if start >= "2010-01-01" and start <= "2017-08-23":

        session = Session(engine)

        sel = [func.min(measurement.tobs), func.avg(
            measurement.tobs), func.max(measurement.tobs)]

        results = session.query(*sel).filter(measurement.date >= start).all()

        session.close()

        summary = []
        for min, avg, max in results:
            summary_dict = {}
            summary_dict["tmin"] = min
            summary_dict["tavg"] = avg
            summary_dict["tmax"] = max
            summary.append(summary_dict)

        return jsonify(summary)
    else:
        return jsonify({"error": f"Date not in range, must be between 2010-01-01 and 2017-08-23."}), 404


@app.route("/api/v1.0/<start>/<end>")
def dates(start, end):

    if (start >= "2010-01-01" and start <= "2017-08-23") and (end >= "2010-01-01" and end <= "2017-08-23"):

        session = Session(engine)

        sel = [func.min(measurement.tobs), func.avg(
            measurement.tobs), func.max(measurement.tobs)]

        results = session.query(*sel).filter(measurement.date >= start).all()

        session.close()

        summary = []
        for min, avg, max in results:
            summary_dict = {}
            summary_dict["tmin"] = min
            summary_dict["tavg"] = avg
            summary_dict["tmax"] = max
            summary.append(summary_dict)

        return jsonify(summary)
    else:
        return jsonify({"error": f"Date not in range, must be between 2010-01-01 and 2017-08-23."}), 404




if __name__ == "__main__":
        app.run(debug=True)
