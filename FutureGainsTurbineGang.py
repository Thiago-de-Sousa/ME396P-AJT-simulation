# Copyright Thiago de Sousa, Ashan Ran, and Juan Barbarena
# under the MIT license

# Future Gains Turbine Gang v1: the ultimate turbine calculator with
# forecast weather data using Dark Sky API

# Required installed packages:
    # pandas, geopy, windpowerlib, geocoder, datetime, json, csv, sys, requests
    # timezonefinderL, matplotlib

# Initial process: user input on desired location, timeframe and daily/hourly

# import necessary packages
# Data packages
import pandas as pd

# Geo packages
from geopy.distance import geodesic
import geocoder

# Forecast-necessary packages
import sys
import json
import requests
from datetime import datetime, date, time, timedelta, timezone

# User inputs: 
desired_loc = str(input('Desired location: '))
# desired_forecast = input('Input number of days from today for forecast: ')
# try:
#     desired_delta = int(desired_forecast)
#     if not 1<=desired_delta<=7:
#         desired_delta = 7
#         print('Maximum forecast is for 7 days. Set to 7 days')
# except NameError:
#     print('Invalid input. Default set to 7')
#     desired_delta = 7
# today_date = date.today()
# time_delta = timedelta(desired_delta)

   
# Handling location
Location = geocoder.osm(desired_loc)
desired_lat_long = Location.latlng
lat, long = round(desired_lat_long[0],2), round(desired_lat_long[1],2)
loc_string = str(lat) + ',' + str(long)

# Determining where user is, to warn if input is very far from them
user_current_loc = geocoder.ip('me')
user_lat_long = user_current_loc.latlng
distance_mi = round(geodesic(user_lat_long,desired_lat_long).miles,2)

# Handling bad user input - location
if isinstance(desired_lat_long,list) is False:
    print('Invalid location, please try again')
    exit()
    distance_mi = 0

if distance_mi > 350:
    print('Warning! Your distance to the location is', distance_mi,'miles',
          '\n','Consider refining your input using City,State/Province,Country')
    YesorNo = input('Would you like to proceed? (Y/N): ')
    if YesorNo != 'Y':
        exit()

# Using dark sky API - limit of 100 requests/month
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
    print('Invalid location. Exiting script')
    exit()

# Manipulating data to behave as needed for windpowerlib
# Empty lists
time_stamps, temperature, pressure, wind_speed = [],[],[],[]

for record in api_response['hourly']['data']:
    time_L = record['time']
    temp = record['temperature']
    press = record['pressure']
    wind = record['windSpeed']
    time_converted = datetime.fromtimestamp(time_L).strftime('%Y%m%d')
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
formatted_weather_data = pd.concat([pd.DataFrame(heights_row),weather_data],
                                   ignore_index=True)

formatted_weather_data.to_csv('Test_file_deliverable2.csv',index=False)

