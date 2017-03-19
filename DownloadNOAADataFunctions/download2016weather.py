# Import necessary modules, functions
import pandas as pd
import re
import json

import requests


# Save token and base url
base_url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/'

# Get the list of airport stations

# Request the information on all airport stations for specific state
def get_airport_stations(my_token, state_FIPS):
	"""
	This function gets the list of airport with 2016 weather data
	----------
	Input: 
		my_token (str)
			token generated from "token request page"
		state_FIPS (int)
			state FIPS code 
	----------
	Output: 
		 dictionary with airport station name as a key and 
		 	station id as a value
	"""
	station_url = '{}stations?locationid=FIPS:{}&datetypeid=GHCND&startdate=2016-01-01&enddate=2016-12-31&limit=1000'.format(base_url, state_FIPS)
	response = requests.get(station_url, headers = {'token': my_token}).json()	

	airport_ids = {}
	for item in response['results']: 
		name = item.get('name')

		if re.search('.*GHCND.*', item.get('id')):
			if re.search('.*AIRPORT.*', name):
				airport_ids[name] = item.get('id')
	return airport_ids

def get_station_info(my_token, station_id):
	"""
	This function gets all the information on the station 
	----------
	Input: 
		my_token (str)
			token generated from "token request page"
		station_id (str)
	----------
	Output: 
		dictionary of station information
	"""	
	station_url = '{}stations/{}'.format(base_url, station_id)
	return requests.get(station_url, headers = {'token': my_token}).json()

def get_data(my_token, dataset_id, data_type_id, station_id):
	"""
	This function gets all the data for specified data type and station
	----------
	Input: 
		my_token (str)
			token generated from "token request page"
		dataset_id: dataset ID 
			ex) GHCND, GSOM, GSOY, NEXRAD2, NEXRAD3, NORMAL_ANN, 
				NORMAL_DLY, NORMAL_HLY, NORMAL_MLY, PRECIP_15, 
				PRECIP_HLY
		data_type_id: data type ID
		station_id: station ID
	----------
	Output: 
		pandas DataFrame
	"""
	data_url = '{}data?datasetid={}&datatypeid={}&stationid={}&startdate=2016-01-01&enddate=2016-12-31&units=standard&limit=1000'\
	.format(base_url, dataset_id, data_type_id, station_id)
	data_json = requests.get(data_url, headers = {'token': my_token}).json()
	
	# Convert JSON format to a single dictionary
	data_dict = {k:[v] for k, v in data_json['results'][0].items()}
	for item in data_json['results'][1:]: 
		for k, v in item.items():
			data_dict[k].append(v)

	# Convert to DataFrame
	df = pd.DataFrame(data_dict)

	# Confirm all one data type, and rename 'value' column
	# to be the data type name
	assert all(df['datatype'] == data_type_id)
	df.drop(['attributes', 'datatype'], axis = 1, inplace = True)
	df.rename(index = str, columns = {'value': data_type_id}, inplace = True)

	return  df