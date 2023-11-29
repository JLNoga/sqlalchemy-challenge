# Import the dependencies.

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measure = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
# Calculate the date one year from the last date in data set.
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start/<start>/end/<end>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    one_year = session.query(Measure.date, Measure.prcp).\
    filter(Measure.date>=year_ago).all()
    
    session.close()
    
    one_year_rows = [{"Date": year[0], "Precipitation": year[1]} for year in one_year]
    
    return jsonify(one_year_rows)

@app.route("/api/v1.0/stations")
def stations():    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    #Query a list of stations
    station_list = session.query(Measure.station).\
        group_by(Measure.station).all()

    session.close

    station_list_rows = [{"Station":station[0]} for station in station_list]
    
    return jsonify(station_list_rows)

@app.route("/api/v1.0/tobs")
def tobs():
    
    twelve_months = session.query(Measure.date, Measure.tobs).\
    filter(Measure.date>=year_ago).\
    filter(Measure.station=="USC00519281").all()

    session.close

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    twelve_months_rows = [{"Date": temp[0],"Temperature": temp[1]} for temp in twelve_months]

    return jsonify(twelve_months_rows)

@app.route("/api/v1.0/start/<start>")
def begin(start):
    start = dt.datetime.strptime(start, '%Y%m%d')
    print(start)
    active_id = session.query(Measure.date, 
                              func.min(Measure.tobs), 
                              func.avg(Measure.tobs), 
                              func.max(Measure.tobs)).\
    filter(Measure.date>=start).\
    group_by(Measure.date).all()
    
    session.close
    print(len(active_id))
    active_id_rows = [{"Date": temp[0], "TMin": temp[1], 
                       "TAvg": temp[2], "TMax": temp[3]} 
                       for temp in active_id]

    return jsonify(active_id_rows)

@app.route("/api/v1.0/start/<start>/end/<end>")
def begin_end(start, end):
    start = dt.datetime.strptime(start, '%Y%m%d')
    end = dt.datetime.strptime(end, '%Y%m%d')
    
    active_id_end = session.query(Measure.date, 
                              func.min(Measure.tobs), 
                              func.avg(Measure.tobs), 
                              func.max(Measure.tobs)).\
    filter(Measure.date >= start).\
    filter(Measure.date <= end).\
    group_by(Measure.date).all()
    
    session.close
    
    active_id_end_rows = [{"Date": temp[0], "TMin": temp[1], 
                       "TAvg": temp[2], "TMax": temp[3]} 
                       for temp in active_id_end]

    return jsonify(active_id_end_rows)
if __name__ == '__main__':
    app.run(debug=True)