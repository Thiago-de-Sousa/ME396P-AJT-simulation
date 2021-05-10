Created by Ashan Ranmuthu, Thiago de Sousa Burgani, and Juan P. Barberena Valencia

*****************************
WINDPOWERCALC3000 README FILE
*****************************

Contents:
 - I. Introduction
 - II. Requirements
 - III. WindPowerCalc3000_History Instructions
 - IV. WindPowerCalc3000_Forecast Instructions
 - V. Useful Links


---------------
I. INTRODUCTION
---------------
This package was created as the final project for the Application Programming For Engineers course (ME 396P) during the Spring 2021 semester with Dr. Pryor as instructor.
This package has two programs:
1. WindPowerCalc3000_History: This program helps parties interested in building wind turbines decide where and which models to build. It does this by estimating the energy production and financial performance a given turbine would have achieved under historical weather conditions in a given location. It can also provide comparative estimates for multiple turbines if desired so that users can make decisions between turbines. 
2. WindPowerCalc3000_Forecast: This program helps parties that already operate wind turbines forecast their power production over the next seven days. The parties can then compare the power production forecast with their own power demand forecasts to predict when supplemental power will be needed and when there will be excess wind energy to store.

----------------
II. REQUIREMENTS
----------------
In order to use this program, several packages need to be installed. Type the following commands into the console of your IDE to do so:

 - pip install windpowerlib
 - pip install geopy
 - pip install geocoder
 - pip install meteostat
 - pip install timezonefinderL
 - pip install pandas
 - pip install sys
 - pip install os
 - pip install datetime
 - pip install requests
 - pip install json
 - pip install matplotlib
 - pip install csv
 - pip install numpy

**The user must download all the files in this repository and keep them in the same directory at all times. (The easiest way is to download the repository code as a zip file.) Only the folder called "archived" can be deleted.**

-------------------------------------------
III. WINDPOWERCALC3000_HISTORY INSTRUCTIONS
-------------------------------------------
Open WindPowerCalc3000_History.py.

Once it is running, you will be presented with the welcome interface which will ask you to type a letter to open a module. Each valid letter and its corresponding module is shown below. (The welcome interface shows these instructions.)
 - 'w'  Weather Module
 - 'db' Access Wind Turbine Database
 - 's'  SingleTurbine Analysis Module
 - 'c'  Turbine Comparison Module
 - 'q'  Quits the program.

IMPORTANT: The program must first download weather data for the user's desired location before generating useful plots, so the user's first input should be 'w'.

**A. Weather Module**

This module is accessed by typing 'w' after the welcome instructions. In this module, the user will type in the desired location for analysis. For example: "Sacramento, CA". Another example: "Paris, France". The program will check the distance between the specified location and the user's IP address. If the distance is greater than 350 miles, the program will display this distance and ask whether to proceed. This can help verify whether the program has selected the right location. (For example, it will inform a user in Texas if the program is looking for Paris, France when the user actually wanted Paris, Texas.)
The program will then ask for the beginning and end of the historical time frame for which plots should be generated. **Only data since the year 2000 can be reliably downloaded.** The weather data download will begin. A longer time frame will lead to a longer download time. A time frame of one year will typically download in ten seconds. Some locations will have no available data.
After downloading, a message will appear, and the user will be presented again with the welcome instructions for how to proceed.

**B. Access Wind Turbine Database**

The windpowerlib package's wind turbine database is accessed by typing 'db' after the welcome instructions. The program will automatically display the database in chart form. (The database is stored in turbine_database.csv.) The turbine_type column shows the names of the models.

**C. Single Turbine Analysis Module**

This module is accessed by typing 's' after the welcome instructions. If weather data hasn't been generated yet the program will inform the user and return to the welcome instructions.

The user will be prompted for the name of the turbine model they wish to analyze. The turbine model name must excatly match the name as it is shown in the turbine_type column of the database. The user can type 'db' to see the database.
Once the turbine type is accepted, the user will need to input the turbine hub height, construction cost (USD), annual maintenance cost (as a percentage of the construction cost, without the % sign), and expected revenue (USD per kWh produced). If the user enters '0' or just hits enter in any of these, a default value will be used, and a 
warning message will appear.

The program then performs the calculations and produces the following plots. These plots are are also saved as png images to the directory "History Plots\Single Turbine History Plots" which contains example plots that can be deleted if desired.
1. Power Output (Power vs Time) (uses calculation functions from windpowerlib package)
2. Financial Analysis (Revenue and Costs vs Time)
3. Profit (Profit vs Time)

A detailed report will also be printed to the screen and contain the following user-inputed parameters:
 - Location
 - Length of time range
 - Construction Cost
 - Annual Maintenance Cost
 - Revenue per kWh

The report will also contain the following calculations:
 - Total Energy Output through the time range.
 - Total Revenue obtained through the time range.
 - Total Profit obtained through the time range.
 - Break Even: a prediction of the time needed to break even on construction cost and annual maintenance costs. (Only accurate if time range is at least 1 year.)

Once the user has reviewed all the information presented, they can choose whether to return to the welcome screen or to quit the program.

**D. Turbine Comparison Module**

This module is accessed by typing 'c' after the welcome instructions. It is very similar to the Single Turbine Analysis Module. If weather data hasn't been generated yet the program will inform the user and return to the welcome instructions.

The turbine models to compare are obtained from the TurbinesToCompare.csv file. Simply update that file with the turbine model names and the hub heights at which you would build them. The turbine model names must exactly match entries in the turbine_database.csv file. Once the CSV file is ready with the correct format and turbine model names, press enter.
The user must then follow prompts to enter the expecte revenue (USD per kWh produced), construction cost (USD), and annual maintenance cost (as a percentage of the construction cost, without the % sign).

The program then performs the calculations and produces the following plots. These plots are are also saved as png images to the directory "History Plots\Turbine Comparison History Plots" which contains example plots that can be deleted if desired.
1. Power Output (Power vs Time) (uses calculation functions from windpowerlib package)
2. Financial Analysis (Revenue and Costs vs Time) (only for two turbine models or less)
3. Profit (Profit vs Time) (only for two turbine models or less)

A detailed report will also be printed to the screen and contain the following user-inputed parameters:
 - Location
 - Length of time range
 - Revenue per kWh

The report will also print a table that provides the following parameters for every turbine:
 - Turbine model name
 - Construction Cost
 - Maintenance Cost
 - Energy produced in the time range
 - Revenue obtained through the time range
 - Profit obtained through the time range
 - Break Even: a prediction of the time needed to break even on construction cost and annual maintenance costs. (Only accurate if time range is at least 1 year.)

Once the user has reviewed all the information presented, the generated plot png images must be placed in a folder to prevent them from being overridden the next time this module is used. Then the user can choose whether to return to the welcome screen or to quit the program. 

-------------------------------------------
IV. WINDPOWERCALC3000_FORECAST INSTRUCTIONS
-------------------------------------------
Open WindPowerCalc3000_Forecast.py

The MyTurbines.csv file represents your wind farm. It currently has data for an wind farm. The first column is titled turbine_catalog_name. Put the names of the turbine models in your wind farm. Check the turbine_database.csv file for all the turbine models that this package supports. In the second column, put the hub height of each of your turbine models. If you have multiple turbines of the same model that were built at different hub heights, you must create a new row for each combination of turbine model and hub height. For each row in the third column, put the number of turbines in your wind farm that are of that row's model and hub height. Save and close the MyTurbines.csv file.

Run the WindPowerCalc3000_Forecast.py file. Enter the desired location. For example: "Sacramento, CA". Another example: "Paris, France". Some locations will have no available data.

The program will output a plot of the seven day hourly power generation forecast for your wind farm (this uses calculation functions from windpowerlib package). An image of this plot will be saved to the "Forecast Plots" folder. This folder contains example plots that can be deleted if desired.

----------------
V. USEFUL LINKS
----------------
To learn more about the main packages being used in this program, copy and paste the following links in your web browser:
- https://windpowerlib.readthedocs.io/en/stable/                  -- windpowerlib documentation
- https://geopy.readthedocs.io/en/stable/                         -- Geopy documentation
- https://geocoder.readthedocs.io/                                -- Geocoder documentation
- https://dev.meteostat.net/                                      -- Meteostat documentation
- https://timezonefinder.readthedocs.io/en/latest/index.html      -- Timezonefinder documentation
- https://pandas.pydata.org/docs/                                 -- Pandas documentation
- https://matplotlib.org/                                         -- Matplotlib documentation
