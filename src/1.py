import configparser
import requests
import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# get api key from config file
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['api']['key']

# api params
city = 'Taipei,tw'
unit = 'metric'

# fire api
api_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + city + '&appid=' + api_key + '&units=' + unit
response = requests.get(api_url)
if response.status_code != 200:
    print('ERROR')
    quit()
else:
    result_json = response.json()
    # get the information we need
    weather = result_json['weather'][0]['main']
    temperature = result_json['main']['temp']
    timestamp = result_json['dt']
    dt_object = datetime.fromtimestamp(timestamp)
    print('- Weather data API process successfully.')
    print('- City: ' + city)
    print('- Unit: ' + unit)
    print('- Weather: ' + weather)
    print('- Temperature: ', temperature)
    print('- Timestamp formatted: ', dt_object)

# check database
try:
    connection = mysql.connector.connect(host='db', database='main', user='root', password='test')
    if connection.is_connected():
        db_info = connection.get_server_info()
        print('- Connected to MySQL Server version: ', db_info)
        cursor = connection.cursor()
        sql_select_query = 'select id from weather_log where city = "' + city + '" and timestamp = "' + str(dt_object) + '"'
        cursor.execute(sql_select_query)
        records = cursor.fetchall()
        if cursor.rowcount > 0:
            # the same data exists, skip insert
            print('- Identical record exists, do nothing and exit.')
        else:
            sql_insert_query = 'insert into weather_log (city, weather, temperature, timestamp) values ("' + city + '", "' + weather + '", ' + str(temperature) + ', "' + str(dt_object) + '")'
            cursor.execute(sql_insert_query)
            connection.commit()
            if cursor.rowcount > 0:
                print('- New weather log data successfully stored to database.')
            else:
                print('- Unknown error while adding log data to database.')

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("- Closed database connection.")



# write to database
