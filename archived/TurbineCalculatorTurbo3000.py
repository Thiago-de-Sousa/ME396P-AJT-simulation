# Copyright Thiago de Sousa, Ashan Ran, and Juan Barbarena
# under the MIT license

# Turbine Calculator Turbo 3000 v1: the ultimate turbine calculator with
# historical weather data

# Required installed packages:
    # pandas, geopy, windpowerlib, geocoder, meteostat, datetime, 
    # timezonefinderL, matplotlib, os, sys, requests
    
# Initial process: user input on desired location, timeframe and daily/hourly

# import necessary packages
# Data packages
import os
import sys
import pandas as pd
import requests
from windpowerlib import ModelChain, WindTurbine, get_turbine_types
from matplotlib import pyplot as plt

from geopy.distance import geodesic
import geocoder

# Forecast packages
import datetime
from timezonefinderL import TimezoneFinder as TZFind
from meteostat import Point, Hourly


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


# Parameters for the model
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
    
plt.close('all')

# Dummy variable for the while loop to begin    
turbine = 'a'
weather = None

# Program info and instructions for the user
print(29*'*')
print('TURBINE CALCULATOR TURBO 3000')
print(29*'*')
print()
print('Instructions:')
print("To download weather data for a specific location, type 'w'")
print("If you wish to analyze one turbine, type 's'")
print("If you wish to compare two turbines, type 'c'")
print("If you wish to see the turbine database, type 'db'")
print("If you wish to exit, type 'q' now.")
print()
print("NOTE: You must first download weather data before turbine analysis.")
print()

counterr = 0
# Loop to ensure valid input from the user and to perform the desired function
while turbine != 'q':
    
    #if the user is doing a second calculation, remind them of the instructions.
    if counterr != 0:
        print()
        print()
        print('Instructions:')
        print("To download weather data for a specific location, type 'w'")
        print("If you wish to analyze one turbine, type 's'")
        print("If you wish to compare two turbines, type 'c'")
        print("If you wish to see the turbine database, type 'db'")
        print("If you wish to exit, type 'q' now.")
    counterr+=1
    
    turbine = input("What do you wish to do? ")
    
    if turbine == 'q':
        print("Program exited.")
        break
    elif turbine == 'w':
        print()
        print("WEATHER MODULE")
        print(14*'-')
        print("Instructions: ")
        print("Fill in all the required data for weather history retrieval")
        print()

        # User inputs: 
        desired_loc = str(input('Desired location: '))
        start_year = input('Start Year: ')
        start_month = input('Month (as number 1-12): ')
        start_day = input('Day: ')
        end_year = input('End Year: ')
        end_month = input('Month (as number 1-12): ')
        end_day = input('Day: ')
        
        # # Just for testing:
        # desired_loc = 'Sacramento'
        # start_year = '2021'
        # start_month = '1'
        # start_day = '1'
        # end_year = '2021'
        # end_month = '2'
        # end_day = '28'
        
        try:
            start_year,start_month,start_day = eval(start_year), eval(start_month), eval(start_day)
            end_year,end_month,end_day = eval(end_year), eval(end_month), eval(end_day)
        except NameError:
            sys.exit('\n','Invalid input. Please try again')
        
        # Handling too old data and users from the future that don't know 
        # the gregorian calendar
        
        # Basic ones first
        if start_year < 2000 or start_year > end_year or not isinstance(start_year,int):
            start_year = 2000
            print('\n','Warning: Fetching the data will likely take a long time')
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
                print('\n','Warning: erroneous dates input. Single day will be obtained')
        
        if end_year == datetime.datetime.now().year:
            if end_month > datetime.datetime.now().month:
                end_month = datetime.datetime.now().month
            if end_month == datetime.datetime.now().month:
                if end_day > datetime.datetime.now().day:
                    end_day = datetime.datetime.now().day
                    print('\n',"Warning: if you'd like to use predicted data", 
                          ' please refer to the FutureGainsTurbineGang model')
        
           
        # Handling location
        try:
            Location = geocoder.osm(desired_loc)
            desired_lat_long = Location.latlng
            lat, long = round(desired_lat_long[0],2), round(desired_lat_long[1],2)
        except NameError:
            # sys.exit('Please install geocoder before proceeding')
            break
        except TypeError:
            # sys.exit('Please enter a valid location')
            break
        
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
            if not(YesorNo == 'Y' or YesorNo == 'y'):
                # sys.exit('Exiting program.')
                print('Program exited.')
                break
        
        # Handling start year, end year, and standardized timezone
        tf = TZFind()
        tz = tf.timezone_at(lng=long, lat=lat)
        start = datetime.datetime(start_year,start_month,start_day)
        end = datetime.datetime(end_year,end_month,end_day)
        print()
        print("Downloading weather data, please wait...")
        
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
        data = pd.concat([pd.DataFrame(heights_row),w_data_format],
                                           ignore_index=False)
        # In case of missing data:
        data.loc[data["pressure"].isnull(),'pressure'] = 101500
        data.loc[data["temperature"].isnull(),'temperature'] = 298
        data.loc[data["wind_speed"].isnull(),'wind_speed'] = 0
        data.to_csv('Test_file.csv')
        print("Done! Writing data to CSV file...")
        # Read weather data from csv
        try:
            weather = get_weather_data(filename='Test_file.csv', datapath='')
            print("Done!",'\n')
        except IndexError:
            print('\n','Sorry, the chosen location currently is not in the weather database. Please try a different location')
        continue
    elif turbine == 'db':
        print()
        df=get_turbine_types(print_out=True)
        continue
    
    elif turbine == 's':
        df = get_turbine_types(print_out = False)
        turb_correct = False
        power_gen = []
        revenue_list = []
        cost_list = []
        profit_list = []
        cum_revenue = []
        cum_profit = []
        
        if weather is None:
                print("No weather data generated yet! Please do this first...")
                continue
        else:
            pass
        
        print()
        print("SINGLE TURBINE ANALYSIS MODULE")
        print(30*"-")
        
        # User input of turbine to analyze. Loop to ensure valid turbine name is entered
        while turb_correct == False:
            turb_name = input("Enter the name of the turbine you wish to analyze exactly as it appears in the 'turbine_type' column of the database. Or enter 'db' to see the database: ")
            # turb_name = input("To see turbine database, type 'db'. The name of a turbine is under the turbine_type column")
            if turb_name in df.values:
                turb_correct = True
            elif turb_name == 'db':
                df=get_turbine_types(print_out=True)
                continue
            else:
                print()
                # print("This turbine is not in the database.")
                YesorNo = input('This turbine is not in the database. The turbine database has turbine names in the ''turbine_type'' column. Would you like to see the turbine database? (Y/N): ')
                if (YesorNo == 'Y') or  (YesorNo == 'y'):
                    print()
                    df=get_turbine_types(print_out=True)
                    
                continue
            
            # Parameter input from user. If no value is entered, default values will be used   
            hub_height = input("Enter the hub height for the turbine (meters): ")
            if hub_height == '0' or hub_height == '':
                print("WARNING! Default value will be used...")
                hub_height = 135
            else:
                hub_height = int(hub_height)

            ccost = input('Enter the construction cost (USD) for a single {} turbine: '.format(turb_name))
            if ccost == '0' or ccost == '':
                ccost = 10000000
                print("WARNING! Default value will be used...",ccost)
            else: 
                ccost = eval(ccost)

            mfactor = (input("Enter the annual maintenance cost as a percentage of the construction cost (don't include the % symbol): "))
            if mfactor == '0' or mfactor == '':
                mfactor = 0.02
                print("WARNING! Default value will be used...",mfactor)
            else:
                mfactor = float(mfactor) / 100

            revenue = (input("Enter the expected revenue per kWh: "))
            if revenue == '0' or revenue == '':
                print("WARNING! Default value will be used...")
                revenue = 0.07
            else:
                revenue = float(revenue)
            
            # #Just for testing:
            # hub_height = 135
            # ccost = 3e6
            # mfactor = 0.02
            # revenue = 0.07
            
            
            
            print()
            print()
            
            turbine_data = {'turbine_type': turb_name,
                            'hub_height': hub_height,
                            'construction_cost': ccost,
                            'maint_cost': mfactor, 
                            'revenue': revenue}
            
            # Windpowerlib model to calculate power output
            turbine_model = WindTurbine(**turbine_data)
            mc_turbine = ModelChain(turbine_model, **modelchain_data).run_model(weather)
            turbine_model.power_output = mc_turbine.power_output
                
        # Calculation of financial data for the specified power output and turbine data
        for i in range(0,len(turbine_model.power_output)):
            power_gen.append(turbine_model.power_output.iloc[i])
            cost_list.append(turbine_data['construction_cost'] + (((i+1)*turbine_data['maint_cost']/(365*24)))*turbine_data['construction_cost'])
        for item in power_gen:
            revenue_list.append(turbine_data['revenue'] * item / 1000)
        for i in range(0,len(revenue_list)):
            profit_list.append(revenue_list[i] - cost_list[i])
            if i == 0:
                cum_revenue.append(revenue_list[i])
                cum_profit.append(revenue_list[i] - cost_list[i])
            else:
                cum_revenue.append(revenue_list[i] + cum_revenue[i-1])
                cum_profit.append(revenue_list[i] + cum_revenue[i-1] - cost_list[i])
        time_range = len(power_gen) / (24*365)
        tot_revenue = sum(revenue_list)
        tot_costs = cost_list[-1]
        
        # Results report printed to the screen
        print((27 + len(turb_name))*'-')
        print("Analysis for {} wind turbine".format(turb_name))
        print((27 + len(turb_name))*'-')
        print()
        print("Location:", Location)
        print("Total time analyzed:", '{:.1f}'.format(time_range), 'years')
        print("Construction Cost for Turbine: $", turbine_data['construction_cost'])
        print("Hub Height: ", turbine_data['hub_height'], 'm')
        print("Annual Maintenance Cost: $", int(turbine_data['construction_cost']*turbine_data['maint_cost']))
        print("Revenue per kWh: $", turbine_data['revenue'])
        print()
        print("Total Energy Output:",'{:.0f}'.format(sum(power_gen)/1000000), "MWh")
        print("Total Revenue over the time range: $", '{:.0f}'.format(tot_revenue))
        print("Total Profit over the time range: $", '{:.0f}'.format(tot_revenue - tot_costs))
        print("Break-Even Point reached in ",'{:.2f}'.format(turbine_data['construction_cost'] / ((tot_revenue / time_range) - turbine_data['construction_cost']*turbine_data['maint_cost'])), 'years')
        
        # Plot of power output and financial results
        
        
        if plt:
            plt.close('all')
            turbine_model.power_output.plot()
            plt.title('Power Output for {}'.format(turb_name))
            plt.xlabel('Time')
            plt.ylabel('Power in W')
            plt.show()
            
            plt.figure(3)
            plt.plot(list(weather.index.to_pydatetime()), cum_revenue, label = "Revenue")
            plt.plot(list(weather.index.to_pydatetime()), cost_list, label = "Costs")
            plt.legend()
            plt.xlabel('Time')
            plt.xticks(rotation = 45)
            plt.ylabel("USD")
            plt.title("Financial Analysis for {}".format(turb_name))
            plt.show()
            
            plt.figure(4)
            plt.plot(list(weather.index.to_pydatetime()), cum_profit)
            plt.xlabel('Time')
            plt.xticks(rotation = 45)
            plt.ylabel("USD")
            plt.title("Profit for {}".format(turb_name))
            plt.show()  
        
        print()
        YesNo = input("Do you want to continue using the program? (Y/N): ")
        if YesNo == ('Y' or 'y'):
            continue
        else:
            print("Program exited.")
            break
    
    elif turbine == 'c': 
        ccost_list = []
        mfactor_list = []
        revenue_list = []
        power_gen_list = []
        revenue_comparison = []
        cost_comparison = []
        profit_comparison = []
        cum_revenue_comparison = []
        cum_profit_comparison = []
        tot_revenue = []
        tot_costs = []
        maint_list = []
        tot_energy = []
        tot_profit = []
        breakeven = []
        power_gen = []
        totalrevenue_list = []
        cost_list = []
        profit_list = []
        cum_revenue = []
        cum_profit = []
        
        if weather is None:
                print("No weather data generated yet! Please do this first...")
                continue
        else:
            pass
        
        # Further instructions for the user
        print()
        print("TURBINE COMPARISON MODULE")
        print(25*'-')
        print("Instructions: ")
        print("This module uses a file called TurbinesToCompare.CSV (in the same directory as this program). "
              "Please update that CSV file with the turbines you wish to compare and the desired respective hub heights. "
              "To see the database of available turbines, refer to turbine_database.csv (in the same directory as this program).")

        print()
        print("NOTE: Financial Plots are available only when comparing two turbines.")           
        access = input("If you have the CSV file ready, press enter to continue... ")
        
        # Turbine list population from user CSV file
        csvdata = pd.read_csv('TurbinesToCompare.csv')
        turbinesList = csvdata.turbine_catalog_name.to_numpy().tolist()
        hubHeightsList = csvdata.hub_height.to_numpy().tolist()
        
        listOfDicts = []
        n=0
        for turbine in turbinesList:
            listOfDicts.append({'turbine_type': turbine, 'hub_height': hubHeightsList[n]})
            n+=1
        
        n=0
        listOfWindTurbines = []
        for elem in listOfDicts:
            listOfWindTurbines.append(WindTurbine(**elem))
            n+=1
            
        n=0
        listOfModelChains = []
        for elem in listOfWindTurbines:
            listOfModelChains.append(ModelChain(listOfWindTurbines[n], **modelchain_data).run_model(weather))
            n+=1

        listOfPowerOutputs = []
        for elem in listOfModelChains:
            listOfPowerOutputs.append(elem.power_output)
            
        # Parameter input from the user. If not value is entered, defaults will be used
        revenue = (input("Enter the expected revenue (USD) per kWh: "))  
        if revenue == '0' or revenue == '':
                print("WARNING! Default value will be used...")
                revenue_list.append(0.07)
        else:
                revenue_list.append(float(eval((revenue))))
                            
        for j in range(0, len(listOfDicts)):
            ccost = input('Enter the construction cost (USD) for a single {} turbine (scientific notation like 4.5e7 is ok): '.format(listOfDicts[j]['turbine_type']))
            if ccost == '0' or ccost == '':
                print("WARNING! Default value will be used...")
                ccost_list.append(10000000)
            else: 
                ccost_list.append(int(eval(ccost)))
                
            mfactor = (input("Enter the annual maintenance cost as a percentage of the construction cost (don't include the % symbol): "))
            if mfactor == '0' or mfactor == '':
                print("WARNING! Default value will be used...")
                mfactor_list.append(0.02)
            else:
                mfactor_list.append(float(eval((mfactor)) / 100))
                
    
            # Power Output calculations
            for i in range(0,len(listOfModelChains[j].power_output)):
                power_gen.append(listOfModelChains[j].power_output.iloc[i])
                cost_list.append(ccost_list[j] + (((i+1)*mfactor_list[j]/(365*24)))*ccost_list[j])
            for item in power_gen:
                totalrevenue_list.append(revenue_list[0] * item / 1000)
            for i in range(0,len(totalrevenue_list)):
                profit_list.append(totalrevenue_list[i] - cost_list[i])
                if i == 0:
                    cum_revenue.append(totalrevenue_list[i])
                    cum_profit.append(totalrevenue_list[i] - cost_list[i])
                else:
                    cum_revenue.append(totalrevenue_list[i] + cum_revenue[i-1])
                    cum_profit.append(totalrevenue_list[i] + cum_revenue[i-1] - cost_list[i])
            
            # Financial Data Calculations
            power_gen_list.append(power_gen[:])
            revenue_comparison.append(totalrevenue_list[:])
            cost_comparison.append(cost_list[:])
            profit_comparison.append(profit_list[:])
            cum_revenue_comparison.append(cum_revenue[:])
            cum_profit_comparison.append(cum_profit[:])
            
            power_gen.clear()
            totalrevenue_list.clear()
            cost_list.clear()
            profit_list.clear()
            cum_revenue.clear()
            cum_profit.clear()
            
            time_range = len(power_gen_list[0]) / (24*365)
            maint_list.append((int(ccost_list[j] * mfactor_list[j])))
            tot_energy.append((sum(power_gen_list[j]) / 1000000))
            tot_revenue.append((sum(revenue_comparison[j])))
            tot_costs.append(cost_comparison[j][-1])
            tot_profit.append((tot_revenue[j] - tot_costs[j]))
            breakeven.append((ccost_list[j] / ((tot_revenue[j] / time_range) - ccost_list[j]*mfactor_list[j])))
            

    
        # Results Report printed to screen in tabular format    
        print(24*'-')
        print("Wind Turbine Comparison")
        print(24*'-')
        print()
        print("Location:", Location)
        print("Total time analyzed:", '{:.1f}'.format(time_range), 'years')
        print("Revenue per kWh: $", revenue_list[0])
        print()
        print("{:^11} {:^10} {:^11} {:^12} {:^12} {:^10} {:^7}".format('Turbine', 'Const.($)', 'Maint.($)', 'Energy(MWh)', 'Revenue($)', 'Profit($)', 'Break Even(Yr)'))
        for turbine, ccost, maint, energy, revenue, profit, be_point in zip(turbinesList, ccost_list, maint_list, tot_energy, tot_revenue, tot_profit, breakeven):
            print("{:^11} {:^10} {:^11} {:^12.0f} {:^12.0f} {:^10.0f} {:^7.2f}".format(turbine, ccost, maint, energy, revenue, profit, be_point))
                    
          
        try:
            from matplotlib import pyplot as plt
        except ImportError:
            plt = None
        
        if plt:
            # Plot of power outputs for all compared turbines
            for j in range(0, len(listOfDicts)):
                listOfModelChains[j].power_output.plot(legend = True, label = listOfDicts[j]['turbine_type'])
            plt.title('Power Output Comparison')
            plt.xlabel('Time')
            plt.ylabel('Power in W')
            plt.show()
            
            # Plots of fiancial data for only two compared turbines
            if len(listOfDicts) == 2:
                
                plt.figure(3)
                plt.suptitle("Financial Analysis")
                plt.subplot(1, 2, 1)
                plt.plot(list(weather.index.to_pydatetime()), cum_revenue_comparison[0], label = "Revenue")
                plt.plot(list(weather.index.to_pydatetime()), cost_comparison[0], label = "Costs")
                plt.legend()
                plt.xlabel('Time')
                plt.xticks(rotation = 60)
                plt.ylabel("USD")
                plt.title("{}".format(listOfDicts[0]['turbine_type']))
                plt.subplot(1, 2, 2)
                plt.plot(list(weather.index.to_pydatetime()), cum_revenue_comparison[1], label = "Revenue")
                plt.plot(list(weather.index.to_pydatetime()), cost_comparison[1], label = "Costs")
                plt.legend()
                plt.xlabel('Time')
                plt.xticks(rotation = 60)
                plt.title("{}".format(listOfDicts[1]['turbine_type']))
                plt.tight_layout()
                plt.show()
                
                plt.figure(4)
                plt.suptitle("Profit Comparison")
                plt.subplot(1, 2, 1)
                plt.plot(list(weather.index.to_pydatetime()), cum_profit_comparison[0])
                plt.xlabel('Time')
                plt.xticks(rotation = 60)
                plt.ylabel("USD")
                plt.title("{}".format(listOfDicts[0]['turbine_type']))
                plt.subplot(1, 2, 2)
                plt.plot(list(weather.index.to_pydatetime()), cum_profit_comparison[1])
                plt.xlabel('Time')
                plt.xticks(rotation = 60)
                plt.title("{}".format(listOfDicts[1]['turbine_type']))
                plt.tight_layout()
                plt.show()
            else:
                print()
                print("WARNING! Financial Comparison Plots are not available for more than two turbines... ")
        
        print()
        YesNo = input("Do you want to continue using the program? (Y/N): ")
        if YesNo == ('Y' or 'y'):
            continue
        else:
            print("Program exited.")
            break
    

    else:
        print()
        print("Invalid input.")
        continue
