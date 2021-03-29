#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 21:18:33 2021

@author: thiago
"""

# Scratch for windpowerlib

import os
import pandas as pd
import requests
from windpowerlib import ModelChain, WindTurbine

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

# Get specific turbine
enercon_e126 = {
    'turbine_type': "E-126/4200",
    'hub_height': 135}

GE_120 = {
    'turbine_type': "GE120/2500",
    'hub_height': 135}

e126 = WindTurbine(**enercon_e126)
GE_turb = WindTurbine(**GE_120)

modelchain_data = {
    'wind_speed_model': 'logarithmic',      # 'logarithmic' (default),
                                            # 'hellman' or
                                            # 'interpolation_extrapolation'
    'density_model': 'ideal_gas',           # 'barometric' (default), 'ideal_gas'
                                            #  or 'interpolation_extrapolation'
    'temperature_model': 'linear_gradient', # 'linear_gradient' (def.) or
                                            # 'interpolation_extrapolation'
    'power_output_model':
        'power_curve',          # 'power_curve' (default) or
                                            # 'power_coefficient_curve'
    'density_correction': True,             # False (default) or True
    'obstacle_height': 0,                   # default: 0
    'hellman_exp': None                     # None (default) or None
}                    

# initialize ModelChain with own specifications and use run_model method to
# calculate power output
mc_e126 = ModelChain(e126, **modelchain_data).run_model(
    weather)
mc_GE = ModelChain(GE_turb, **modelchain_data).run_model(
    weather)
# write power output time series to WindTurbine object
e126.power_output = mc_e126.power_output
GE_turb.power_output = mc_GE.power_output

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

if plt:
    e126.power_output.plot(legend=True, label='Enercon E126')
    GE_turb.power_output.plot(legend=True, label='GE120')
    plt.title('Power for Enercon E126 and GE120 over a year')
    plt.xlabel('Time')
    plt.ylabel('Power in W')
    plt.show()
    
    # Power coefficients
    fig2 = plt
    fig2.plot(e126.power_coefficient_curve.wind_speed,
             e126.power_coefficient_curve.value, 
             label='Enercon')
    fig2.plot(GE_turb.power_coefficient_curve.wind_speed,
             GE_turb.power_coefficient_curve.value, 
             label='GE 120')
    fig2.xlabel('Wind speed in m/s')
    fig2.ylabel('Power coefficient')
    fig2.title('Power coefficient comparison')
    fig2.legend()
    fig2.show()
    
    # Power output

    fig3 = plt
    fig3.plot(e126.power_curve.wind_speed,
             e126.power_curve.value, 
             label='Enercon')
    fig3.plot(GE_turb.power_curve.wind_speed,
             GE_turb.power_curve.value, 
             label='GE 120')
    fig3.xlabel('Wind speed in m/s')
    fig3.ylabel('Power in W')
    fig3.title('Power curve comparison')
    fig3.legend()
    fig3.show()