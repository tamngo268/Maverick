# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 12:34:17 2023

This script was written to generate a dashboard with many different components
to provide the partner with enhanced visualizations to better represent the
data in the National Wildlife Strike Database.

@author: GMU 
"""

#%% Import libraries
import dash_bootstrap_components as dbc
from dash import Dash, dcc, Input, Output, html, no_update, ctx, dash_table
import plotly.express as px
import pandas as pd
import os

#%% Change default renderer to browser
import plotly.io as pio
pio.renderers.default = 'browser'

#%% Markdown text for footer of dashboard
about_md = '''
### Overview
Team Maverick | Team Members: Anish Shrestha, Deepti Khandagale, Mitch Boehm, 
Spencer Liao, Tam Ngo
\nProfessor: Robert Kraig
\nPartner: Federal Aviation Administration (FAA) Airport Technology Research and 
Development (ATR) Branch

Aircraft collisions caused by birds and other wildlife have been an ongoing 
safety concern for the aviation industry. The Federal Aviation Administration 
(FAA) National Wildlife Strike Database (NWSD) includes about 284,000 reports 
of wildlife strikes from 1990 to 2023. The database contains 100 variables 
ranging from incident date and time, airport information, aircraft information, 
environment conditions, impact and damage information, wildlife information, 
and reporter information. The NWSD is used by airports, researchers, and city 
planners to better understand the economic cost of wildlife strikes, the scale 
of safety issues, and the nature of the problems. To further promote usage and 
provide valuable insight, the project partner has commissioned the team to analyze 
the NWSD data, integrate it with other data sources, and create dashboards and 
visualizations that allow users to conduct on-demand preliminary analyses from 
the user interface. The project team conducted exploratory data analysis of the 
NWSD along with FAA Operations Network flight count data and Visual Crossing 
weather data. We discovered valuable insights such as the “en route” phase of 
flight resulted in the most injuries and fatalities, unknown small and medium 
birds were involved in most incidents, business aircraft incurred the most 
damage costs, and more. The team delivered prototype dashboards containing 
visualizations that allow users to explore them using filter and drill-down 
features and quickly identify trends and patterns.
'''

#%% Array of states
states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 
          'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 
          'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 
          'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']


#%% Read data from pickle
data = pd.read_pickle(os.path.join(os.getcwd(), '..\Data\strike_reports.pkl'))

#%% Parse out null airport ids and filter to just US airport codes
data = data.loc[~data['AIRPORT_ID'].isnull()]
data_us = data[(data['AIRPORT_ID'].str.startswith('K')) | (data['AIRPORT_ID'].str.startswith('P'))]
mask = data_us['AIRPORT_ID'].str.findall('(\S{4,})').astype(bool)
data_us = data_us[mask].reset_index(drop=True)

#%% Find min year and max year in data
min_year = min(data.INCIDENT_YEAR)
max_year = max(data.INCIDENT_YEAR)

# Set max tick to one plus year for odd years
if max_year % 2 == 1:
    max_tick = max_year + 1

#%% Function to filter data frame by years
def filterDfByYear(start, stop):
    temp = data[data['INCIDENT_YEAR'].between(start, stop)]
    df = pd.DataFrame(temp.groupby(['STATE', 'AIRPORT', 'AIRPORT_ID', 'SPECIES', 'INCIDENT_YEAR', 'LATITUDE', 'LONGITUDE']).size()).reset_index()
    df = df.rename(columns={0: 'Incidents', 'STATE': 'State', 'AIRPORT': 'Name', 
                            'AIRPORT_ID': 'Airport ID', 'SPECIES': 'Species',
                            'INCIDENT_YEAR': 'Year', 'LATITUDE': 'Latitude',
                            'LONGITUDE': 'Longitude'})

    return df

#%% Create data frames for each plot and part of dashboard
df_main = filterDfByYear(min_year, max_year)
df_main = df_main[df_main['State'].isin(states)].reset_index(drop=True)
df_main = df_main.groupby('State').sum().reset_index()
df_main = df_main.drop(columns=['Airport ID', 'Name', 'Species', 'Year', 'Latitude', 'Longitude'])

df_line = filterDfByYear(min_year, max_year)
df_line = df_line[df_line['State'].isin(states)].reset_index(drop=True)
df_line = df_line.groupby('Year').sum().reset_index()
df_line = df_line.drop(columns=['State', 'Airport ID', 'Species', 'Name', 'Latitude', 'Longitude'])

df_sun = filterDfByYear(min_year, max_year)
df_sun = df_sun[df_sun['State'].isin(states)].reset_index(drop=True)
df_sun = df_sun.drop(columns=['Year', 'Species', 'Latitude', 'Longitude'])

df_latlng = filterDfByYear(min_year, max_year).groupby(['Airport ID', 'Name', 'State', 'Latitude', 'Longitude']).sum().reset_index()
df_latlng = df_latlng.rename(columns={0: 'Incidents'})
df_latlng = df_latlng.drop(columns=['Species', 'Year'])
df_latlng = df_latlng.sort_values(by=['Incidents'], ascending=False)

df_worldwide = df_latlng[~df_latlng['State'].isin(states)].reset_index(drop=True)
df_statesonly = df_latlng[df_latlng['State'].isin(states)].reset_index(drop=True)

#%% Function to plot choropleth for incidents by state
def plotChoropleth(df):
    fig = px.choropleth(df, locations='State',
                        color='Incidents', 
                        locationmode='USA-states',
                        scope='usa',
                        hover_name='State',
                        color_continuous_scale='portland',
                        template='seaborn')
                        
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig

#%% Function to plot line graph of incidents by year
def plotLineGraph(df):
    fig = px.line(df, x='Year', y='Incidents', markers=True)
    return fig

#%% Function to plot sun burst plot of incidents by state with airport ID children
def plotSunBurst(df):
    fig = px.sunburst(df, path=['State', 'Airport ID'], values='Incidents', color='State')
    return fig

#%% Function to plot 3d scatter heat map for incidents by lat/lng
def plotScatterGeo(df):
    fig = px.scatter_geo(
            df,
            locationmode='USA-states',
            lat='Latitude',
            lon='Longitude',
            hover_data=['Airport ID', 'State', 'Latitude', 'Longitude', 'Incidents'],
            color='Incidents',
            size='Incidents',
            color_continuous_scale='portland',
            projection='orthographic',
            template='plotly_dark'
        )

    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    
    return fig

#%% Function to plot 2d scatter heat map for incidents by lat/lng
def plotScatterMapbox(df):
    fig = px.scatter_mapbox(df,
                            lat='Latitude',
                            lon='Longitude',
                            hover_data=['Airport ID', 'State', 'Latitude', 'Longitude', 'Incidents'],
                            size='Incidents',
                            color='Incidents',
                            color_continuous_scale='portland',
                            zoom=3,
                            template='seaborn'
                            )
            
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    
    return fig

#%% Function to plot 2d scatter heat map for incidents by runways zoomed in to airport
def plotScatterMapboxRunwayHeatmap(df, zoom_level):
    fig = px.scatter_mapbox(df,
                            lat='Latitude',
                            lon='Longitude',
                            hover_data=['Runway', 'Latitude', 'Longitude', 'Incidents'],
                            size='Incidents',
                            color='Incidents',
                            color_continuous_scale='portland',
                            zoom=zoom_level,
                            template='seaborn')
            
    fig.update_layout(mapbox_style='open-street-map', title='')
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    
    return fig

#%% Function to count runway incidents at given airport
def runways(df, rwy_list):
    # Get all non-duplicate runways
    rwys = df.Runway.drop_duplicates().values
    
    # Loop through and replace those with the full runway name
    for i in rwys:
        for j in rwy_list:
            if i.upper() in j:
                df['Runway'] = df['Runway'].replace(i, j)
                
    # Replace runways not found in list with blank
    for i in rwys:
        if i not in rwy_list:
            df['Runway'] = df['Runway'].replace(i, '')

    # Remove the blank cells to be left with only the runways
    df_new = df[df['Runway'] != ''].reset_index(drop=True)

    # Get counts of runway incidents
    counts = []
    for i in rwy_list:
        counts.append(len(df_new[df_new['Runway'] == i]))
    
    return counts

#%% Function to sort out null values from data frame column
def validDataFrame(df, null_col):
    return df.loc[~df[null_col].isnull()]

#%% Function to filter and clean ATL data frame and return counts of incidents
def getATL(start, stop):
    df = data[data.AIRPORT_ID == 'KATL'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for ATL runways
    lngs = [-84.428405, -84.417076, -84.438190, -84.427890, -84.433334] # longitudes for ATL runways
    lats = [33.649586, 33.646799, 33.634687, 33.631900, 33.620305] # latitudes for ATL runways
    
    # Runway list
    rwy_list = ['8R/26L', '8L/26R', '9R/27L', '9L/27R', '10/28']
    
    # Clean up ATL messy data
    df['Runway'] = df['Runway'].replace('20R', '')
    df['Runway'] = df['Runway'].replace('27', '')
    df['Runway'] = df['Runway'].replace('17R', '27R')
    df['Runway'] = df['Runway'].replace('16R', '26R')
    df['Runway'] = df['Runway'].replace('1R', '')
    df['Runway'] = df['Runway'].replace('9/27', '')
    df['Runway'] = df['Runway'].replace('8/26', '')
    df['Runway'] = df['Runway'].replace('3L', '')
    df['Runway'] = df['Runway'].replace('09R', '9R')
    df['Runway'] = df['Runway'].replace('9', '')
    df['Runway'] = df['Runway'].replace('4', '')
    df['Runway'] = df['Runway'].replace('08R', '8R')
    df['Runway'] = df['Runway'].replace('08L', '8L')
    df['Runway'] = df['Runway'].replace('09L', '9L')
    df['Runway'] = df['Runway'].replace('4R', '')
    df['Runway'] = df['Runway'].replace('17L', '27L')
    df['Runway'] = df['Runway'].replace('12', '')
    df['Runway'] = df['Runway'].replace('10R', '10')
    df['Runway'] = df['Runway'].replace('16', '')
    df['Runway'] = df['Runway'].replace('26', '')
    df['Runway'] = df['Runway'].replace('34L', '')
    
    # Get counts of ATL runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean DEN data frame and return counts of incidents
def getDEN(start, stop):
    df = data[data.AIRPORT_ID == 'KDEN'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for DEN
    lngs = [-104.641501, -104.660267, -104.640702, -104.704903, -104.687115, -104.696394] # longitudes for DEN runways
    lats = [39.849474, 39.847606, 39.877333, 39.840841, 39.880334, 39.875343] # latitudes for DEN runways
    
    # Runways of DEN
    rwy_list = ['17L/35R', '17R/35L', '8/26', '7/25', '16L/34R', '16R/34L']
    
    # Clean up messy DEN runway data
    df['Runway'] = df['Runway'].replace('16', '26')
    df['Runway'] = df['Runway'].replace('15', '25')
    df['Runway'] = df['Runway'].replace('17', '')
    df['Runway'] = df['Runway'].replace('6', '26')
    df['Runway'] = df['Runway'].replace('16/34', '')
    df['Runway'] = df['Runway'].replace('17/35', '')
    df['Runway'] = df['Runway'].replace('17LN', '17L')
    df['Runway'] = df['Runway'].replace('26R', '26')
    df['Runway'] = df['Runway'].replace('4R', '')
    df['Runway'] = df['Runway'].replace('16/34R', '16L/34R')
    df['Runway'] = df['Runway'].replace('19L', '16L')
    df['Runway'] = df['Runway'].replace('17/35R', '17L/35R')
    df['Runway'] = df['Runway'].replace('16R/35L', '')
    df['Runway'] = df['Runway'].replace('24R', '34R')
    df['Runway'] = df['Runway'].replace('31R', '34R')
    df['Runway'] = df['Runway'].replace('1R', '')
    df['Runway'] = df['Runway'].replace('4L', '')
    
    # Get counts of DEN runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean DFW data frame and return counts of incidents
def getDFW(start, stop):
    df = data[data.AIRPORT_ID == 'KDFW'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for DFW runways
    lngs = [-97.073306, -97.011186, -97.054714, -97.050878, -97.030005, -97.026284, -97.009839] # longitudes for DFW runways
    lats = [32.899955, 32.903487, 32.907908, 32.892420, 32.909359, 32.891874, 32.886939] # latitudes for DFW runways
    
    # Runway list
    rwy_list = ['13R/31L', '13L/31R', '18R/36L', '18L/36R', '17R/35L', '17C/35C', '17L/35R']
    
    # Clean up dfw messy data
    df['Runway'] = df['Runway'].replace('13', '')
    df['Runway'] = df['Runway'].replace('17', '')
    df['Runway'] = df['Runway'].replace('26R', '36R')
    df['Runway'] = df['Runway'].replace('17/35', '')
    df['Runway'] = df['Runway'].replace('18/36', '')
    df['Runway'] = df['Runway'].replace('R18R', '18R')
    df['Runway'] = df['Runway'].replace('18R/E1', '18R')
    df['Runway'] = df['Runway'].replace('18R/WL', '18R')
    df['Runway'] = df['Runway'].replace('18L/G8', '18L')
    df['Runway'] = df['Runway'].replace('17L/Q', '17L')
    df['Runway'] = df['Runway'].replace('17L/Q7', '17L')
    df['Runway'] = df['Runway'].replace('17/35C', '17C/35C')
    df['Runway'] = df['Runway'].replace('17R/35R', '')
    
    # Get counts of DFW runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean IAD data frame and return counts of incidents
def getIAD(start, stop):
    df = data[data.AIRPORT_ID == 'KIAD'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lng of center of IAD runways
    lngs = [-77.473481, -77.459517, -77.474709, -77.436129] # longitudes for IAD runways
    lats = [38.938858, 38.958783, 38.958783, 38.941521] # latitudes for IAD runways
    
    # List of IAD runway names
    rwy_list = ['01R/19L', '01C/19C', '01L/19R', '12/30']
    
    # Clean up messy IAD data
    df['Runway'] = df['Runway'].replace('1/19', '1C/19C')
    df['Runway'] = df['Runway'].replace('19', '1C/19C')
    df['Runway'] = df['Runway'].replace('19C/1C', '1C/19C')
    df['Runway'] = df['Runway'].replace('1', '1C/19C')
    df['Runway'] = df['Runway'].replace('01C', '1C/19C')
    df['Runway'] = df['Runway'].replace('01R', '1R/19L')
    df['Runway'] = df['Runway'].replace('01L', '1L/19R')
    df['Runway'] = df['Runway'].replace('RWY 1C', '1C/19C')
    df['Runway'] = df['Runway'].replace('IC', '1C/19C')
    df['Runway'] = df['Runway'].replace('2C', '1C/19C')

    counts = runways(df, rwy_list)

    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean JFK data frame and return counts of incidents
def getJFK(start, stop):
    df = data[data.AIRPORT_ID == 'KJFK'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lats/Lngs for JFK runways
    lngs = [-73.772892, -73.762345, -73.775377, -73.794576] # longitudes for JFK runways
    lats = [40.638497, 40.635769, 40.651061, 40.638165] # latitudes for JFK runways
    
    # JFK Runway List
    rwy_list = ['04L/22R', '04R/22L', '13L/31R', '13R/31L']
    
    # Clean up messy JFK data
    df['Runway'] = df['Runway'].replace('4/L22R', '4L/22R')
    df['Runway'] = df['Runway'].replace('13', '')
    df['Runway'] = df['Runway'].replace('31', '')
    df['Runway'] = df['Runway'].replace('13/31', '')
    df['Runway'] = df['Runway'].replace('4 R', '4R/22L')
    df['Runway'] = df['Runway'].replace('22', '')
    df['Runway'] = df['Runway'].replace('4L/31L', '4R/31L')
    df['Runway'] = df['Runway'].replace('2R', '4R/31L')
    df['Runway'] = df['Runway'].replace('31L/KE', '4R/31L')
    
    # Get counts of JFK runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean LAX data frame and return counts of incidents
def getLAX(start, stop):
    df = data[data.AIRPORT_ID == 'KLAX'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for LAX runways
    lngs = [-118.422211, -118.410753, -118.412909, -118.391302] # longitudes for LAX runways
    lats = [33.950030, 33.949212, 33.936473, 33.936543] # latitudes for LAX runways
    
    # Runway list
    rwy_list = ['6R/24L', '6L/24R', '7R/25L', '7L/25R']
    
    # Clean up LAX messy data
    df['Runway'] = df['Runway'].replace('24', '')
    df['Runway'] = df['Runway'].replace('25', '')
    df['Runway'] = df['Runway'].replace('7/25', '')
    df['Runway'] = df['Runway'].replace('8R/26L', '')
    df['Runway'] = df['Runway'].replace('6', '')
    df['Runway'] = df['Runway'].replace('06L', '6L')
    df['Runway'] = df['Runway'].replace('07R', '7R')
    df['Runway'] = df['Runway'].replace('06R', '6R')
    df['Runway'] = df['Runway'].replace('22L', '25L')
    
    # Get counts of LAX runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean MCO data frame and return counts of incidents
def getMCO(start, stop):
    df = data[data.AIRPORT_ID == 'KMCO'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for MCO runways
    lngs = [-81.282397, -81.295754, -81.322046, -81.326870] # longitudes for MCO runways
    lats = [28.429595, 28.428907, 28.420814, 28.442078] # latitudes for MCO runways
    
    # Runway list
    rwy_list = ['17L/35R', '17R/35L', '18L/36R', '18R/36L']
    
    # Clean up ORD messy data
    df['Runway'] = df['Runway'].replace('15R', '18R')
    df['Runway'] = df['Runway'].replace('17', '')
    df['Runway'] = df['Runway'].replace('17/35R', '17L/35R')
    df['Runway'] = df['Runway'].replace('18', '')
    df['Runway'] = df['Runway'].replace('35', '')
    df['Runway'] = df['Runway'].replace('36', '')
    
    # Get counts of ORD runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean ORD data frame and return counts of incidents
def getORD(start, stop):
    df = data[data.AIRPORT_ID == 'KORD'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for ORD runways
    lngs = [-87.900462, -87.883445, -87.912843, -87.923804, -87.902998, -87.921197, -87.901313, -87.913676] # longitudes for ORD runways
    lats = [41.994043, 41.966881, 42.002944, 41.988307, 41.984108, 41.969152, 41.965879, 41.957335] # latitudes for ORD runways
    
    # Runway list
    rwy_list = ['04L/22R', '04R/22L', '09L/27R', '09C/27C', '09R/27L', '10L/28R', '10C/28C', '10R/28L']
    
    # Clean up ORD messy data
    df['Runway'] = df['Runway'].replace('10C/27C', '10/28')
    df['Runway'] = df['Runway'].replace('10R-28L', '10R/28L')
    df['Runway'] = df['Runway'].replace('22', '')
    df['Runway'] = df['Runway'].replace('27', '')
    df['Runway'] = df['Runway'].replace('28 R', '10L/28R')
    df['Runway'] = df['Runway'].replace('35R', '32R')
    df['Runway'] = df['Runway'].replace('37R', '27R')
    df['Runway'] = df['Runway'].replace('4', '')
    df['Runway'] = df['Runway'].replace('4/22', '')
    df['Runway'] = df['Runway'].replace('4L/22R', '04L/22R')
    df['Runway'] = df['Runway'].replace('4R', '04R/22L')
    df['Runway'] = df['Runway'].replace('4r/22l', '04R/22L')
    df['Runway'] = df['Runway'].replace('9/27', '')
    df['Runway'] = df['Runway'].replace('9C', '09C/27C')
    df['Runway'] = df['Runway'].replace('9L-27R', '09L/27R')
    df['Runway'] = df['Runway'].replace('9L/27R', '09L/27R')
    df['Runway'] = df['Runway'].replace('9L/M', '09L/27R')
    df['Runway'] = df['Runway'].replace('9R-27L', '09R/27L')
    df['Runway'] = df['Runway'].replace('9R/27L', '09R/27L')
    df['Runway'] = df['Runway'].replace('9r', '09R')
    
    # Get counts of ORD runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean SLC data frame and return counts of incidents
def getSLC(start, stop):
    df = data[data.AIRPORT_ID == 'KSLC'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for SLC runways
    lngs = [-111.967351, -111.973787, -111.998582, -111.962186] # longitudes for SLC runways
    lats = [40.779786, 40.780540, 40.800766, 40.786723] # latitudes for SLC runways
    
    # Runway list
    rwy_list = ['14/32', '16L/34R', '16R/34L', '17/35']
    
    # Clean up SLC messy data
    df['Runway'] = df['Runway'].replace('16', '')
    df['Runway'] = df['Runway'].replace('16L/A11', '')
    df['Runway'] = df['Runway'].replace('16R-34L', '16R/34L')
    df['Runway'] = df['Runway'].replace('16R/A7', '')
    df['Runway'] = df['Runway'].replace('25', '17/35')
    df['Runway'] = df['Runway'].replace('34', '')
    df['Runway'] = df['Runway'].replace('35L', '')
    
    # Get counts of LAX runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean MEM data frame and return counts of incidents
def getMEM(start, stop):
    df = data[data.AIRPORT_ID == 'KMEM'].reset_index(drop=True)
    df = df[df['INCIDENT_YEAR'].between(start, stop)]
    df = df.rename(columns={'RUNWAY': 'Runway'})
    df = validDataFrame(df, 'Runway')
    
    # Lat/Lngs for MEM runways
    lngs = [-89.969795, -89.972819, -89.975680, -89.987180] # longitudes for MEM runways
    lats = [35.058172, 35.042257, 35.029938, 35.036909] # latitudes for MEM runways
    
    # Runway list
    rwy_list = ['09/27', '18L/36R', '18C/36C', '18R/36L']
    
    # Clean up MEM messy data
    df['Runway'] = df['Runway'].replace('17R', '18R')
    df['Runway'] = df['Runway'].replace('18 L', '18L')
    df['Runway'] = df['Runway'].replace('18C/ TWY P', '18C')
    df['Runway'] = df['Runway'].replace('18C/P', '18C')
    df['Runway'] = df['Runway'].replace('18L / TWY S3', '18L')
    df['Runway'] = df['Runway'].replace('18L-36R', '18L/36R')
    df['Runway'] = df['Runway'].replace('18L/36R at TWY P', '18L/36R')
    df['Runway'] = df['Runway'].replace('18L/S4', '18L/36R')
    df['Runway'] = df['Runway'].replace('18L/Twy P', '18L/36R')
    df['Runway'] = df['Runway'].replace('18R/35L', '18R/36L')
    df['Runway'] = df['Runway'].replace('18R/36', '18R/36L')
    df['Runway'] = df['Runway'].replace('18R/6L', '18R/36L')
    df['Runway'] = df['Runway'].replace('18R/M6', '18R/36L')
    df['Runway'] = df['Runway'].replace('18R/M7', '18R/36L')
    df['Runway'] = df['Runway'].replace('19R', '18R')
    df['Runway'] = df['Runway'].replace('26L', '36L')
    df['Runway'] = df['Runway'].replace('27/B', '09/27')
    df['Runway'] = df['Runway'].replace('35L', '36L')
    df['Runway'] = df['Runway'].replace('35R', '36R')
    df['Runway'] = df['Runway'].replace('36', '')
    df['Runway'] = df['Runway'].replace('36C/S5', '36C')
    df['Runway'] = df['Runway'].replace('36L/M4', '36L')
    df['Runway'] = df['Runway'].replace('36L/M6', '36L')
    df['Runway'] = df['Runway'].replace('36R/ S of TWY E', '36R')
    df['Runway'] = df['Runway'].replace('8', '')
    df['Runway'] = df['Runway'].replace('9-27', '09/27')
    df['Runway'] = df['Runway'].replace('9/27', '09/27')
    df['Runway'] = df['Runway'].replace('9/27 near TWY V3', '09/27')
    
    # Get counts of MEM runway incidents
    counts = runways(df, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Get data frames for each specific runway
df_atl = getATL(min_year, max_year)
df_den = getDEN(min_year, max_year)
df_dfw = getDFW(min_year, max_year)
df_iad = getIAD(min_year, max_year)
df_jfk = getJFK(min_year, max_year)
df_lax = getLAX(min_year, max_year)
df_mco = getMCO(min_year, max_year)
df_mem = getMEM(min_year, max_year)
df_ord = getORD(min_year, max_year)
df_slc = getSLC(min_year, max_year)

#%% Set up dashboard app
external_stylesheets = [dbc.themes.COSMO]
app = Dash(__name__, external_stylesheets=external_stylesheets)

#%% Define app layout for dashboard and parts
app.layout = dbc.Container([
    dbc.Row([
        html.Div(className='row', children=[
        html.Div(className='twelve columns', children=[
            html.Div(style={'float': 'left'}, children=[
                    html.H1('FAA National Wildlife Strike Database (NWSD)'),
                    html.H3('Visualizing NWSD incidents')
                ]
            ),
            
            html.Div(style={'float': 'right'}, children=[
                html.A( 
                    html.Img(
                            src='https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Seal_of_the_United_States_Federal_Aviation_Administration.svg/2048px-Seal_of_the_United_States_Federal_Aviation_Administration.svg.png',
                            style={'float': 'right', 'height': '100px', 'margin-top': '5px'}
                            ),
                    href='https://wildlife.faa.gov/home')
                    ]
                ),
            ]),
        ]),
    ]),
    
    dcc.Tabs([
        dcc.Tab(label='Tab 1', children=[
            dbc.Row(html.H5(id='plot-title')),
    
        dbc.Row([
            dbc.Col(children=[
                    html.P('Filter by FAA region'),
                    dcc.Dropdown(
                        id='region',
                        options=['Entire US', 
                                 'Alaskan',
                                 'Central',
                                 'Eastern',
                                 'Great Lakes',
                                 'New England',
                                 'Northwest Mountain',
                                 'Southern',
                                 'Southwest',
                                 'Western-Pacific'],
                        value='Entire US',
                        clearable=True,
                        )],
                className='justify-content-center',
                width=2
            ),
            
            dbc.Col(children=[
                html.P('Filter by year'),
                dcc.RangeSlider(value=[min_year, max_year],
                                step=1,
                                marks={i: str(i) for i in range(min_year, max_tick+1, 2)},
                                id='slider'
                                ),
                ],
                width=7
            ),
            
            dbc.Col(children=[
                html.P('Filter state plots'),
                dcc.RadioItems(id='top-ten',
                               options=['All Airports', 'Top 10'],
                               value='All Airports',
                               inline=True,
                               )
                ],
                width=3
            )
        ]),
        
        html.Br(),
        
        dbc.Row([
            dbc.Col(
                children=[html.P('Incidents by State'),
                          dash_table.DataTable(columns=[{'name': i, 'id': i} for i in df_main.columns],
                                               style_cell={'textAlign': 'center'},
                                               fixed_rows={'headers': True, 'data': 0},
                                               fixed_columns={'headers': True, 'data': 0},
                                               id='data-frame-main')
                        ],
                width=2
                ),
            
            dbc.Col(
                children=[dcc.Graph(id='us-map', figure=plotChoropleth(df_main)),
                          dbc.Modal([dbc.ModalHeader(dbc.ModalTitle('Incidents by Airport in Selected State')),
                                     dbc.ModalBody(children=[
                                         dbc.Col(dcc.Graph(id='state-bar'))]),
                                     dbc.ModalFooter(
                                         children=[dbc.Button('Close', 
                                                              id='close', 
                                                              className='ms-auto', 
                                                              n_clicks=0)
                                                   ])],
                                    id='modal',
                                    is_open=False,
                                    fullscreen=True)],
                width=9
                ),
            ]),
            
        html.Br(),
        
        dbc.Row([
            dbc.Col(
                children=[html.P('Incidents by Year'),
                          dash_table.DataTable(columns=[{'name': i, 'id': i} for i in df_line.columns],
                                               style_cell={'textAlign': 'center'},
                                               fixed_rows={'headers': True, 'data': 0},
                                               fixed_columns={'headers': True, 'data': 0},
                                               id='data-frame-line')
                        ],
                width=2
                ),
            
            dbc.Col(
                children=[dcc.Graph(id='line-graph', figure=plotLineGraph(df_line))],
                width=6
                ),
            
            dbc.Col(
                children=[dcc.Graph(id='sun-burst', figure=plotSunBurst(df_sun))],
                width=3
                )
            
            ]),
        
        html.Br(),
        
        dbc.Row([dcc.Markdown(children=[about_md])])]),
        
        dcc.Tab(label='Tab 2', children=[
            dbc.Row(html.H5(id='plot-title-2')),
    
            dbc.Row([
                dbc.Col(children=[
                        html.P('Filter by FAA region'),
                        dcc.Dropdown(
                            id='region-2',
                            options=['Entire US', 
                                     'Alaskan',
                                     'Central',
                                     'Eastern',
                                     'Great Lakes',
                                     'New England',
                                     'Northwest Mountain',
                                     'Southern',
                                     'Southwest',
                                     'Western-Pacific'],
                            value='Entire US',
                            clearable=True,
                            )],
                    className='justify-content-center',
                    width=2
                ),
                
                dbc.Col(children=[
                    html.P('Filter by year'),
                    dcc.RangeSlider(value=[min_year, max_year],
                                    step=1,
                                    marks={i: str(i) for i in range(min_year, max_tick+1, 2)},
                                    id='slider-2'
                                    ),
                    ],
                    width=6
                ),
                
                dbc.Col(children=[
                        html.P('2D vs. 3D Plot'),
                        dcc.RadioItems(id='dimension',
                                       options=['2D', '3D'],
                                       value='2D',
                                       inline=True,
                                       )],
                        width=2),
                
                dbc.Col(children=[
                        html.P('US vs. Worldwide'),
                        dcc.RadioItems(id='us-vs-world',
                                       options=['US Only', 'Worldwide'],
                                       value='US Only',
                                       inline=True,
                                       )],
                        width=2)
                
                ]),
            
            html.Br(),
            
            dbc.Row([
                dbc.Col(
                    children=[html.P('Incidents Across All Airports'),
                              dash_table.DataTable(columns=[{'name': i, 'id': i} for i in df_latlng[['Airport ID', 'Incidents']].columns],
                                                   style_cell={'textAlign': 'center'},
                                                   fixed_rows={'headers': True, 'data': 0},
                                                   fixed_columns={'headers': True, 'data': 0},
                                                   id='data-frame-by-airport')
                            ],
                    width=3
                    ),
                
                dbc.Col(
                    children=[dcc.Graph(id='scatter-plot', figure=plotScatterMapbox(df_statesonly)),
                              dbc.Modal([dbc.ModalHeader(dbc.ModalTitle('Incidents by Runway for Selected Airport')),
                                         dbc.ModalBody(children=[
                                             dbc.Row(children=[
                                                     dbc.Col(children=[dcc.Graph(id='runway-heatmap')], width=9),
                                                     dbc.Col(children=[html.P('Incidents by Runway'),
                                                                       dash_table.DataTable(columns=[{'name': i, 'id': i} for i in df_atl[['Runway', 'Incidents']].columns],
                                                                                            style_cell={'textAlign': 'center'},
                                                                                            fixed_rows={'headers': True, 'data': 0},
                                                                                            fixed_columns={'headers': True, 'data': 0},
                                                                                            id='data-frame-airport')], width=3)
                                                 ])]),
                                         dbc.ModalFooter(
                                             children=[dbc.Button('Close', 
                                                                  id='close-2', 
                                                                  className='ms-auto', 
                                                                  n_clicks=0)
                                                       ])],
                                        id='modal-2',
                                        is_open=False,
                                        fullscreen=True)],
                    width=9
                    ),
                ]),
            
            html.Br(),
            
            dbc.Row([dcc.Markdown(children=[about_md])])
            
            ])
        ])
    
], fluid=True)

#%% Callback values used for function to toggle modal screen
@app.callback(
    Output(component_id='modal', component_property='is_open'), 
    Output(component_id='state-bar', component_property='figure'),
    Input(component_id='us-map', component_property='clickData'),
    Input(component_id='close', component_property='n_clicks'),
    Input(component_id='slider', component_property='value'),
    Input(component_id='top-ten', component_property='value')
)

#%% Function to toggle modal plot showing specific state airport incident counts
def toggle_modal(mapclicked, is_open, slider_value, filter_value):
    if ctx.triggered_id == 'us-map':
        df = filterDfByYear(slider_value[0], slider_value[1])
        df = df[df['State'].isin(states)].reset_index(drop=True)
        
        if mapclicked['points'][0]['hovertext'] in states:
            state = mapclicked['points'][0]['hovertext']
            
            df = df[df['State'] == state].reset_index(drop=True)
            df = df.groupby(['Airport ID', 'Name']).sum().reset_index().drop(columns=['State', 'Year'])
            
            if state == 'HI' or state == 'AK':
                df['Airport ID'] = df['Airport ID'].apply(lambda x: x.lstrip('P'))
            else:
                df['Airport ID'] = df['Airport ID'].apply(lambda x: x.lstrip('K'))

            if slider_value[0] == slider_value[1]:
                title = 'Total Incidents at {} Airports in {}: {:,}'.format(state, slider_value[0], df['Incidents'].sum())
            else:
                title = 'Total Incidents at {} Airports between {} and {}: {:,}'.format(state, slider_value[0], slider_value[1], df['Incidents'].sum())
            
            df = df.sort_values(by=['Incidents'], ascending=False).reset_index(drop=True)
            if filter_value == 'Top 10':
                df = df.iloc[:10]
                
            # generating incidents by airport ID bar graph
            bar_fig = px.bar(df, x='Airport ID', y='Incidents', color='Incidents',
                             hover_data=['Name', 'Airport ID', 'Incidents'])
            
            bar_fig.update_layout(title=title, showlegend=False, template='seaborn')
            
            return (True, bar_fig)
        
        else:
            return (False, no_update)    
    
    else:
        return (False, no_update)
    
    if ctx.triggered_id == 'close':
        return (False, no_update)

    return is_open, no_update

#%% Callback values for update plots and tables function
@app.callback(
    Output(component_id='data-frame-main', component_property='data'),
    Output(component_id='data-frame-line', component_property='data'),
    Output(component_id='us-map', component_property='figure'),
    Output(component_id='line-graph', component_property='figure'),
    Output(component_id='sun-burst', component_property='figure'),
    Output(component_id='plot-title', component_property='children'),
    Input(component_id='sun-burst', component_property='clickData'),
    Input(component_id='region', component_property='value'),
    Input(component_id='slider', component_property='value'),
    Input(component_id='top-ten', component_property='value')
)

#%% Function to update main plots and tables on dashboard
def updatePlotsAndTables(sunclicked, region_value, slider_value, filter_value):
    df_choro = filterDfByYear(slider_value[0], slider_value[1])
    df_choro = df_choro[df_choro['State'].isin(states)].reset_index(drop=True)
    df_choro = df_choro.groupby('State').sum().reset_index()
    df_choro = df_choro.drop(columns=['Airport ID', 'Name', 'Year'])
    
    df_line = filterDfByYear(slider_value[0], slider_value[1])
    df_line = df_line[df_line['State'].isin(states)].reset_index(drop=True)
    df_line = df_line.groupby(['State', 'Year']).sum().reset_index()
    df_line = df_line.drop(columns=['Airport ID', 'Name'])
    
    df_sun = filterDfByYear(slider_value[0], slider_value[1])
    df_sun = df_sun[df_sun['State'].isin(states)].reset_index(drop=True)
    df_sun = df_sun.drop(columns=['Name', 'Species', 'Year', 'Latitude', 'Longitude'])
    
    if ctx.triggered_id == 'sun-burst' and sunclicked['points'][0]['id'] in states and sunclicked['points'][0]['id'] != None:
        state = sunclicked['points'][0]['id']
        df_choro = df_choro[df_choro['State'] == state].reset_index(drop=True)
        df_line = df_line[df_line['State'] == state].reset_index(drop=True)
        df_sun = df_sun[df_sun['State'] == state].reset_index(drop=True)
        
        if slider_value[0] == slider_value[1]:
            title = 'Total Incidents for {} in {}: {:,}'.format(state, slider_value[0], df_choro['Incidents'].sum())
        else:
            title = 'Total Incidents for {} between {} and {}: {:,}'.format(state, slider_value[0], slider_value[1], df_choro['Incidents'].sum())
            
    else:
        if region_value == 'Alaskan':
            df_choro = df_choro[df_choro['State'] == 'AK'].reset_index(drop=True)
            df_line = df_line[df_line['State'] == 'AK'].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'] == 'AK'].reset_index(drop=True)
        elif region_value == 'Central':
            df_choro = df_choro[df_choro['State'].isin(['IA', 'KS', 'MO', 'NE'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['IA', 'KS', 'MO', 'NE'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['IA', 'KS', 'MO', 'NE'])].reset_index(drop=True)
        elif region_value == 'Eastern':
            df_choro = df_choro[df_choro['State'].isin(['DC', 'DE', 'MD', 'NJ', 'NY', 'PA', 'VA', 'WV'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['DC', 'DE', 'MD', 'NJ', 'NY', 'PA', 'VA', 'WV'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['DC', 'DE', 'MD', 'NJ', 'NY', 'PA', 'VA', 'WV'])].reset_index(drop=True)
        elif region_value == 'Great Lakes':
            df_choro = df_choro[df_choro['State'].isin(['IL', 'IN', 'MI', 'MN', 'ND', 'OH', 'SD', 'WI'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['IL', 'IN', 'MI', 'MN', 'ND', 'OH', 'SD', 'WI'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['IL', 'IN', 'MI', 'MN', 'ND', 'OH', 'SD', 'WI'])].reset_index(drop=True)
        elif region_value == 'New England':
            df_choro = df_choro[df_choro['State'].isin(['CT', 'MA', 'ME', 'NH', 'RI', 'VT'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['CT', 'MA', 'ME', 'NH', 'RI', 'VT'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['CT', 'MA', 'ME', 'NH', 'RI', 'VT'])].reset_index(drop=True)
        elif region_value == 'Northwest Mountain':
            df_choro = df_choro[df_choro['State'].isin(['CO', 'ID', 'MT', 'OR', 'UT', 'WA', 'WY'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['CO', 'ID', 'MT', 'OR', 'UT', 'WA', 'WY'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['CO', 'ID', 'MT', 'OR', 'UT', 'WA', 'WY'])].reset_index(drop=True)
        elif region_value == 'Southern':
            df_choro = df_choro[df_choro['State'].isin(['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'PR', 'SC', 'TN'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'PR', 'SC', 'TN'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'PR', 'SC', 'TN'])].reset_index(drop=True)
        elif region_value == 'Southwest':
            df_choro = df_choro[df_choro['State'].isin(['AR', 'LA', 'NM', 'OK', 'TX'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['AR', 'LA', 'NM', 'OK', 'TX'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['AR', 'LA', 'NM', 'OK', 'TX'])].reset_index(drop=True)
        elif region_value == 'Western-Pacific':
            df_choro = df_choro[df_choro['State'].isin(['AZ', 'CA', 'HI', 'NV'])].reset_index(drop=True)
            df_line = df_line[df_line['State'].isin(['AZ', 'CA', 'HI', 'NV'])].reset_index(drop=True)
            df_sun = df_sun[df_sun['State'].isin(['AZ', 'CA', 'HI', 'NV'])].reset_index(drop=True)
            
        if slider_value[0] == slider_value[1]:
            title = 'Total Incidents for {} Region in {}: {:,}'.format(region_value, slider_value[0], df_choro['Incidents'].sum())
        else:
            title = 'Total Incidents for {} Region between {} and {}: {:,}'.format(region_value, slider_value[0], slider_value[1], df_choro['Incidents'].sum())
        
    df_line = df_line.groupby(['Year']).sum().reset_index().drop(columns=['State'])
    
    fig_choro = plotChoropleth(df_choro)
    fig_line = plotLineGraph(df_line)
    fig_sun = plotSunBurst(df_sun)
    
    fig_choro.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig_line.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig_sun.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    
    display_div = html.Div([title])
    
    return df_choro.to_dict('records'), df_line.to_dict('records'), fig_choro, fig_line, fig_sun, display_div

#%% Callback values for update plots and tables function
@app.callback(
    Output(component_id='scatter-plot', component_property='figure'),
    Output(component_id='data-frame-by-airport', component_property='data'),
    Output(component_id='plot-title-2', component_property='children'),
    Input(component_id='us-vs-world', component_property='value'),
    Input(component_id='dimension', component_property='value'),
    Input(component_id='region-2', component_property='value'),
    Input(component_id='slider-2', component_property='value'),
)

#%% Function to update main plots and tables on dashboard
def toggleBetween2dAnd3d(us_vs_world_value, dim_value, region_value, slider_value):
    df = filterDfByYear(slider_value[0], slider_value[1])
    df = df.groupby(['Airport ID', 'State', 'Latitude', 'Longitude']).sum().reset_index()
    df = df.rename(columns={0: 'Incidents'})
    df = df.drop(columns=['Species', 'Year'])

    df = df.sort_values(by=['Incidents'], ascending=False)

    if us_vs_world_value == 'US Only':
        df = df[df['State'].isin(states)].reset_index(drop=True)
        
        if region_value == 'Alaskan':
            df = df[df['State'] == 'AK'].reset_index(drop=True)
        elif region_value == 'Central':
            df = df[df['State'].isin(['IA', 'KS', 'MO', 'NE'])].reset_index(drop=True)
        elif region_value == 'Eastern':
            df = df[df['State'].isin(['DC', 'DE', 'MD', 'NJ', 'NY', 'PA', 'VA', 'WV'])].reset_index(drop=True)
        elif region_value == 'Great Lakes':
            df = df[df['State'].isin(['IL', 'IN', 'MI', 'MN', 'ND', 'OH', 'SD', 'WI'])].reset_index(drop=True)
        elif region_value == 'New England':
            df = df[df['State'].isin(['CT', 'MA', 'ME', 'NH', 'RI', 'VT'])].reset_index(drop=True)
        elif region_value == 'Northwest Mountain':
            df = df[df['State'].isin(['CO', 'ID', 'MT', 'OR', 'UT', 'WA', 'WY'])].reset_index(drop=True)
        elif region_value == 'Southern':
            df = df[df['State'].isin(['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'PR', 'SC', 'TN'])].reset_index(drop=True)
        elif region_value == 'Southwest':
            df = df[df['State'].isin(['AR', 'LA', 'NM', 'OK', 'TX'])].reset_index(drop=True)
        elif region_value == 'Western-Pacific':
            df = df[df['State'].isin(['AZ', 'CA', 'HI', 'NV'])].reset_index(drop=True)
        else:
            df = df

    else:
        df_worldwide = df[~df['State'].isin(states)].reset_index(drop=True)
        df = df_worldwide.sort_values(by=['Incidents'], ascending=False)
    
    if dim_value == '2D':
        fig_scatter = plotScatterMapbox(df)
    else:
        fig_scatter = plotScatterGeo(df)
        
    fig_scatter.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    
    if slider_value[0] == slider_value[1]:
        title = 'Total Incidents for {} Region in {}: {:,}'.format(region_value, slider_value[0], df['Incidents'].sum())
    else:
        title = 'Total Incidents for {} Region between {} and {}: {:,}'.format(region_value, slider_value[0], slider_value[1], df['Incidents'].sum())
    
    return fig_scatter, df.to_dict('records'), title

#%% Callback values for update plots and tables function
@app.callback(
    Output(component_id='modal-2', component_property='is_open'), 
    Output(component_id='runway-heatmap', component_property='figure'),
    Output(component_id='data-frame-airport', component_property='data'),
    Input(component_id='scatter-plot', component_property='clickData'),
    Input(component_id='close-2', component_property='n_clicks'),
    Input(component_id='slider-2', component_property='value'),
)

#%% Function to toggle runway heatmap on click
def toggleRunwayHeatmap(mapclicked, is_open, slider_value):
    if ctx.triggered_id == 'scatter-plot':
        airport_id = mapclicked['points'][0]['customdata'][0]
        
        if airport_id == 'KATL':
            df = getATL(slider_value[0], slider_value[1])
            plot_title = 'ATL - Atlanta Hartsfield-Jackson International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
            
        elif airport_id == 'KDEN':
            df = getDEN(slider_value[0], slider_value[1])
            plot_title='DEN - Denver International Airport Incidents by Runway'
            zoom_level = 11
            plot_flag = True
            
        elif airport_id == 'KDFW':
            df = getDFW(slider_value[0], slider_value[1])
            plot_title='DFW - Dallas/Fort Worth International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
            
        elif airport_id == 'KIAD':
            df = getIAD(slider_value[0], slider_value[1])
            plot_title='IAD - Washington Dulles International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
            
        elif airport_id == 'KJFK':
            df = getJFK(slider_value[0], slider_value[1])
            plot_title='JFK - New York John F Kennedy International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
            
        elif airport_id == 'KLAX':
            df = getLAX(slider_value[0], slider_value[1])
            plot_title='LAX - Los Angeles International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
        
        elif airport_id == 'KMCO':
            df = getMCO(slider_value[0], slider_value[1])
            plot_title='MCO - Orlando International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
        
        elif airport_id == 'KMEM':
            df = getMEM(slider_value[0], slider_value[1])
            plot_title='MEM - Memphis International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
            
        elif airport_id == 'KORD':
            df = getORD(slider_value[0], slider_value[1])
            plot_title='ORD - Chicago O\'Hare International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
        
        elif airport_id == 'KSLC':
            df = getSLC(slider_value[0], slider_value[1])
            plot_title = 'SLC - Salt Lake City International Airport Incidents by Runway'
            zoom_level = 12
            plot_flag = True
        
        else:
            plot_flag = False
            
        if plot_flag:
            fig = plotScatterMapboxRunwayHeatmap(df, zoom_level)
            fig.update_layout(mapbox_style='open-street-map', title=plot_title)
            fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
            return (True, fig, df.to_dict('records'))
        
        else:
            return (False, no_update, no_update)
        
    if ctx.triggered_id == 'close-2':
        return (False, no_update, no_update)
    
    return is_open, no_update, no_update

#%% Execute main and run app on custom 127.0.0.1:1234 environment
if __name__ == '__main__':
    app.run_server(debug=True, port=os.getenv('HOST', '1234'))
    os.system('start http://127.0.0.1:1234')