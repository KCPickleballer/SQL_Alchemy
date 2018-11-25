import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import text


from flask import Flask, jsonify
from datetime import date, timedelta
from datetime import datetime



#################################################
# Database Setup
#################################################
#engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")
engine = create_engine('sqlite:///Instructions/Resources/hawaii.sqlite', connect_args={'check_same_thread': False}, echo=True)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Stations = Base.classes.stations

Measurements = Base.classes.measurements

# Create our session (link) from Python to the DB
session = Session(engine)

conn = engine.connect()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"start & end are dates in format YYYY-MM-DD<br/>"
    )


@app.route("/api/v1.0/stations")
def names():
    """Return a list of stations"""
    # Query all passengers
    results = session.query(Stations.name).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of preipitation for each day of the last year"""
    # Query all passengers
   # results = session.query(Passenger).all()
   # session.commit()

    now = date.today()

    one_yr = timedelta(days=365)
    

    now = now - one_yr
    last_yr = now - one_yr


    #last_yr = last_yr.isoformat()
    last_year = last_yr.strftime('%Y-%m-%d')
    now_str =  now.strftime('%Y-%m-%d')

# get the precip amounts from the observation place with 
    s = text(
     "SELECT   m.date, max(m.prcp) maxPrcp, max( m.tobs) maxTobs  "
         " FROM measurements m "
         " join (SELECT  mx.station, count(*) "
         "  FROM measurements mx "
         "  where mx.date between :x and :y "
         "  group by mx.station "
         "  order by count(*) desc limit 1 ) as t1 on "
         " m.station = t1.station "
         " where m.date between :x and :y "
         " group by m.date"
         " order by m.date ")
    results = conn.execute(s, x=last_year, y=now_str).fetchall()


    # Create a dictionary from the row data and append to a list of all_passengers
    all_dates = []
    for prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = prcp[0]
        prcp_dict["prcp"] = prcp[1]
        all_dates.append(prcp_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/<start>")
def api_start(start):
    """Fetch the Justice League character whose real_name matches
       the path variable supplied by the user, or a 404 if not."""

    #canonicalized = real_name.replace(" ", "").lower()
    begin_object = datetime.strptime(start, '%Y-%m-%d')
    
    one_yr = timedelta(days=365)


    begin_object = begin_object - one_yr
    
#last_yr = last_yr.isoformat()
    begin_dte = begin_object.strftime('%Y-%m-%d')

#now_str =  now.strftime('%Y-%m-%d')
    
    s = text(
     "SELECT   min(m.tobs) minTemp, max(m.tobs) maxTemp, avg(m.tobs) avgTemp  "
         " FROM measurements m "
         " where m.date >= :x ")
         
    try:
        trip = conn.execute(s, x=begin_dte).fetchone()
    except:
        return "SQL Error"

    all_dates = []
    temp_dict = {}
    temp_dict["minTemp"] = trip[0]
    temp_dict["maxTemp"] = trip[1]
    temp_dict["avgTemp"] = trip[2]
    all_dates.append(temp_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/<start>/<end>")
def api_start_end(start, end):
    """Fetch the Justice League character whose real_name matches
       the path variable supplied by the user, or a 404 if not."""

    #canonicalized = real_name.replace(" ", "").lower()
    begin_object = datetime.strptime(start, '%Y-%m-%d')
    end_object = datetime.strptime(end, '%Y-%m-%d')
    
    one_yr = timedelta(days=365)

    ###  subtract one year from both dates because we dont have data for 2018
    begin_object = begin_object - one_yr
    end_object = end_object - one_yr
   
    
#last_yr = last_yr.isoformat()
    begin_dte = begin_object.strftime('%Y-%m-%d')
    end_dte = end_object.strftime('%Y-%m-%d')

#now_str =  now.strftime('%Y-%m-%d')
    
    s = text(
     "SELECT   min(m.tobs) minTemp, max(m.tobs) maxTemp, avg(m.tobs) avgTemp  "
         " FROM measurements m "
         " where m.date between :x and :y ")
         
    try:
        trip = conn.execute(s, x=begin_dte, y=end_dte).fetchone()
    except:
        return "SQL Error"

    all_dates = []
    temp_dict = {}
    temp_dict["minTemp"] = trip[0]
    temp_dict["maxTemp"] = trip[1]
    temp_dict["avgTemp"] = trip[2]
    all_dates.append(temp_dict)

    return jsonify(all_dates)



if __name__ == '__main__':
    app.run(debug=True)

