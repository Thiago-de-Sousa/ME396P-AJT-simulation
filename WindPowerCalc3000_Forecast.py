# Copyright Thiago de Sousa, Ashan Ran, and Juan Barbarena
# under the MIT license

# Future Gains Turbine Gang v1: the ultimate turbine calculator with
# forecast weather data using Dark Sky API

# Required installed packages:
    # pandas, geopy, windpowerlib, geocoder, datetime, json, csv, sys, requests
    # timezonefinderL, matplotlib

# Initial process: user input on desired location


from windpowerlib import ModelChain, WindTurbine


# import necessary packages
# Data packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Geo packages
from geopy.distance import geodesic
import geocoder

# Forecast-necessary packages
import os
import sys
import json
import requests
from datetime import datetime, date, time, timedelta, timezone

# User inputs: 
desired_loc = str(input('Desired location: '))

   
# Handling location
try:
    Location = geocoder.osm(desired_loc)
    desired_lat_long = Location.latlng
    lat, long = round(desired_lat_long[0],2), round(desired_lat_long[1],2)
except NameError:
    sys.exit('Please install geocoder before proceeding')
except TypeError:
    sys.exit('Please enter a valid location')

loc_string = str(lat) + ',' + str(long)

# Determining where user is, to warn if input is very far from them
try:
    user_current_loc = geocoder.ip('me')
    user_lat_long = user_current_loc.latlng
    distance_mi = round(geodesic(user_lat_long,desired_lat_long).miles,2)
except NameError:
    sys.exit('Please install geopy before proceeding')


# Handling bad user input - location
if isinstance(desired_lat_long,list) is False:
    sys.exit('\n','Invalid location, please try again')
    distance_mi = 0

if distance_mi > 350:
    print('\n','Warning! Your distance to the location is', distance_mi,'miles',
          '\n','Consider refining your input using City,State/Province,Country')
    YesorNo = input('Would you like to proceed? (Y/N): ')
    if YesorNo != ('Y' or 'y'):
        sys.exit('Weather download cancelled...')

# Using dark sky API - limit of 100 requests/month
try:
    RAPID_API_KEY = 'ba1272d4a3mshe642df7b84ef927p1702b5jsnaf57a7183e2f'
    url = "https://dark-sky.p.rapidapi.com/" + loc_string
    querystring = {"lang":"en","units":"si","extend":"hourly"} # 168 hrs of data
    headers = {
        'x-rapidapi-host': "dark-sky.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
      }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if(200 == response.status_code):
        api_response = json.loads(response.text)
    else:
        sys.exit('Invalid location. Exiting script.')
except TypeError:
    sys.exit('Invalid location. Please refine your input. Exiting...')

# Manipulating data to behave as needed for windpowerlib
# Empty lists
time_stamps, temperature, pressure, wind_speed = [],[],[],[]

for record in api_response['hourly']['data']:
    time_L = record['time']
    temp = record['temperature']
    press = record['pressure']
    wind = record['windSpeed']
    time_converted = datetime.fromtimestamp(time_L).strftime('%Y-%m-%d %H:%M')
    time_stamps.append(time_converted)
    temperature.append(temp)
    pressure.append(press)
    wind_speed.append(wind)

# Creating weather dataframe
raw_weather = {'Time':time_stamps,'pressure':pressure,
               'temperature':temperature,'wind_speed':wind_speed}
weather_data = pd.DataFrame(raw_weather)

# Adding roughness value (obtained from sample weather data)
length = len(weather_data)
roughness_length_column = [0.15 for i in range(length)]
weather_data['roughness_length'] = roughness_length_column

# Unit conversions
weather_data['temperature'] += 273.15 # Kelvin conversion
weather_data['pressure'] *= 100 # conversion from hPa to Pa

# Adding heigts
heights_row = []
heights_row.insert(0,{'Time':'height','pressure': 0,'temperature': 2,
                      'wind_speed':10,'roughness_length':0})
w_data = pd.concat([pd.DataFrame(heights_row),weather_data],
                                   ignore_index=True)
# In case of missing data:
w_data.loc[w_data["pressure"].isnull(),'pressure'] = 101500
w_data.loc[w_data["temperature"].isnull(),'temperature'] = 298
w_data.loc[w_data["wind_speed"].isnull(),'wind_speed'] = 0

w_data.to_csv('weather.csv',index=False)

# Taken from windpowerlib example file
def get_weather_data(filename='weather.csv', **kwargs):
    r"""
    Imports weather data from a file.

    The data include wind speed at two different heights in m/s, air
    temperature in two different heights in K, surface roughness length in m
    and air pressure in Pa. The height in m for which the data applies is
    specified in the second row.
    In case no weather data file exists, an example weather data file is
    automatically downloaded and stored in the same directory as this example.

    Parameters
    ----------
    filename : str
        Filename of the weather data file. Default: 'weather.csv'.

    Other Parameters
    ----------------
    datapath : str, optional
        Path where the weather data file is stored.
        Default is the same directory this example is stored in.

    Returns
    -------
    :pandas:`pandas.DataFrame<frame>`
        DataFrame with time series for wind speed `wind_speed` in m/s,
        temperature `temperature` in K, roughness length `roughness_length`
        in m, and pressure `pressure` in Pa.
        The columns of the DataFrame are a MultiIndex where the first level
        contains the variable name as string (e.g. 'wind_speed') and the
        second level contains the height as integer at which it applies
        (e.g. 10, if it was measured at a height of 10 m). The index is a
        DateTimeIndex.

    """

    if 'datapath' not in kwargs:
        kwargs['datapath'] = os.path.dirname(__file__)

    file = os.path.join(kwargs['datapath'], filename)

    # download example weather data file in case it does not yet exist
    if not os.path.isfile(file):
        req = requests.get("https://osf.io/59bqn/download")
        with open(file, "wb") as fout:
            fout.write(req.content)

    # read csv file
    weather_df = pd.read_csv(
        file,
        index_col=0,
        header=[0, 1],
        date_parser=lambda idx: pd.to_datetime(idx, utc=True))

    # change time zone
    weather_df.index = weather_df.index.tz_convert(
        'Europe/Berlin')

    return weather_df

# Read weather data from csv
try:
    weather = get_weather_data(filename='weather.csv', datapath='')
except PermissionError:
    sys.exit('Please close any open CSVs before continuing')

csvdata = pd.read_csv('weather.csv')
tspan = csvdata[csvdata.columns[0]].to_numpy().tolist()[1:]

# Get a WindTurbine object for each entry in MyTurbines.csv
csvdata = pd.read_csv('MyTurbines.csv')
turbinesList = csvdata.turbine_catalog_name.to_numpy().tolist()
hubHeightsList = csvdata.hub_height.to_numpy().tolist()
amountsList = csvdata.amount.to_numpy().tolist()
listOfDicts = []
n=0
for turbine in turbinesList:
    listOfDicts.append({'turbine_type': turbine, 'hub_height': hubHeightsList[n], 'amount': amountsList[n]})
    n+=1

n=0
listOfWindTurbines = []
for elem in listOfDicts:
    listOfWindTurbines.append(WindTurbine(**elem))
    n+=1

# Taken from windpowerlib example file
modelchain_data = {
    'wind_speed_model': 'logarithmic',      # 'logarithmic' (default),
                                            # 'hellman' or
                                            # 'interpolation_extrapolation'
    'density_model': 'ideal_gas',           # 'barometric' (default), 'ideal_gas'
                                            #  or 'interpolation_extrapolation'
    'temperature_model': 'linear_gradient', # 'linear_gradient' (def.) or
                                            # 'interpolation_extrapolation'
    'power_output_model':
        'power_curve',                      # 'power_curve' (default) or
                                            # 'power_coefficient_curve'
    'density_correction': True,             # False (default) or True
    'obstacle_height': 0,                   # default: 0
    'hellman_exp': None                     # None (default) or None
}                    

#creating a model for each entry in MyTurbines.csv
n=0
listOfModelChains = []
for elem in listOfWindTurbines:
    listOfModelChains.append(ModelChain(listOfWindTurbines[n], **modelchain_data).run_model(weather))
    n+=1
    
# initialize ModelChain with own specifications and use run_model method to
# calculate power output
# mc_e126 = ModelChain(listOfWindTurbines[0], **modelchain_data).run_model(weather)

#Create list of arrays. Each array has power values for every time value in the weather data.
n=0
powerOutputListOfArrays = []
for elem in listOfModelChains:
    powerOutputListOfArrays.append(np.array(listOfModelChains[n].power_output.tolist()))
    n+=1
    
#Sum up all arrays (and multiply by amount of turbines for each array) into one 1-D array that contains power of entire wind farm for every time value in the weather data.
n=0
for elem in powerOutputListOfArrays:
    if n==0:
        totalPowerArray = elem * listOfDicts[n]['amount']
    else:
        totalPowerArray += elem * listOfDicts[n]['amount']
    n+=1

# Convert to a pandas series for faster plotting
totalPowerPandasSeries = pd.Series(totalPowerArray, tspan)

# Get current time to label plot.
now = datetime.now()
print("now =", now)
dt_string = now.strftime("%d-%m-%Y %H%M")
print("date and time =", dt_string)

# Plotting
plt.figure()
# listOfModelChains[0].power_output.plot(legend=True, label='Enercon E126')
# listOfModelChains[1].power_output.plot(legend=True, label='GE120')
totalPowerPandasSeries.plot()

title = 'Power Generation Forecast for Next Seven Days \n Generated: '
plt.title(title + dt_string)
plt.xlabel('Time')
plt.xticks(rotation = 45)
plt.ylabel('Power in W')
plt.tight_layout()
plt.show()
plt.savefig('Forecast Plots/Forecast_{}_{}.png'.format(desired_loc, dt_string))
 