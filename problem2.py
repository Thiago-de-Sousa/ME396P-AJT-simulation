import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from windpowerlib import ModelChain, WindTurbine
import os
import requests

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
weather = get_weather_data(filename='weather.csv', datapath='')

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
print(totalPowerPandasSeries)

# Plotting
plt.figure()
# listOfModelChains[0].power_output.plot(legend=True, label='Enercon E126')
# listOfModelChains[1].power_output.plot(legend=True, label='GE120')
totalPowerPandasSeries.plot()
plt.title('Power for Enercon E126 and GE120 over a year')
plt.xlabel('Time')
plt.ylabel('Power in W')
# plt.show()


    
# csvdata[0]
# turbinesDict = {}
# n=0
# for turbine in turbinesList:
#     turbinesDict[n] = {'turbine_type': turbine, hub_height: 

# enercon_e126 = {
#     'turbine_type': "E-126/4200",
#     'hub_height': 135}

