# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 15:47:04 2023

@author: mitch
"""

#%%
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

#%%
states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 
          'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 
          'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 
          'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

#%% Load data from pickle
data = pd.read_pickle(os.path.join(os.getcwd(), '..\Data\strike_reports.pkl'))

#%% Break data into lat/long worldwide vs. states only
df_latlng = pd.DataFrame(data.groupby(['AIRPORT_ID', 'STATE', 'LATITUDE', 'LONGITUDE']).size()).reset_index()
df_latlng = df_latlng.rename(columns={0: 'Incidents', 'AIRPORT_ID': 'Airport ID', 
                                      'STATE': 'State', 'LATITUDE': 'Latitude',
                                      'LONGITUDE': 'Longitude'})
df_worldwide = df_latlng.copy()
df_statesonly = df_latlng[df_latlng['State'].isin(states)].reset_index(drop=True)

#%% Function to sort out null values from data frame column
def validDataFrame(df, null_col):
    return df.loc[~df[null_col].isnull()]

#%% Function to count runway incidents at given airport
def runways(df, rwy_list):
    # Get all non-duplicate runways
    rwys = df.RUNWAY.drop_duplicates().values
    
    # Loop through and replace those with the full runway name
    for i in rwys:
        for j in rwy_list:
            if i.upper() in j:
                df['RUNWAY'] = df['RUNWAY'].replace(i, j)
                
    # Replace runways not found in list with blank
    for i in rwys:
        if i not in rwy_list:
            df['RUNWAY'] = df['RUNWAY'].replace(i, '')

    # Remove the blank cells to be left with only the runways
    df_new = df[df['RUNWAY'] != ''].reset_index(drop=True)

    # Get counts of runway incidents
    counts = []
    for i in rwy_list:
        counts.append(len(df_new[df_new['RUNWAY'] == i]))
    
    return counts

#%% Function to filter and clean ATL data frame and return counts of incidents
def getATL(df):
    df_atl = df[df.AIRPORT_ID == 'KATL'].reset_index(drop=True)
    df_atl = validDataFrame(df_atl, 'RUNWAY')
    
    # Lat/Lngs for ATL runways
    lngs = [-84.428405, -84.417076, -84.438190, -84.427890, -84.433334] # longitudes for ATL runways
    lats = [33.649586, 33.646799, 33.634687, 33.631900, 33.620305] # latitudes for ATL runways
    
    # Runway list
    rwy_list = ['8R/26L', '8L/26R', '9R/27L', '9L/27R', '10/28']
    
    # Clean up ATL messy data
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('20R', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('27', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('17R', '27R')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('16R', '26R')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('1R', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('9/27', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('8/26', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('3L', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('09R', '9R')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('9', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('4', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('08R', '8R')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('08L', '8L')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('09L', '9L')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('4R', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('17L', '27L')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('12', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('10R', '10')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('16', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('26', '')
    df_atl['RUNWAY'] = df_atl['RUNWAY'].replace('34L', '')
    
    # Get counts of DFW runway incidents
    counts = runways(df_atl, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean DEN data frame and return counts of incidents
def getDEN(df):
    df_den = df[df.AIRPORT_ID == 'KDEN'].reset_index(drop=True)
    df_den = validDataFrame(df_den, 'RUNWAY')
    
    # Lat/Lngs for DEN
    lngs = [-104.641501, -104.660267, -104.640702, -104.704903, -104.687115, -104.696394] # longitudes for DEN runways
    lats = [39.849474, 39.847606, 39.877333, 39.840841, 39.880334, 39.875343] # latitudes for DEN runways
    
    # Runways of DEN
    rwy_list = ['17L/35R', '17R/35L', '8/26', '7/25', '16L/34R', '16R/34L']
    
    # Clean up messy DEN runway data
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('16', '26')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('15', '25')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('17', '')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('6', '26')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('16/34', '')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('17/35', '')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('17LN', '17L')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('26R', '26')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('4R', '')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('16/34R', '16L/34R')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('19L', '16L')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('17/35R', '17L/35R')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('16R/35L', '')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('24R', '34R')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('31R', '34R')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('1R', '')
    df_den['RUNWAY'] = df_den['RUNWAY'].replace('4L', '')
    
    # Get counts of DEN runway incidents
    counts = runways(df_den, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean dfwdata frame and return counts of incidents
def getDFW(df):
    df_dfw = df[df.AIRPORT_ID == 'KDFW'].reset_index(drop=True)
    df_dfw = validDataFrame(df_dfw, 'RUNWAY')
    
    # Lat/Lngs for DFW runways
    lngs = [-97.073306, -97.011186, -97.054714, -97.050878, -97.030005, -97.026284, -97.009839] # longitudes for DFW runways
    lats = [32.899955, 32.903487, 32.907908, 32.892420, 32.909359, 32.891874, 32.886939] # latitudes for DFW runways
    
    # Runway list
    rwy_list = ['13R/31L', '13L/31R', '18R/36L', '18L/36R', '17R/35L', '17C/35C', '17L/35R']
    
    # Clean up dfw messy data
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('13', '')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('17', '')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('26R', '36R')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('17/35', '')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('18/36', '')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('R18R', '18R')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('18R/E1', '18R')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('18R/WL', '18R')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('18L/G8', '18L')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('17L/Q', '17L')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('17L/Q7', '17L')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('17/35C', '17C/35C')
    df_dfw['RUNWAY'] = df_dfw['RUNWAY'].replace('17R/35R', '')
    
    # Get counts of DFW runway incidents
    counts = runways(df_dfw, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'RUNWAY': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean IAD data frame and return counts of incidents
def getIAD(df):
    df_iad = df[df.AIRPORT_ID == 'KIAD'].reset_index(drop=True)
    df_iad = validDataFrame(df_iad, 'RUNWAY')
    
    # Lat/Lng of center of IAD runways
    lngs = [-77.473481, -77.459517, -77.474709, -77.436129] # longitudes for IAD runways
    lats = [38.938858, 38.958783, 38.958783, 38.941521] # latitudes for IAD runways
    
    # List of IAD runway names
    rwy_list = ['01R/19L', '01C/19C', '01L/19R', '12/30']
    
    # Clean up messy IAD data
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('1/19', '1C/19C')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('19', '1C/19C')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('19C/1C', '1C/19C')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('1', '1C/19C')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('01C', '1C/19C')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('01R', '1R/19L')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('01L', '1L/19R')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('RWY 1C', '1C/19C')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('IC', '1C/19C')
    df_iad['RUNWAY'] = df_iad['RUNWAY'].replace('2C', '1C/19C')

    counts = runways(df_iad, rwy_list)

    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean JFK data frame and return counts of incidents
def getJFK(df):
    df_jfk = df[df.AIRPORT_ID == 'KJFK'].reset_index(drop=True)
    df_jfk = validDataFrame(df_jfk, 'RUNWAY')
    
    # Lats/Lngs for JFK runways
    lngs = [-73.772892, -73.762345, -73.775377, -73.794576] # longitudes for JFK runways
    lats = [40.638497, 40.635769, 40.651061, 40.638165] # latitudes for JFK runways
    
    # JFK Runway List
    rwy_list = ['04L/22R', '04R/22L', '13L/31R', '13R/31L']
    
    # Clean up messy JFK data
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('4/L22R', '4L/22R')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('13', '')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('31', '')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('13/31', '')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('4 R', '4R/22L')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('22', '')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('4L/31L', '4R/31L')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('2R', '4R/31L')
    df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('31L/KE', '4R/31L')
    
    # Get counts of JFK runway incidents
    counts = runways(df_jfk, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean LAX data frame and return counts of incidents
def getLAX(df):
    df_lax = df[df.AIRPORT_ID == 'KLAX'].reset_index(drop=True)
    df_lax = validDataFrame(df_lax, 'RUNWAY')
    
    # Lat/Lngs for LAX runways
    lngs = [-118.422211, -118.410753, -118.412909, -118.391302] # longitudes for LAX runways
    lats = [33.950030, 33.949212, 33.936473, 33.936543] # latitudes for LAX runways
    
    # Runway list
    rwy_list = ['6R/24L', '6L/24R', '7R/25L', '7L/25R']
    
    # Clean up LAX messy data
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('24', '')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('25', '')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('7/25', '')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('8R/26L', '')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('6', '')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('06L', '6L')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('07R', '7R')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('06R', '6R')
    df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('22L', '25L')
    
    # Get counts of LAX runway incidents
    counts = runways(df_lax, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean MCO data frame and return counts of incidents
def getMCO(df):
    df_mco = df[df.AIRPORT_ID == 'KMCO'].reset_index(drop=True)
    df_mco = validDataFrame(df_mco, 'RUNWAY')
    
    # Lat/Lngs for MCO runways
    lngs = [-81.282397, -81.295754, -81.322046, -81.326870] # longitudes for MCO runways
    lats = [28.429595, 28.428907, 28.420814, 28.442078] # latitudes for MCO runways
    
    # Runway list
    rwy_list = ['17L/35R', '17R/35L', '18L/36R', '18R/36L']
    
    # Clean up ORD messy data
    df_mco['RUNWAY'] = df_mco['RUNWAY'].replace('15R', '18R')
    df_mco['RUNWAY'] = df_mco['RUNWAY'].replace('17', '')
    df_mco['RUNWAY'] = df_mco['RUNWAY'].replace('17/35R', '17L/35R')
    df_mco['RUNWAY'] = df_mco['RUNWAY'].replace('18', '')
    df_mco['RUNWAY'] = df_mco['RUNWAY'].replace('35', '')
    df_mco['RUNWAY'] = df_mco['RUNWAY'].replace('36', '')
    
    # Get counts of ORD runway incidents
    counts = runways(df_mco, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Function to filter and clean ORD data frame and return counts of incidents
def getORD(df):
    df_ord = df[df.AIRPORT_ID == 'KORD'].reset_index(drop=True)
    df_ord = validDataFrame(df_ord, 'RUNWAY')
    
    # Lat/Lngs for ORD runways
    lngs = [-87.900462, -87.883445, -87.912843, -87.923804, -87.902998, -87.921197, -87.901313, -87.913676] # longitudes for ORD runways
    lats = [41.994043, 41.966881, 42.002944, 41.988307, 41.984108, 41.969152, 41.965879, 41.957335] # latitudes for ORD runways
    
    # Runway list
    rwy_list = ['04L/22R', '04R/22L', '09L/27R', '09C/27C', '09R/27L', '10L/28R', '10C/28C', '10R/28L']
    
    # Clean up ORD messy data
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('10C/27C', '10/28')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('10R-28L', '10R/28L')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('14', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('14/32', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('15', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('15/33', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('17L', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('22', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('27', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('27C', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('28 R', '10L/28R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('31', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('32', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('33', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('35R', '32R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('36R', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('37R', '27R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('4', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('4/22', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('4L', '04L')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('4L/22R', '04L/22R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('4R', '04R/22L')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('4r/22l', '04R/22L')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9/27', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9C', '')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9L', '09L')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9L-27R', '09L/27R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9L/27R', '09L/27R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9L/M', '09L/27R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9R', '09R')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9R-27L', '09R/27L')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9R/27L', '09R/27L')
    df_ord['RUNWAY'] = df_ord['RUNWAY'].replace('9r', '09R')
    
    # Get counts of ORD runway incidents
    counts = runways(df_ord, rwy_list)
    
    # Create data frame of runways with lats, lngs, and counts
    df_count = pd.DataFrame({'Runway': rwy_list, 'Latitude': lats, 'Longitude': lngs, 'Incidents': counts})
    return df_count

#%% Get data frames for each specific runway
df_atl = getATL(data)
df_den = getDEN(data)
df_dfw = getDFW(data)
df_iad = getIAD(data)
df_jfk = getJFK(data)
df_lax = getLAX(data)
df_ord = getORD(data)
df_mco = getMCO(data)

#%% Create dash app
app = Dash(__name__)

#%% Generate layout in html with main graph and dropdown for airports
app.layout = html.Div(
    [
        html.H4('FAA National Wildlife Strike Database (NWSD) Incidents'),
        html.P(
            'Plotting NWSD incidents across the U.S. and airport specific runways.'
        ),
        dcc.Graph(id='graph'),
        html.P(
            'Choose an airport to generate a runway specific heatmap for: '
        ),
        dcc.Dropdown(
            id='type',
            options=['All Airports', 
                     'ATL - Atlanta Hartsfield-Jackson International Airport', 
                     'DEN - Denver International Airport', 
                     'DFW - Dallas/Fort Worth International Airport', 
                     'IAD - Washington Dulles International Airport', 
                     'JFK - New York John F Kennedy International Airport', 
                     'LAX - Los Angeles International Airport',
                     'MCO - Orlando International Airport',
                     'ORD - Chicago O\'Hare International Airport'],
            value='All Airports',
            clearable=True,
        ),
    ]
)

#%% Callback variables for app
@app.callback(
    Output('graph', 'figure'),
    Input('type', 'value'),
)

#%% Generate map plot on app based on dropdown selection
def generate_chart(values):
    if values == 'ATL - Atlanta Hartsfield-Jackson International Airport':
        fig = px.scatter_mapbox(df_atl,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=12,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='ATL - Atlanta Hartsfield-Jackson International Airport Incidents by Runway')
    
    elif values == 'DEN - Denver International Airport':
        fig = px.scatter_mapbox(df_den,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=11,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='DEN - Denver International Airport Incidents by Runway')
        
    elif values == 'DFW - Dallas/Fort Worth International Airport':
        fig = px.scatter_mapbox(df_dfw,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=12,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='DFW - Dallas/Fort Worth International Airport Incidents by Runway')
        
    elif values == 'IAD - Washington Dulles International Airport':
        fig = px.scatter_mapbox(df_iad,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=11.5,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='IAD - Washington Dulles International Airport Incidents by Runway')
        
    elif values == 'JFK - New York John F Kennedy International Airport':
        fig = px.scatter_mapbox(df_jfk,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=12,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='JFK - New York John F Kennedy International Airport Incidents by Runway')
        
    elif values == 'LAX - Los Angeles International Airport':
        fig = px.scatter_mapbox(df_lax,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=12,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='LAX - Los Angeles International Airport Incidents by Runway')
    
    elif values == 'MCO - Orlando International Airport':
        fig = px.scatter_mapbox(df_mco,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=12,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='MCO - Orlando International Airport Incidents by Runway')
    
    elif values == 'ORD - Chicago O\'Hare International Airport':
        fig = px.scatter_mapbox(df_ord,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Runway', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=11,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='ORD - Chicago O\'Hare International Airport Incidents by Runway')
    
    else:
        fig = px.scatter_mapbox(df_statesonly,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Airport ID', 'State', 'Latitude', 'Longitude', 'Incidents'],
                                size='Incidents',
                                color='Incidents',
                                color_continuous_scale='portland',
                                zoom=3,
                                template='seaborn')
        
        fig.update_layout(mapbox_style='open-street-map', title='All US Airstrike Incidents')
        
    return fig

#%% Generate app and run server locally
if __name__ == '__main__':
    app.run_server(debug=False, port=os.getenv('PORT', '1234'), )
    os.system('start http://127.0.0.1:1234')