from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import multiprocessing as mp
import time
import json
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
app.json.sort_keys = False

# Keys of acess of the base APIs
keys = [os.getenv(f"KEY_{i}") for i in range(6)]
timeout = 10

# Functions to "GET" requests of the base APIs
def api0(lat, lng):
    with requests.Session() as session:
        starttime = time.time()
        response = session.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true", timeout=timeout)
        endtime = time.time()
    print(f"api0 - Connection time: {endtime - starttime} seconds")
    return response

def api1(lat, lng):
    with requests.Session() as session:
        starttime = time.time()
        response = session.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&units=metric&lang=pt_br&exclude=minutely,hourly&appid={keys[1]}")
        endtime = time.time()
    print(f"api1 - Connection time: {endtime - starttime} seconds")
    return response

def api2(lat, lng):
    with requests.Session() as session:
        starttime = time.time()
        response = session.get(f"https://api.hgbrasil.com/weather?key=SUA-CHAVE&lat={lat}2&lon={lng}&user_ip=remote", timeout=timeout)
        endtime = time.time()
    print(f"api2 - Connection time: {endtime - starttime} seconds")
    return response

def api3(lat, lng):
    with requests.Session() as session:
        starttime = time.time()
        response = session.get(f"http://api.weatherapi.com/v1/current.json?key={keys[3]}&q={lat},{lng}&aqi=no", timeout=timeout)
        endtime = time.time()
    print(f"api3 - Connection time: {endtime - starttime} seconds")
    return response

def api4(lat, lng):
    with requests.Session() as session:
        starttime = time.time()
        response = session.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat}%2C%20{lng}?unitGroup=metric&include=days&key={keys[4]}&contentType=json", timeout=timeout)
        endtime = time.time()
    print(f"api4 - Connection time: {endtime - starttime} seconds")
    return response

def api5(lat, lng):
    with requests.Session() as session:
        starttime = time.time()
        response = session.get(f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lng}&apikey={keys[5]}", timeout=timeout)
        endtime = time.time()
    print(f"api5 - Connection time: {endtime - starttime} seconds")
    return response


# Main function of the API
@app.route('/get/?search=<city>')
def get_weather(city):
    # Initializate some variables 
    apicountT = 0
    apicountFL = 0
    apicountWS = 0
    apicountH = 0
    temperature = 0
    humidity = 0
    feels_like = 0
    wind_speed = 0

    # Get the latitude and longitude of the city/place after the "get/" from google maps API
    location = requests.get(f"https://nominatim.openstreetmap.org/search?q={city}&format=json")
    loc = location.json()
    print(f"https://nominatim.openstreetmap.org/search?q={city}&format=json")
    print(json.dumps(loc, indent=2))
    try:
        lat = loc[0]["lat"]
    except:
        return jsonify({'message': "NOT_FOUND"}), 400
    lng = loc[0]["lon"]
    print(lat, lng)

    processes = [] # Create the paralelism variable array as empty

    # Create the poll to manage the process
    with mp.Pool() as pool:
        # Loop that get the request for each API
        for api_func in [api0, api1, api2, api3, api4, api5]:
            process = pool.apply_async(api_func, args=(lat, lng)) # Create the process to run any "api" funtion
            processes.append(process) # Append the function to the "processes" array

        # Use the "GET" method for each element in the "processes" array
        responses = []
        for process in processes:
            try:
                response = process.get(timeout=timeout)
                if response is not None:
                    responses.append(response)
            except Exception as e:
                print(f"Error getting response: {e}")

    weather_data = []   # Create the weather data array as empty

    # Loop for get the data of each element in "responses" array
    for response in responses:
        # Verify if the response of the APIs was successfully done
        if response.status_code == 200:
            weather_data.append(response.json()) # Uses the ".json" method to interpret the JSON for Python
        else:
            print("API ERROR")

    #debug
    print(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true")
    print(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&exclude=minutely,hourly&units=metric&appid=a855b02b7c3ea7131dc80891d98100fb")
    print(f"https://api.hgbrasil.com/weather?key=SUA-CHAVE&lat={lat}2&lon={lng}&user_ip=remote")
    print(f"http://api.weatherapi.com/v1/current.json?key={keys[3]}&q={lat},{lng}&aqi=no")
    print(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat}%2C%20{lng}?unitGroup=metric&include=days&key={keys[4]}&contentType=json")
    print(f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lng}&apikey={keys[5]}")
    
    i = 0
    while i < 1:
        try:
            default_temp = weather_data[i]["current"]["temp"] # Use OpenWeather to compare with other APIs data
            default_flike = weather_data[i]["current"]["feels_like"]
            default_wspeed = weather_data[i]["current"]["wind_speed"]
            default_humidity = weather_data[i]["current"]["humidity"]
        except:
            None
        i += 1
    margin = 3 # Define a margin

    #Collect the data into some matrizes with an Error Handler in case of Error
    temp_data = []
    temp_index = [
        [0,"current_weather", "temperature"],
        [1,"current", "temp"],
        [2,"results", "temp"],
        [3,"current", "temp_c"],
        [4,"days", 0, "temp"],
        [5,"data", "values", "temperature"]
    ]

    i = 0
    while i < len(temp_index):
        if len(temp_index[i]) == 3:
            try:
                temp_data.append(weather_data[temp_index[i][0]][temp_index[i][1]][temp_index[i][2]])
            except:
                None
        else:
            try:
                temp_data.append(weather_data[temp_index[i][0]][temp_index[i][1]][temp_index[i][2]][temp_index[i][3]])
            except:
                None
        i += 1

    flike_data = []
    flike_index = [
        [1, "current", "feels_like"],
        [3, "current", "feelslike_c"],
        [4, "days", 0, "feelslike"],
        [5, "data", "values", "temperatureApparent"]
    ]

    i = 0
    while i < len(flike_index):
        if len(flike_index[i]) == 3:
            try:
                flike_data.append(weather_data[flike_index[i][0]][flike_index[i][1]][flike_index[i][2]])
            except:
                None
        else:
            try:
                flike_data.append(weather_data[flike_index[i][0]][flike_index[i][1]][flike_index[i][2]][flike_index[i][3]])
            except:
                None
        i += 1

    wspeed_data = []
    wspeed_index = [
        [0, "current_weather", "windspeed", "kmph"],
        [1, "current", "wind_speed"],
        [3, "current", "wind_kph", "kmph"],
        [4, "days", 0, "windspeed", "kmph"],
        [5, "data", "values", "windSpeed"]
    ]

    i = 0
    while i < len(wspeed_index):
        if "kmph" in wspeed_index[i]:
            if len(wspeed_index[i]) == 4:
                try:
                    wspeed_data.append(weather_data[wspeed_index[i][0]][wspeed_index[i][1]][wspeed_index[i][2]] / 3.6)
                except:
                    None
            else:
                try:
                    wspeed_data.append(weather_data[wspeed_index[i][0]][wspeed_index[i][1]][wspeed_index[i][2]][wspeed_index[i][3]] / 3.6)
                except:
                    None
        elif len(wspeed_index[i]) == 3:
            try:
                wspeed_data.append(weather_data[wspeed_index[i][0]][wspeed_index[i][1]][wspeed_index[i][2]])
            except:
                None
        else:
            try:
                wspeed_data.append(weather_data[wspeed_index[i][0]][wspeed_index[i][1]][wspeed_index[i][2]][wspeed_index[i][3]])
            except:
                None
        i += 1

    humidity_data = []
    humidity_index = [
        [1, "current", "humidity"],
        [2, "results", "humidity"],
        [3, "current", "humidity"],
        [4, "days", 0, "humidity"],
        [5, "data", "values", "humidity"]
    ]

    i = 0
    while i < len(humidity_index):
        if len(humidity_index[i]) == 3:
            try:
                humidity_data.append(weather_data[humidity_index[i][0]][humidity_index[i][1]][humidity_index[i][2]])
            except:
                None
        else:
            try:
                humidity_data.append(weather_data[humidity_index[i][0]][humidity_index[i][1]][humidity_index[i][2]][humidity_index[i][3]])
            except:
                None
        i += 1

    #Compare the data with a margin and print them for debug
    print("--------------------")
    print("Temperature")

    i = 0
    while i < len(temp_data):
        if temp_data[i] > default_temp - margin and temp_data[i] < default_temp + margin:
            temperature += temp_data[i]
            apicountT += 1
            print(temp_data[i])
        else:
            print(f"API{i} T FAIL ({temp_data[i]})")
        i += 1

    print("--------------------")
    print("Feels Like")

    i = 0
    while i < len(flike_data):
        if flike_data[i] > default_flike - margin and flike_data[i] < default_flike + margin:
            feels_like += flike_data[i]
            apicountFL += 1
            print(flike_data[i])
        else:
            print(f"API{i} FL FAIL ({flike_data[i]})")
        i += 1

    print("--------------------")
    print("Wind Speed")
    
    i = 0
    while i < len(wspeed_data):
        if wspeed_data[i] > default_wspeed - margin and wspeed_data[i] < default_wspeed + margin:
            wind_speed += wspeed_data[i]
            apicountWS += 1
            print(round(wspeed_data[i], 2))
        else:
            print(f"API{i} WS FAIL ({round(wspeed_data[i], 2)})")
        i += 1

    print("--------------------")
    print("Humidity")
    
    i = 0
    while i < len(humidity_data):
        if humidity_data[i] > default_humidity - margin * 3 and humidity_data[i] < default_humidity + margin * 3:
            humidity += humidity_data[i]
            apicountH += 1
            print(humidity_data[i])
        else:
            print(f"API{i} H FAIL ({humidity_data[i]})")
        i += 1


    # Data that will be returned
    final_api = {
        'location': {
                'adresstype': loc[0]["addresstype"],
                'name': weather_data[3]["location"]["name"],
                'region': weather_data[3]["location"]["region"],
                'country': weather_data[3]["location"]["country"],
                'local_time': weather_data[3]["location"]["localtime"],
                'timezone': weather_data[1]["timezone"],
                'dt': weather_data[1]["current"]["dt"]
        },
        'current': {
            'temperature': round(temperature / apicountT, 2), # Do a arithmetic average of the sum of all temperature data and the number of API data collected
            'feels_like': round(feels_like / apicountFL, 2),
            'wind_speed': round(wind_speed / apicountWS, 2),
            'sunrise': weather_data[1]["current"]["sunrise"],
            'sunset': weather_data[1]["current"]["sunset"],
            'humidity': round(humidity / apicountH, 2),
            'clouds': weather_data[1]["current"]["clouds"],
            'weather':{
                'id': weather_data[1]["current"]["weather"][0]["id"],
                'main': weather_data[1]["current"]["weather"][0]["main"],
                'description': weather_data[1]["current"]["weather"][0]["description"]
            }
        },
        'daily': []
    }

    for daily_data in weather_data[1]["daily"]:
        final_api["daily"].append({
            'dt': daily_data["dt"],
            'sunrise': daily_data["sunrise"],
            'sunset': daily_data["sunset"],
            'temperature': {
                'min': daily_data["temp"]["min"],
                'max': daily_data["temp"]["max"]
            },
            'humidity': daily_data["humidity"],
            'wind_speed': daily_data["wind_speed"],
            'weather': {
                'id': daily_data["weather"][0]["id"],
                'main': daily_data["weather"][0]["main"],
                'description': daily_data["weather"][0]["description"],
                'icon': daily_data["weather"][0]["icon"]
            }
    })

    return jsonify(final_api), 200 # Return the JSON version of the "final_api" dict and the conection code 200

@app.route('/get/')
def get_html():
    index_city = request.args.get("search")
    if index_city != None:
        return get_weather(index_city)
    return home()

@app.route("/ip")
def get_ip():
    ip_response = requests.get("https://api64.ipify.org/?format=json")
    ip_data = ip_response.json()
    ip_address = ip_data["ip"]

    location_response = requests.get(f"http://ip-api.com/json/{ip_address}")
    location_data = location_response.json()

    ip_log = {
        'city': location_data["city"],
        'region': location_data["region"],
        'country': location_data["country"]
    }

    return jsonify(ip_log)

# Main page
@app.route('/')
def home():
    return render_template("index.html"), 200

# Error 404 if the page is not found
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

#Get the enviroments variebles
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')

if __name__ == '__main__':
    app.run()