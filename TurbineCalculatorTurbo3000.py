# Copyright Thiago de Sousa, Ashan Ran, and Juan Barbarena
# under the MIT license

# Turbine Calculator Turbo 3000 v1: the ultimate turbine calculator with
# historical weather data

# Required installed packages:
    # pandas, geopy, windpowerlib, geocoder, meteostat, datetime, 
    # timezonefinderL, matplotlib

# Initial process: user input on desired location, timeframe and daily/hourly

# import necessary packages
# Data packages
import pandas as pd

# Geo packages
from geopy.distance import geodesic
import geocoder

# Forecast packages
import datetime
from timezonefinderL import TimezoneFinder as TZFind
from meteostat import Point, Hourly

# User inputs: 
desired_loc = str(input('Desired location: '))
start_year = input('Start Year: ')
start_month = input('Month (as number 1-12): ')
start_day = input('Day: ')
end_year = input('End Year: ')
end_month = input('Month (as number 1-12): ')
end_day = input('Day: ')

try:
    start_year,start_month,start_day = eval(start_year), eval(start_month), eval(start_day)
    end_year,end_month,end_day = eval(end_year), eval(end_month), eval(end_day)
except NameError:
    print('Invalid input. Please try again')
    exit()

# Handling too old data and users from the future that don't know 
# the gregorian calendar

# Basic ones first
if start_year < 2000 or start_year > end_year or not isinstance(start_year,int):
    start_year = 2000
    print('Warning: Fetching the data will likely take a long time')
if (end_year > datetime.datetime.now().year or not isinstance(end_year,int)
    or end_year < start_year):
    end_year = datetime.datetime.now().year
if not 1<=start_month<=12 or not isinstance(start_month,int):
    start_month = 1
if not 1<=end_month<=12 or not isinstance(end_month,int):
    end_month = 1
if not 1<=start_day<=31 or not isinstance(start_day,int):
    start_day = 1
if not 1<=end_day<=31 or not isinstance(end_day,int):
    end_day = 1
    
# Big brain ones
if start_year == end_year and start_month>=end_month:
    start_month = end_month
    if start_day > end_day:
        start_day = end_day - 1
        print('Warning: erroneous dates input. Single day will be obtained')

if end_year == datetime.datetime.now().year:
    if end_month > datetime.datetime.now().month:
        end_month = datetime.datetime.now().month
    if end_month == datetime.datetime.now().month:
        if end_day > datetime.datetime.now().day:
            end_day = datetime.datetime.now().day
            print("Warning: if you'd like to use predicted data", 
                  ' please refer to the FutureGainsTurbineGang model')

   
# Handling location
Location = geocoder.osm(desired_loc)
desired_lat_long = Location.latlng
lat, long = desired_lat_long[0], desired_lat_long[1]

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
        quit()

# Handling start year, end year, and standardized timezone
tf = TZFind()
tz = tf.timezone_at(lng=long, lat=lat)
start = datetime.datetime(start_year,start_month,start_day)
end = datetime.datetime(end_year,end_month,end_day)

# Obtaining weather data
desired_point = Point(lat,long,10) #Finds closest weather station
weather_data = Hourly(desired_point, start, end)   
weather_data = weather_data.fetch()

# Manipulating to the format needed
# Weather columns that aren't needed
weather_data = weather_data.drop(['dwpt','rhum','prcp','snow','coco',
                                  'tsun','wdir','wpgt'],axis=1)
weather_data.rename(columns= {'temp':'temperature',
                              'pres':'pressure',
                              'wspd':'wind_speed'},inplace=True)
w_data_format = weather_data.reindex(columns = ['pressure','temperature',
                                                'wind_speed'])
# Adding roughness value (obtained from sample weather data)
length = len(w_data_format)
roughness_length_column = [0.15 for i in range(length)]
w_data_format['roughness_length'] = roughness_length_column

# Unit conversions
w_data_format['temperature'] += 273.15 # Kelvin conversion
w_data_format['pressure'] *= 100 # conversion from hPa to Pa
w_data_format['wind_speed'] *= (5/18) # conversion to m/s

# adding heights row 
heights_row = []
heights_row.insert(0,{'pressure': 0,'temperature': 2,'wind_speed':10,
                      'roughness_length':0})
formatted_weather_data = pd.concat([pd.DataFrame(heights_row),w_data_format],
                                   ignore_index=False)
formatted_weather_data.to_csv('Test_file.csv')










