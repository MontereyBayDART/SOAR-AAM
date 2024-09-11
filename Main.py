import pandas as pd
import numpy as np
import datetime

#Read in data
raw_data = pd.read_csv('Marina.csv', dtype={
    'STATION': int,
    'NAME': object,
    'DATE': object,
    'SOURCE': object,
    'REPORT_TYPE': object,
    'CALL_SIGN': object,
    'QUALITY_CONTROL': object,
    'CIG': object,
    'GA1': object,
    'GA2': object,
    'GA3': object,
    'GD1': object,
    'GD2': object,
    'GD3': object,
    'GE1': object,
    'GF1': object,
    'OC1': object,
    'OD1': object,
    'OE1': object,
    'OE2': object,
    'OE3': object,
    'QUALITY_CONTROL.1': object,
    'VIS': object,
    'WND': object,
})

civil_twilight = pd.read_csv('CivilTwilight.csv')
weatherdata_init = raw_data
print(str(len(weatherdata_init)) + " rows")
print(raw_data.dtypes)
#Set hover test conditions.
hover_test_conditions = [
    304.8,  # minimum cloud ceiling height, meters
    4828.03,  # minimum visibility, meters
    15.433,  # maximum wind speed, meters/second * 10 (scaling factor readjustment)
    15, #minimum flight time, minutes
    3 #number of test flights desired daily
]

#Set flight test conditions.
flight_test_conditions = [
    304.8, #minimum cloud ceiling height, meters
    4828.03, #minimum visibility, meters
    51.444, #maximum wind speed, meters/s * 10 (scaling factor readjustment)
    45, #minimum flight time, minutes
    3 #number of test flights desired daily
]

airport_names = raw_data['NAME'].unique()
print(airport_names)

#Filter out columns
weather_data_selected_columns = ['NAME', 'DATE', 'REPORT_TYPE', 'CIG', 'VIS', 'WND']
selected_report_types = ['FM-15', 'FM-16']
raw_data = raw_data[weather_data_selected_columns]

#Report type filter
raw_data = raw_data[raw_data['REPORT_TYPE'].isin(selected_report_types)]
raw_data = raw_data[raw_data['NAME'] == airport_names[0]]

report_type_filter = raw_data
print(str(abs(len(report_type_filter) - len(weatherdata_init))) + " rows were removed in report type filtering ("
      + str(len(raw_data)) + " rows)")

#Quality filter
raw_data = raw_data[
    (raw_data['CIG'].str[0:5] != '99999') & (raw_data['CIG'].str[6].isin(['1', '5']))
    & (raw_data['VIS'].str[0:6] != '999999') & (raw_data['VIS'].str[7].isin(['1', '5', 'P']))
    & (raw_data['WND'].str[8:12] != '9999') & (raw_data['WND'].str[13].isin(['1', '5']))
    ]

quality_filter = raw_data
print(str(abs(len(quality_filter) - len(report_type_filter))) + " rows were removed in quality filtering ("
      + str(len(raw_data)) + " rows)")
raw_data.to_csv('raw_data_output', index=False)

#Build dataframes for analysis
conditions_table = pd.DataFrame(columns=[
    'Name', 'Date', 'CIG', 'VIS', 'WND', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'HourMinute',
    'CivilBegin', 'CivilEnd', 'CivilBegin_Hour', 'CivilBegin_Minute', 'CivilEnd_Hour', 'CivilEnd_Minute', 'CIG_Hover',
    'VIS_Hover', 'WND_Hover', 'CIG_Flight', 'VIS_Flight', 'WND_Flight', 'Hover_Clear', 'Flight_Clear'])

for index, row in raw_data.iterrows():
        conditions_table.loc[index, 'Name'] = row['NAME']
        conditions_table.loc[index, 'Date'] = row['DATE']
        conditions_table.loc[index, 'CIG'] = row['CIG']
        conditions_table.loc[index, 'VIS'] = row['VIS']
        conditions_table.loc[index, 'WND'] = row['WND']
        conditions_table.loc[index, 'Year'] = row['DATE'][:4]
        conditions_table.loc[index, 'Month'] = row['DATE'][5:7]
        conditions_table.loc[index, 'Day'] = row['DATE'][8:10]
        conditions_table.loc[index, 'Hour'] = row['DATE'][11:13]
        conditions_table.loc[index, 'Minute'] = row['DATE'][14:16]
        conditions_table.loc[index, 'HourMinute'] = row['DATE'][11:13] + row['DATE'][14:16]

        #CIG_Hover
        if float(row['CIG'][:5]) >= hover_test_conditions[0]:
            conditions_table.loc[index, 'CIG_Hover'] = True
        else:
            conditions_table.loc[index, 'CIG_Hover'] = False

        # VIS_Hover
        if float(row['VIS'][:6]) >= hover_test_conditions[1]:
            conditions_table.loc[index, 'VIS_Hover'] = True
        else:
            conditions_table.loc[index, 'VIS_Hover'] = False

        # WND_Hover
        if float(row['WND'][8:12]) <= hover_test_conditions[2]:
            conditions_table.loc[index, 'WND_Hover'] = True
        else:
            conditions_table.loc[index, 'WND_Hover'] = False

        # CIG_Flight
        if float(row['CIG'][:5]) >= flight_test_conditions[0]:
            conditions_table.loc[index, 'CIG_Flight'] = True
        else:
            conditions_table.loc[index, 'CIG_Flight'] = False

        # VIS_Flight
        if float(row['VIS'][:6]) >= flight_test_conditions[1]:
            conditions_table.loc[index, 'VIS_Flight'] = True
        else:
            conditions_table.loc[index, 'VIS_Flight'] = False

        # WND_Flight
        if float(row['WND'][8:12]) <= flight_test_conditions[2]:
            conditions_table.loc[index, 'WND_Flight'] = True
        else:
            conditions_table.loc[index, 'WND_Flight'] = False

# Convert 'YEAR' and 'DAY' columns in civil_twilight to numeric
civil_twilight = civil_twilight.apply(pd.to_numeric)

# Convert 'Year' and 'Day' columns in conditions_table to numeric
conditions_table[['Year', 'Day', 'Month', 'Hour', 'Minute', 'HourMinute']] = conditions_table[
    ['Year', 'Day', 'Month', 'Hour', 'Minute', 'HourMinute']].apply(pd.to_numeric)

conditions_table['CivilBegin'] = conditions_table['CivilBegin'].astype(str)
conditions_table['CivilEnd'] = conditions_table['CivilBegin'].astype(str)

print("done with conditions table")

for index, row in conditions_table.iterrows():
    # Filter the civil_twilight DataFrame based on 'Year' and 'Day'
    civil_filter = civil_twilight[
        (civil_twilight['YEAR'] == row['Year']) &
        (civil_twilight['DAY'] == row['Day'])
        ]

    # Extract the value based on the 'Month' column
    month_index = 2 * row['Month']  # Adjust this if needed (e.g., if it's 0-based)
    conditions_table.loc[index, 'CivilBegin'] = civil_filter.iloc[0, month_index]
    conditions_table.loc[index, 'CivilEnd'] = civil_filter.iloc[0, month_index + 1]

    conditions_table.loc[index, 'CivilBegin_Hour'] = (conditions_table.loc[index, 'CivilBegin'] // 100)
    conditions_table.loc[index, 'CivilBegin_Minute'] = (
            conditions_table.loc[index, 'CivilBegin'] - ((conditions_table.loc[index, 'CivilBegin'] // 100) * 100)
    )
    conditions_table.loc[index, 'CivilEnd_Hour'] = (conditions_table.loc[index, 'CivilEnd'] // 100)
    conditions_table.loc[index, 'CivilEnd_Minute'] = (
            conditions_table.loc[index, 'CivilEnd'] - ((conditions_table.loc[index, 'CivilEnd'] // 100) * 100)
    )

    hover_clear_conditions = [conditions_table.loc[index, 'CIG_Hover'],
                              conditions_table.loc[index, 'VIS_Hover'],
                              conditions_table.loc[index, 'WND_Hover']]

    flight_clear_conditions = [conditions_table.loc[index, 'CIG_Flight'],
                               conditions_table.loc[index, 'VIS_Flight'],
                               conditions_table.loc[index, 'WND_Flight']]

    # Hover_Clear
    if all(hover_clear_conditions):
        conditions_table.loc[index, 'Hover_Clear'] = True
    else:
        conditions_table.loc[index, 'Hover_Clear'] = False

    # Flight_Clear
    if all(flight_clear_conditions):
        conditions_table.loc[index, 'Flight_Clear'] = True
    else:
        conditions_table.loc[index, 'Flight_Clear'] = False



conditions_table[
    ['CivilBegin', 'CivilEnd', 'CivilBegin_Hour', 'CivilBegin_Minute', 'CivilEnd_Hour', 'CivilEnd_Minute']
] = conditions_table[
    ['CivilBegin', 'CivilEnd', 'CivilBegin_Hour', 'CivilBegin_Minute', 'CivilEnd_Hour', 'CivilEnd_Minute']
].apply(pd.to_numeric)

print("done with clear conditions in conditions table")
conditions_table.to_csv('conditions_table_output', index=False)

daily_table_selected_columns = ['Name', 'Year', 'Month', 'Day']
daily_table = conditions_table.drop_duplicates(subset=daily_table_selected_columns).copy()
daily_table = daily_table[daily_table_selected_columns]
daily_table['Hover_Testing_Windows'] = 0
daily_table['Flight_Testing_Windows'] = 0
daily_table['Total_Hover_Time'] = 0
daily_table['Total_Flight_Time'] = 0
daily_table['Hover_Testing_Threshold'] = False
daily_table['Flight_Testing_Threshold'] = False
daily_table = daily_table.reset_index(drop=True)
#print(daily_table.columns)
#print(daily_table.dtypes)

clear = ['Hover_Clear', 'Flight_Clear']
total_time = ['Total_Hover_Time', 'Total_Flight_Time']
total_windows = ['Hover_Testing_Windows', 'Flight_Testing_Windows']
test_conditions = [hover_test_conditions, flight_test_conditions]
testing_thresholds = ['Hover_Testing_Threshold', 'Flight_Testing_Threshold']

for index, row in daily_table.iterrows():
    test_time = [0, 0]
    time_block = [0, 0]
    daily_filter = conditions_table[(conditions_table['Name'] == daily_table.loc[index, 'Name']) &
                                    (conditions_table['Year'] == daily_table.loc[index, 'Year']) &
                                    (conditions_table['Month'] == daily_table.loc[index, 'Month']) &
                                    (conditions_table['Day'] == daily_table.loc[index, 'Day'])]
    #print(daily_filter)

    for index_filter in range(len(daily_filter) - 1):
        if index_filter + 1 < len(daily_filter):
            civil_begin_time = ((60 * daily_filter.iloc[index_filter]['CivilBegin_Hour']) +
                                daily_filter.iloc[index_filter]['CivilBegin_Minute'])
            civil_end_time = ((60 * daily_filter.iloc[index_filter]['CivilEnd_Hour']) +
                              daily_filter.iloc[index_filter]['CivilEnd_Minute'])
            daily_filter_time = (
                        (60 * daily_filter.iloc[index_filter]['Hour']) + daily_filter.iloc[index_filter]['Minute'])
            daily_filter_next_time = (
                (60 * daily_filter.iloc[index_filter + 1]['Hour']) + daily_filter.iloc[index_filter + 1]['Minute'])

            for i in range(2):
                if daily_filter.iloc[index_filter][clear[i]] == True:
                    if (daily_filter_time < civil_begin_time) & (daily_filter_next_time > civil_begin_time):
                        test_time[i] = (daily_filter_next_time - civil_begin_time)
                        time_block[i] += test_time[i]
                        daily_table.loc[index, total_time[i]] += test_time[i]  # in minutes
                    elif (daily_filter_time < civil_end_time) & (daily_filter_next_time > civil_end_time):
                        test_time[i] = (civil_end_time - daily_filter_time)
                        time_block[i] += test_time[i]
                        daily_table.loc[index, total_time[i]] += test_time[i]  # in minutes
                    elif (daily_filter_time > civil_begin_time) & (daily_filter_next_time < civil_end_time):
                        test_time[i] = (daily_filter_next_time - daily_filter_time)
                        time_block[i] += test_time[i]
                        daily_table.loc[index, total_time[i]] += test_time[i]  # in minutes
                    else:
                        test_time[i] = 0
                        daily_table.loc[index, total_windows[i]] += time_block[i] // test_conditions[i][3]
                        time_block[i] = 0
                    #print(time_block)
                else:
                    test_time[i] = 0
                    daily_table.loc[index, total_windows[i]] += time_block[i] // test_conditions[i][3]
                    time_block[i] = 0




    for i in range(2):
        if daily_table.loc[index, total_windows[i]] >= test_conditions[i][4]:
            daily_table.loc[index, testing_thresholds[i]] = True
        else:
            daily_table.loc[index, testing_thresholds[i]] = False

print("done with daily table")s
daily_table.to_csv('daily_table_output', index=False)

output = pd.DataFrame(columns = ['Airport', 'Mean Hover Windows', '% Days Hover Windows', 'Mean Flight Windows',
                      '% Days Flight Windows', 'Mean Hover Time', 'Mean Flight Time'])

for index in range(len(airport_names)):
    airport_filter = daily_table[daily_table['Name'] == airport_names[index]]
    output.loc[index, "Airport"] = airport_names[index]
    output.loc[index, "Mean Hover Windows"] = airport_filter['Hover_Testing_Windows'].mean()
    output.loc[index, "Mean Flight Windows"] = airport_filter['Flight_Testing_Windows'].mean()
    output.loc[index, "Mean Hover Time"] = airport_filter['Total_Hover_Time'].mean()
    output.loc[index, "Mean Flight Time"] = airport_filter['Total_Flight_Time'].mean()
    output.loc[index, "% Days Hover Windows"] = len(
        airport_filter[airport_filter['Hover_Testing_Threshold'] == True]) / len(airport_filter)
    output.loc[index, "% Days Flight Windows"] = len(
        airport_filter[airport_filter['Flight_Testing_Threshold'] == True]) / len(airport_filter)

print(output)

#Save to file
output.to_csv('output', index=False)



