#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 17:02:28 2023

@author: anish
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import numpy as np
import matplotlib.colors as mcolors

# Set file path
filePath = '/Users/anish/Documents/DAE Classes/DAEN 690/Project/Sprint 3/'

# Read the Strike report data file into a DataFrame
# strikeDataset = pd.read_excel(filePath + 'STRIKE_REPORTS.xlsx')
strikeDataset = pd.read_csv(filePath + 'strike_data_clean_1.csv')
flightCountDataset = pd.read_csv(filePath + 'OPSNET_2020to2023_CSV.csv')
iataIcaoDataset = pd.read_csv(filePath + 'iata-icao.csv')

################################ STRIKE DATASET ################################
# Only keep USA 
# iataIcaoDataset = iataIcaoDataset[iataIcaoDataset['country_code'] == 'US']

# Filter rows in Stike report dataset base on US aiport code in iataIcaoDataset
# strikeDataset = strikeDataset[strikeDataset['AIRPORT_ID'].isin(iataIcaoDataset['icao'])]

# Remove rows where Airport Code is null
strikeDataset = strikeDataset.dropna(subset=['AIRPORT_ID'])

# remove all reports that are not in the contenetal USA
strikeDataset = strikeDataset[strikeDataset['AIRPORT_ID'].str.startswith('K')]

# Convert the 'Date' column to datetime format
strikeDataset['INCIDENT_DATE'] = pd.to_datetime(strikeDataset['INCIDENT_DATE'])

# Remove rows where 'Date' is before January 1, 2020
strikeDataset = strikeDataset[strikeDataset['INCIDENT_DATE'] >= '2020-01-01']


################################ FLIGHT COUNT DATASET ##########################
# Convert the 'Date' column to datetime format
flightCountDataset['Date'] = pd.to_datetime(flightCountDataset['Date'])

# Convert all but the first two columns to integers
flightCountDataset.iloc[:, 2:] = flightCountDataset.iloc[:, 2:].astype(int)

# Remove the first character from the 'AIRPORT_ID' column
strikeDataset['AIRPORT_ID'] = strikeDataset['AIRPORT_ID'].str[1:]

################################ MERGE DATASET ##########################

# Perform a join based on 'Date' and 'Airport Code'
Strikes_Flight_Count = strikeDataset.merge(flightCountDataset, left_on=['INCIDENT_DATE', 'AIRPORT_ID'], right_on=['Date', 'Facility'], how='left')

# Remove rows where 'Column1' has null values
Strikes_Flight_Count = Strikes_Flight_Count.dropna(subset=['Total Operations'])

# Save the merged DataFrame to a CSV file
Strikes_Flight_Count.to_csv('Strikes_Flight_Count.csv', index=False)

################################ VISUALIZE DATASET ##########################
# Count the number of strikes per 10,000 flights
Strikes_Flight_Count['Strikes_Per_10000_Flights'] = (
    Strikes_Flight_Count.groupby(['AIRPORT_ID', 'INCIDENT_DATE'])['AIRPORT_ID']
    .transform('size') / Strikes_Flight_Count['Total Operations'] * 10000
)

# Create a new DataFrame with the aggregated results for each airport
airport_summary = Strikes_Flight_Count.groupby('AIRPORT_ID').agg(
    Total_Strikes=pd.NamedAgg(column='Strikes_Per_10000_Flights', aggfunc='sum')
).reset_index()

# Display the result
print(airport_summary)

################################ VISUALIZE DATASET 2 ##########################
# Group by airport and sum the total number of flights
total_flights_per_airport = Strikes_Flight_Count.groupby('AIRPORT')['Total Operations'].sum().reset_index()

# Group by airport and count the total number of strikes
total_strikes_per_airport = Strikes_Flight_Count.groupby('AIRPORT').size().reset_index(name='Total_Strikes')

# Merge the two dataframes on 'AirportCode'
merged_df = pd.merge(total_flights_per_airport, total_strikes_per_airport, on='AIRPORT')

# Calculate the strikes per 10,000 flights
merged_df['Strikes_Per_10000_Flights'] = (merged_df['Total_Strikes'] / merged_df['Total Operations']) * 10000

# Display the result
print(merged_df)

# Save the merged DataFrame to a CSV file
merged_df.to_csv('Strikes_Per_10000_Flights.csv', index=False)


# Sort the DataFrame by Strikes_Per_10000_Flights in descending order
# sorted_df = merged_df.sort_values(by='Strikes_Per_10000_Flights', ascending=False)
sorted_df = merged_df.sort_values(by='Total_Strikes', ascending=False)


# Select the top 10 airports
top_10_airports = sorted_df.head(10)
top_10_airports = top_10_airports.sort_values(by='Strikes_Per_10000_Flights', ascending=False)


# Reverse the viridis colormap for the legend
cmap = plt.cm.viridis
norm = mcolors.Normalize(vmin=top_10_airports['Strikes_Per_10000_Flights'].min(), vmax=top_10_airports['Strikes_Per_10000_Flights'].max())
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, orientation='vertical', pad=0.05)
cbar.set_label('Strikes Per 10,000 Flights')

# Create a bar graph with colored bars and data labels
plt.figure(figsize=(10, 6))
bars = plt.bar(top_10_airports['AIRPORT'], top_10_airports['Strikes_Per_10000_Flights'], color=cmap(norm(top_10_airports['Strikes_Per_10000_Flights'])))
plt.xlabel('AIRPORT')
plt.ylabel('Strikes Per 10,000 Flights')
plt.title('Strikes Per 10,000 Flights for Selected Airports')
plt.xticks(rotation=45, ha='right')

# Add data labels to each bar
for bar, label in zip(bars, top_10_airports['Strikes_Per_10000_Flights']):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{int(label)}', ha='center', va='bottom')

# Add a color bar to indicate the scale
sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=top_10_airports['Strikes_Per_10000_Flights'].min(), vmax=top_10_airports['Strikes_Per_10000_Flights'].max()))
sm.set_array([])
cbar = plt.colorbar(sm, orientation='vertical', pad=0.05)
cbar.set_label('Strikes Per 10,000 Flights')

# Show the plot
plt.tight_layout()
plt.show()































