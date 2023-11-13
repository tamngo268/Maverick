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

# Set file path
filePath = '/Users/anish/Documents/DAE Classes/DAEN 690/Project/Sprint 3/'

# Read the Strike report data file into a DataFrame
strikeDataset = pd.read_excel(filePath + 'STRIKE_REPORTS.xlsx')
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
# Convert all but the first two columns to integers
flightCountDataset.iloc[:, 2:] = flightCountDataset.iloc[:, 2:].astype(int)


# Perform a join based on 'Date' and 'Airport Code'
merged_df = strikeDataset.merge(flightCountDataset, left_on=['INCIDENT_DATE', 'AIRPORT_ID'], right_on=['Date', 'Facility'], how='left')

# Merge the DataFrames based on different column names
merged_df = flightCountDataset.merge(iataIcaoDataset, left_on='Facility', right_on='iata', how='inner')


# Drop the specified columns
merged_df = merged_df.drop(columns=['country_code', 'region_name', 'iata', 'icao', 'airport'])

# Save the merged DataFrame to a CSV file
merged_df.to_csv('merged_data.csv', index=False)

################################ MAP  ################################

# Create a GeoDataFrame for airport locations
gdf = gpd.GeoDataFrame(
    merged_df, geometry=gpd.points_from_xy(merged_df.longitude, merged_df.latitude))

# Create a heatmap using seaborn
sns.set()
heat_map = sns.heatmap(merged_df.pivot_table('Total Operations', 'Facility', 'Facility'))

# Create a folium map centered on the USA
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

# Add the heatmap layer to the map
m.add_child(heat_map)

# Display the map
m.save('heatmap.html')  # Save the map to an HTML file

################################ MAP ################################

