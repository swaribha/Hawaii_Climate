import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
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
""" results = session.query(Station.name).all()
for record in list(results):
    print(record) """
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    #query the precipitation data 
    results=session.query(Measurement.date,Measurement.prcp.label( "precipitation")).all()
    prcp_data=[]
    for date,precipitation in results:
        prcp_dict={}
        prcp_dict[date]=precipitation
        # prcp_dict['precipitation']=precipitation
        prcp_data.append(prcp_dict)
    
    return jsonify(prcp_data)
@app.route('/api/v1.0/stations')
def stations():
    results=session.query(Station).all()
    station_data=[]
    for row in results:
        station_dict={}
        station_dict['station_id']=row.station
        station_dict['name']=row.name
        station_dict['latitude']=row.latitude
        station_dict['longitude']=row.longitude
        station_dict['elevation']=row.elevation
        station_data.append(station_dict)
    return jsonify(station_data)

@app.route('/api/v1.0/tobs')
# function to get temprature data for a yearfrom last date
def tobs():
    # calculate the last date in the dataset
    date_last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    # print(date_last)
    # calcuating the date year agofrom last date
    date_year_ago=dt.datetime.strptime(date_last,'%Y-%m-%d').date()-dt.timedelta(days=365)
    # print(date_year_ago)
    # # Perform a query to retrieve the data and precipitation scores
    temprature_data=session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>= date_year_ago).all()
    temp_obs=[]
    for row in temprature_data:
        temp_dict={}
        temp_dict[row.date]=row.tobs
        # temp_dict['temprature']=row.tobs
        temp_obs.append(temp_dict)
    return jsonify(temp_obs)

@app.route('/api/v1.0/<start_dt>')
@app.route('/api/v1.0/<start_dt>/<end_dt>')
def date(start_dt,end_dt=None):
    min_maxlist=[]
    if (end_dt==None):
        results=session.query(func.min(Measurement.tobs).label('min'), func.avg(Measurement.tobs).label('average'), func.max(Measurement.tobs).label('max')).filter(Measurement.date >= start_dt).all()
    else:
        results=session.query(func.min(Measurement.tobs).label('min'), func.avg(Measurement.tobs).label('average'), func.max(Measurement.tobs).label('max')).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt).all()
    for row in results:
        minmax_dict={}
        minmax_dict['Minimum Temprature']=row.min
        minmax_dict['Average Temprature']=row.average
        minmax_dict['Maximum Temprature']=row.max
        min_maxlist.append(minmax_dict)
    return jsonify(min_maxlist)

# .filter(Measurement.date <= end_date).all()

if __name__ == '__main__':
    app.run(debug=True)
