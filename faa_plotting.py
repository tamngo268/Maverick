# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 20:03:38 2023

@author: mitch
"""

#%% Import libraries
import pandas as pd
import plotly.graph_objects as go
import os
import folium
from folium.plugins import HeatMap, HeatMapWithTime

#%% Set up renderer to browser for plotly plots
import plotly.io as pio
pio.renderers.default = "browser"

#%% Insert stadia maps api token here (need to debug)
#stadia_api_token = 'Token <insert token here>'

#%% Folium API Function
# def foliumAPISetUp(API_TOKEN):
#     import requests
        
#     # Create a session and attach the authorization header.
#     api_session = requests.Session()
#     api_session.headers['Authorization'] = API_TOKEN
    
#     # Create a property with the desired name.
#     property_resp = api_session.post(
#         'https://client.stadiamaps.com/api/v1/properties/',
#         json={'name': 'My API Property'}
#     )
    
#     # Ensure the request succeeded.
#     assert property_resp.status_code == 201
    
#     # Create a domain attached to that property. But please use another domain name!
#     # example.com is only for demonstration purposes. :)
#     domain_resp = api_session.post(
#         'https://client.stadiamaps.com/api/v1/domains/',
#         json={'property_id': property_resp.json()['id'],
#               'base_domain': 'example.com',
#               'wildcard': True,
#               }
#     )
    
#     # Ensure the request succeeded.
#     assert domain_resp.status_code == 201

# #%%
# foliumAPISetUp(stadia_api_token)

#%% Plot incidents by state heatmap
def plotStateHeatmap(df, var):
    # plotting the heatmap by states
    fig = go.Figure(data=go.Choropleth(
        locations=df['State'], # Spatial coordinates
        z = df['count'].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = var,
        text = df['State']
        ))
    fig.update_layout(
        title_text = var + ' by state<br>(Hover over the states for details)',
        geo_scope='usa', # limit map scope to USA
    )

    fig.show()

#%% All the US States (plus DC)
states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 
          'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 
          'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 
          'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 
          'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

#%% Get full data frame from 
data_df = pd.read_pickle(os.path.join(os.getcwd(), 'strike_reports.pkl'))

#%% Find incident count for each state
counts = []
for i in states:
    counts.append(len(data_df[data_df.STATE == i]))

#%% Create new dataframe with just states and counts
df = pd.DataFrame(data={'State': states, 'count': counts})

#%%
plotStateHeatmap(df, 'Incidents')

#%% Get two data frames one with just lat/lng, the other with lat/lng and date
blah = data_df[['LATITUDE', 'LONGITUDE']]
blah2 = data_df[['INCIDENT_DATE', 'LATITUDE', 'LONGITUDE']]

#%% Group each data frame by columns
res = blah.groupby(['LATITUDE', 'LONGITUDE']).size().sort_values(ascending=False)
new_df = pd.DataFrame({'Count': res}).reset_index()
res2 = blah2.groupby(['INCIDENT_DATE', 'LATITUDE', 'LONGITUDE']).size().sort_values(ascending=False)
new_df2 = pd.DataFrame({'Count': res2}).reset_index()

#%% Create heat map for all data centered on continental US
hm = folium.Map(location=[37.0902, -95.7129], # Center of USA
               tiles='stamentoner',
               zoom_start=3.4)

HeatMap(new_df, min_opacity=0.4, blur=16).add_to(folium.FeatureGroup(name='Heat Map').add_to(hm))
folium.LayerControl().add_to(hm)
hm.save('heatmap_all_data.html')
os.system('start heatmap_all_data.html')

#%% Create heat map with time for all data centered on continental US
hm2 = folium.Map(location=[37.0902, -95.7129], # Center of USA
                 tiles='stamentoner',
                 zoom_start=3.4)

HeatMapWithTime(new_df2, min_opacity=0.4, blur=16).add_to(folium.FeatureGroup(name='Heat Map With Time').add_to(hm2))
folium.LayerControl().add_to(hm2)
hm2.save('heatmap_all_data_vs_time.html')
os.system('start heatmap_all_data_vs_time.html')

#%% Check to make sure a data frame is valid (i.e. not full of null values)
def validDataFrame(df, null_col):
    return df.loc[~df[null_col].isnull()]

#%% IAD Section
df_iad = data_df[data_df.AIRPORT_ID == 'KIAD'].reset_index(drop=True)
df_iad = validDataFrame(df_iad, 'RUNWAY')

#%% Lat/Lng of center of IAD runways
lngs = [-77.473481, -77.459517, -77.474709, -77.436129] # longitudes for IAD runways
lats = [38.938858, 38.958783, 38.958783, 38.941521] # latitudes for IAD runways

#%% List of IAD runway names
rwy_list = ['01R/19L', '01C/19C', '01L/19R', '12/30']

#%% Clean up messy IAD data
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

#%% Function to count of runway incidents at given airport
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

#%% Get counts of IAD runway incidents
counts = runways(df_iad, rwy_list)

#%% Create data frame of runways with lats, lngs, and counts
df_count = pd.DataFrame({'RUNWAY': rwy_list, 'LATITUDE': lats, 'LONGITUDE': lngs, 'COUNT': counts})

#%% Create heatmap centered on IAD with incidents by runway
hm = folium.Map(location=[38.947993, -77.448169], #Center of IAD
               tiles='stamentoner',
               zoom_start=14)

HeatMap(df_count[['LATITUDE', 'LONGITUDE', 'COUNT']], min_opacity=0.75, blur=12).add_to(folium.FeatureGroup(name='Heat Map').add_to(hm))
for i in range(len(df_count)):
    folium.Marker(location=[df_count['LATITUDE'].iloc[i], df_count['LONGITUDE'].iloc[i]], tooltip='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i]), popup='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i])).add_to(hm)

folium.TileLayer('openstreetmap').add_to(hm)
hm.save('heatmap_iad_runways_openstreet.html')
os.system('start heatmap_iad_runways_openstreet.html')

# folium.TileLayer('cartodbdark_matter').add_to(hm)
# hm.save('heatmap_iad_runways_dark.html')
# os.system('start heatmap_iad_runways_dark.html')

#%% JFK Section
df_jfk = data_df[data_df.AIRPORT_ID == 'KJFK'].reset_index(drop=True)
df_jfk = validDataFrame(df_jfk, 'RUNWAY')

#%% Lats/Lngs for JFK runways
lngs = [-73.772892, -73.762345, -73.775377, -73.794576] # longitudes for JFK runways
lats = [40.638497, 40.635769, 40.651061, 40.638165] # latitudes for JFK runways

#%% JFK Runway List
rwy_list = ['04L/22R', '04R/22L', '13L/31R', '13R/31L']

#%% Clean up messy JFK data
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('4/L22R', '4L/22R')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('13', '')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('31', '')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('13/31', '')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('4 R', '4R/22L')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('22', '')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('4L/31L', '4R/31L')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('2R', '4R/31L')
df_jfk['RUNWAY'] = df_jfk['RUNWAY'].replace('31L/KE', '4R/31L')

#%% Get counts of JFK runway incidents
counts = runways(df_jfk, rwy_list)

#%% Create data frame of runways with lats, lngs, and counts
df_count = pd.DataFrame({'RUNWAY': rwy_list, 'LATITUDE': lats, 'LONGITUDE': lngs, 'COUNT': counts})

#%% Create heatmap centered on JFK with incidents by runway
hm = folium.Map(location=[40.641567, -73.777390], #Center of JFK
               tiles='stamentoner',
               zoom_start=14)

HeatMap(df_count[['LATITUDE', 'LONGITUDE', 'COUNT']], min_opacity=0.75, blur=12).add_to(folium.FeatureGroup(name='Heat Map').add_to(hm))
for i in range(len(df_count)):
    folium.Marker(location=[df_count['LATITUDE'].iloc[i], df_count['LONGITUDE'].iloc[i]], tooltip='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i]), popup='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i])).add_to(hm)

folium.TileLayer('openstreetmap').add_to(hm)
hm.save('heatmap_jfk_runways_openstreet.html')
os.system('start heatmap_jfk_runways_openstreet.html')

#%% DEN Section
df_den = data_df[data_df.AIRPORT_ID == 'KDEN'].reset_index(drop=True)
df_den = validDataFrame(df_den, 'RUNWAY')

#%% Lat/Lngs for DEN
lngs = [-104.641501, -104.660267, -104.640702, -104.704903, -104.687115, -104.696394] # longitudes for DEN runways
lats = [39.849474, 39.847606, 39.877333, 39.840841, 39.880334, 39.875343] # latitudes for DEN runways

#%% Runways of DEN
rwy_list = ['17L/35R', '17R/35L', '8/26', '7/25', '16L/34R', '16R/34L']

#%% Clean up messy DEN runway data
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

#%% Get counts of DEN runway incidents
counts = runways(df_den, rwy_list)

#%% Create data frame of runways with lats, lngs, and counts
df_count = pd.DataFrame({'RUNWAY': rwy_list, 'LATITUDE': lats, 'LONGITUDE': lngs, 'COUNT': counts})

#%% Create heatmap centered on DEN for runway incidents
hm = folium.Map(location=[39.857114, -104.669962], #Center of DEN
               tiles='stamentoner',
               zoom_start=13)

HeatMap(df_count[['LATITUDE', 'LONGITUDE', 'COUNT']], min_opacity=0.75, blur=12).add_to(folium.FeatureGroup(name='Heat Map').add_to(hm))
for i in range(len(df_count)):
    folium.Marker(location=[df_count['LATITUDE'].iloc[i], df_count['LONGITUDE'].iloc[i]], tooltip='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i]), popup='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i])).add_to(hm)

folium.TileLayer('openstreetmap').add_to(hm)
hm.save('heatmap_den_runways_openstreet.html')
os.system('start heatmap_den_runways_openstreet.html')

#%% DFW Section
df_dfw = data_df[data_df.AIRPORT_ID == 'KDFW'].reset_index(drop=True)
df_dfw = validDataFrame(df_dfw, 'RUNWAY')

#%% Lat/Lngs for DFW runways
lngs = [-97.073306, -97.011186, -97.054714, -97.050878, -97.030005, -97.026284, -97.009839] # longitudes for DFW runways
lats = [32.899955, 32.903487, 32.907908, 32.892420, 32.909359, 32.891874, 32.886939] # latitudes for DFW runways

#%% Runway list
rwy_list = ['13R/31L', '13L/31R', '18R/36L', '18L/36R', '17R/35L', '17C/35C', '17L/35R']

#%% Clean up dfw messy data
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

#%% Get counts of DFW runway incidents
counts = runways(df_dfw, rwy_list)

#%% Create data frame of runways with lats, lngs, and counts
df_count = pd.DataFrame({'RUNWAY': rwy_list, 'LATITUDE': lats, 'LONGITUDE': lngs, 'COUNT': counts})

#%% Create heatmap centered on DFW with runway incidents
hm = folium.Map(location=[32.895937, -97.037202], #Center of DFW
               tiles='stamentoner',
               zoom_start=13)

HeatMap(df_count[['LATITUDE', 'LONGITUDE', 'COUNT']], min_opacity=0.75, blur=12).add_to(folium.FeatureGroup(name='Heat Map').add_to(hm))
for i in range(len(df_count)):
    folium.Marker(location=[df_count['LATITUDE'].iloc[i], df_count['LONGITUDE'].iloc[i]], tooltip='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i]), popup='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i])).add_to(hm)

folium.TileLayer('openstreetmap').add_to(hm)
hm.save('heatmap_dfw_runways_openstreet.html')
os.system('start heatmap_dfw_runways_openstreet.html')

#%% LAX Section
df_lax = data_df[data_df.AIRPORT_ID == 'KLAX'].reset_index(drop=True)
df_lax = validDataFrame(df_lax, 'RUNWAY')

#%% Lat/Lngs for LAX runways
lngs = [-118.422211, -118.410753, -118.412909, -118.391302] # longitudes for LAX runways
lats = [33.950030, 33.949212, 33.936473, 33.936543] # latitudes for LAX runways

#%% Runway list
rwy_list = ['6R/24L', '6L/24R', '7R/25L', '7L/25R']

#%% Clean up LAX messy data
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('24', '')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('25', '')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('7/25', '')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('8R/26L', '')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('6', '')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('06L', '6L')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('07R', '7R')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('06R', '6R')
df_lax['RUNWAY'] = df_lax['RUNWAY'].replace('22L', '25L')

#%% Get counts of DFW runway incidents
counts = runways(df_lax, rwy_list)

#%% Create data frame of runways with lats, lngs, and counts
df_count = pd.DataFrame({'RUNWAY': rwy_list, 'LATITUDE': lats, 'LONGITUDE': lngs, 'COUNT': counts})

#%% Create heatmap centered on DFW with runway incidents
hm = folium.Map(location=[33.942761, -118.409055], #Center of LAX
               tiles='stamentoner',
               zoom_start=14)

HeatMap(df_count[['LATITUDE', 'LONGITUDE', 'COUNT']], min_opacity=0.75, blur=12).add_to(folium.FeatureGroup(name='Heat Map').add_to(hm))
for i in range(len(df_count)):
    folium.Marker(location=[df_count['LATITUDE'].iloc[i], df_count['LONGITUDE'].iloc[i]], tooltip='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i]), popup='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i])).add_to(hm)

folium.TileLayer('openstreetmap').add_to(hm)
hm.save('heatmap_lax_runways_openstreet.html')
os.system('start heatmap_lax_runways_openstreet.html')

#%% ATL Section
df_atl = data_df[data_df.AIRPORT_ID == 'KATL'].reset_index(drop=True)
df_atl = validDataFrame(df_atl, 'RUNWAY')

#%% Lat/Lngs for LAX runways
lngs = [-84.428405, -84.417076, -84.438190, -84.427890, -84.433334] # longitudes for ATL runways
lats = [33.649586, 33.646799, 33.634687, 33.631900, 33.620305] # latitudes for ATL runways

#%% Runway list
rwy_list = ['8R/26L', '8L/26R', '9R/27L', '9L/27R', '10/28']

#%% Clean up ATL messy data
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

#%% Get counts of DFW runway incidents
counts = runways(df_atl, rwy_list)

#%% Create data frame of runways with lats, lngs, and counts
df_count = pd.DataFrame({'RUNWAY': rwy_list, 'LATITUDE': lats, 'LONGITUDE': lngs, 'COUNT': counts})

#%% Create heatmap centered on DFW with runway incidents
hm = folium.Map(location=[33.635956, -84.425201], #Center of ATL
               tiles='stamentoner',
               zoom_start=14)

HeatMap(df_count[['LATITUDE', 'LONGITUDE', 'COUNT']], min_opacity=0.75, blur=12).add_to(folium.FeatureGroup(name='Heat Map').add_to(hm))
for i in range(len(df_count)):
    folium.Marker(location=[df_count['LATITUDE'].iloc[i], df_count['LONGITUDE'].iloc[i]], tooltip='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i]), popup='RWY {}: {}'.format(df_count['RUNWAY'].iloc[i], df_count['COUNT'].iloc[i])).add_to(hm)

folium.TileLayer('openstreetmap').add_to(hm)
hm.save('heatmap_atl_runways_openstreet.html')
os.system('start heatmap_atl_runways_openstreet.html')

#%%
