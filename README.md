Created by Ashan Ranmuthu, Thiago de Sousa Burgani and Juan P. Barberena Valencia

*****************************
WINDPOWERCALC3000 README FILE
*****************************

Contents:
I.   Introduction
II.  Requirements
III. Available Modules
IV.  WindPowerCalc3000 History Instructions
V.   WindPowerCalc3000 Forecast Instructions
VI.  Useful Links


---------------
I. INTRODUCTION
---------------
This program was created as the final project for the Programming For Engineers course (ME 396P) during the Spring 2021 semester, with Dr. Pryor as instructor.
The main purpose was to develop a program that was able to handle user input for a specific location and other parameters, such as time range, wind turbine type and financial attributes,
to calculate energy production and generate a detailed financial report for the user to review. This report would help the user decide whether the picked location is a good place to 
build a wind turbine. Furthermore, the program would allow the user to compare several turbine types at the same time to aid in the process of choosing the turbine with the best
performace at the given location. Finally, the program also includes a module to forecast energy production into the near future for a wind farm in a specific location. This would enable
the user to plan accordingly to meet power demand and the use of backup power if needed.

----------------
II. REQUIREMENTS
----------------
In order to use this program, the user needs to have the required files in the same directory where the .py files are located. Also, several packages need to be installed with the 
following commands:
  pip install windpowerlib
  pip install geopy
  pip install geocoder
  pip install meteostat
  pip install timezonefinderL
  pip install pandas        
  pip install sys
  pip install os            
  pip install datetime
  pip install requests        
  pip install json
  pip install matplotlib        
  pip install csv
  
The required file for correct function of the program is a spreadsheet called MyTurbines.csv that contains three columns: turbine_catalog_name, hub_height and amount.
Each row will represent a different turbine type, with the name extracted from the database included in the program ('turbine_type' values). The hub height is measured in meters from
the ground to the center of the hub, and the amount refers to the number of each turbine type found in a wind farm. 
It is extremely important to have the spreadsheet formatted as outlined above, or the program will not work as intended, and wrong results or program termination might occur.

------------
III. MODULES
------------
The program is divided in two parts: 
- WindPowerCalc3000 History
- WindPowerCalc3000 Forecast
Each of these parts contain several modules that perform different functions. The modules are the Weather Generation Module, the Single-Turbine Analysis Module, the Multiple-Turbine
Comparison Module, the Weather-Forecasting Module, the Wind Farm Output Forecast Module and the User Interface. All of the modules include exception handling and user-input validation
to ensure that the program runs smoothly.

-----------------------------
IV. WINDPOWERCALC3000 HISTORY
-----------------------------
First, ensure you are in the correct working directory. End should be /ME396P-AJT-simulation. Ensure the **History Plots** folder exists in the directory. The images for both single turbine and turbine comparison programs will be saved to this folder.

After cloning the repository, run the WindPowerCalc3000_History.py file. Once it is running, you will be presented with the welcome interface. Keyboard commands will be displayed with an explanation for each different command. 
IMPORTANT: In order to use the program, the user needs to download the weather data first. Type w (case sensitive) to access the Weather Generation Module.

IV-A. Weather Generation Module
Once inside the Weather Generation Module, the user will type in the desired location for analysis in the format City, State/Province, Country. Some City, State Abbreviation
combinations work, but others may not. For instance, if you type 'Denver, CO', the program will locate you in a small town in Colombia. After location input, the program will ask
for the beginning of the time frame in the format YYYY/M/D, all in separate prompts. Similarly, the program will then ask for the end of the time frame with the same format.
Once location and time range have been specified, the program will check for distance between location and the user's IP address as an input validation function. If the distance is
greater than 350 miles, the program will ask for input validation from the user. To continue, type 'y' or 'Y'. The weather download will begin, and it may take a few moments. 
Once it is done, a message will appear saying so, and the user will be presented again with the welcome instructions.

IV-B. Wind Turbine Database
To access the included turbine database, type 'db' in the welcome screen. The program will output a 60+ item list containing the manufacturer, turbine name (used in the CSV file 
mentioned in Section II), and whether curves are available for each turbine. It is important to write the turbine type exactly as it appears on this database!

IV-C. Single-Turbine Analysis Module
To access this module, type 's' in the welcome screen. If weather data hasn't been generated yet the program will produce an error message and return the user to the welcome screen. 
Once the weather data is available, the user will need to type the name of the turbine they wish to analyze. The user can always type 'db' if they forget what the exact name is.
Once the turbine type is accepted by the program, the user will need to input several parameters that include Hub Height, Construction Cost, Annual Maintenance Cost (as a percentage
of the construction cost, without the % sign) and Expected Revenue (per kWh). If the user enters '0' or just hits enter in any of these, the default value will be used, and a 
warning message will appear.
Once all the parameters are accepted, the program will perform the calculations and produce the outputs. A detailed report will be printed to the screen, containing the values for all
the parameters and then the results section, which contains the following items:
 - Total Energy Output through the time range (in MWh)
 - Total Revenue obtained through the time range
 - Total Profit at the end of the time range
 - Break-Even Point time prediction in years
The program will also show three different plots. These include the following information:
 - Plot of Power Output at each point in the time range
 - Plot of Revenue vs. Costs over the time range. If certains conditions are met, the Break-Even point will be noticeable in this plot
 - Plot of Profit over the time range

Once the user has reviewed all the information presented, they can choose whether to return to the welcome screen or to quit the program.

IV-D. Multiple-Turbine Comparison Module
To access this module, type 'c' in the welcome screen. Similarly to the single turbine module, weather data needs to be downloaded first before gaining access to this module.
Instructions regarding the required CSV file will be presented. Once the CSV file is ready in the same directory and with the correct format, the user can hit any key to advance. The
program will read the file and prompt user-input for the parameters for each turbine. Revenue per kWh will be considered the same for all turbines, since the purpose of this module
is to compare the financial performance of each turbine based on their power production and costs. Once all parameters are accepted by the program, calculations will be done and 
results displayed. The financial report will be formatted as a table containing parameters and results for each turbine type available in the CSV file. The table is easy to read
for a quick comparison of each attribute. 
Plots will only be generated if two turbine types are being compared, due to graphical space limitations.
Again, the user will be presented with the option to return to the welcome screen or to quit the program.

-----------------------------
V. WINDPOWERCALC3000 FORECAST
-----------------------------
First, ensure you are in the correct working directory. End should be /ME396P-AJT-simulation. Ensure the **Forecast Plots** folder exists in the directory. The images generated will be saved to this folder.
After cloing this repository, run the WindPowerCalc3000_Forecast.py file. The CSV file containing the turbine types and their respective parameters should already be located in the same directory. If you'd like to change the turbines, make edits to the CSV, but ensure it is **closed** before running the script.
The program will ask only for the desired location. Once the input is validated, the program will output a plot that shows the total power to be generated by all the turbines in the farm, accurate to the hour, for the next 168 hours (7 days).

----------------
VI. USEFUL LINKS
----------------
To learn more about the packages being used in this program, copy and paste the following links in your web browser:
- https://windpowerlib.readthedocs.io/en/stable/                  -- windpowerlib documentation
- https://geopy.readthedocs.io/en/stable/                         -- Geopy documentation
- https://geocoder.readthedocs.io/                                -- Geocoder documentation
- https://dev.meteostat.net/                                      -- Meteostat documentation
- https://timezonefinder.readthedocs.io/en/latest/index.html      -- Timezonefinder documentation
- https://pandas.pydata.org/docs/                                 -- Pandas documentation
- https://matplotlib.org/                                         -- Matplotlib documentation
