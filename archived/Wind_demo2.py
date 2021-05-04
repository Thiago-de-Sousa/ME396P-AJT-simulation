#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 17:35:59 2021

@author: thiago
"""

import os
import pandas as pd
import requests
from windpowerlib import ModelChain, WindTurbine, TurbineClusterModelChain, WindFarm

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
weather = get_weather_data(filename='weather.csv', datapath='')

# Get specific turbines - Using same as single turbine example
enercon_e126 = {
    'turbine_type': "E-126/4200",
    'hub_height': 135}

GE_120 = {
    'turbine_type': "GE120/2500",
    'hub_height': 135}

e126 = WindTurbine(**enercon_e126)
GE_turb = WindTurbine(**GE_120)

"""
This time, we'll be doing turbine farms instead of single turbines
This can be specially useful to simulate wake losses created by neighboring
turbines. Requires more data to be accurate to real world analysis
"""
# Dataframe with turbine fleet info
Enercon_turbine_fleet = pd.DataFrame(
        {'wind_turbine': [e126],  # as windpowerlib.WindTurbine
         'number_of_turbines': [6],})

# initialize WindFarm object
Enercon_farm = WindFarm(name='Enercon_farm',
                        wind_turbine_fleet=Enercon_turbine_fleet)

GE_turbine_fleet = pd.DataFrame(
        {'wind_turbine': [GE_turb],  # as windpowerlib.WindTurbine
         'number_of_turbines': [6],})

GE_farm = WindFarm(name='GE_farm',
                        wind_turbine_fleet=GE_turbine_fleet)

mc_enercon_fleet = TurbineClusterModelChain(Enercon_farm).run_model(weather)
# write power output time series to WindFarm object
Enercon_farm.power_output = mc_enercon_fleet.power_output

mc_GE_fleet = TurbineClusterModelChain(GE_farm).run_model(weather)
# write power output time series to WindFarm object
GE_farm.power_output = mc_GE_fleet.power_output

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

if plt:
    # Power output

    fig1 = plt
    fig1.plot(Enercon_farm.power_curve.wind_speed,
             Enercon_farm.power_curve.value, 'g*',
             label='Enercon farm')
    fig1.plot(GE_farm.power_curve.wind_speed,
             GE_farm.power_curve.value, 'ro',
             label='GE120 farm')
    fig1.xlabel('Wind speed in m/s')
    fig1.ylabel('Power in W')
    fig1.title('Power curve comparison')
    fig1.legend()
    fig1.show()

    fig2 = plt
    Enercon_farm.power_output.plot(legend=True, label='Enercon farm')
    GE_farm.power_output.plot(legend=True, label='GE120 farm')
    fig2.title('Power for Enercon E126 and GE120 over a year')
    fig2.xlabel('Time')
    fig2.ylabel('Power in W')
    plt.show()
