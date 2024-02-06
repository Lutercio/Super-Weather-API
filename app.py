from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import multiprocessing as mp
import time
import json

app = Flask(__name__)
CORS(app)

# Keys of acess of the base APIs 
keys = ["AIzaSyDPGWdhfrPDMa2xMXUen940TptcccgUZrA", "b8e9cc118639cd4491d6aae15fd2b57e", "", "fbdb034be5e345d5b51184535232608", "3LFSFM734XHLRFZTTJ6SM638L", "eLXXd2jxYZTWjb1muJyOzUVNKCYYR0w7"]

# Functions to "GET" requests of the base APIs
def api0(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m")
    endtime = time.time()
    print(f"Pass0 in {endtime - starttime} seconds")
    return response
def api1(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&units=metric&lang=pt_br&exclude=minutely,hourly,daily&appid={keys[1]}")
    endtime = time.time()
    print(f"Pass1 in {endtime - starttime} seconds")
    return response
def api2(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.hgbrasil.com/weather?key=SUA-CHAVE&lat={lat}2&lon={lng}&user_ip=remote")
    endtime = time.time()
    print(f"Pass2 in {endtime - starttime} seconds")
    return response
def api3(lat, lng):
    starttime = time.time()
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={keys[3]}&q={lat},{lng}&aqi=no")
    endtime = time.time()
    print(f"Pass3 in {endtime - starttime} seconds")
    return response
def api4(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat}%2C%20{lng}?unitGroup=metric&include=days&key={keys[4]}&contentType=json")
    endtime = time.time()
    print(f"Pass4 in {endtime - starttime} seconds")
    return response
def api5(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lng}&apikey={keys[5]}")
    endtime = time.time()
    print(f"Pass5 in {endtime - starttime} seconds")
    return response

# Main function of the API
@app.route('/get/?search=<city>')
def get_weather(city):
    # Initializate some variables 
    apicountT = 0
    apicountFL = 0
    apicountWS = 0
    temperature = 0
    humidity = 0
    feels_like = 0
    wind_speed = 0

    # Get the latitude and longitude of the city/place after the "get/" from google maps API
    location = requests.get(f"https://nominatim.openstreetmap.org/search?q={city}&format=json")
    loc = location.json()
    print(f"https://nominatim.openstreetmap.org/search?q={city}&format=json")
    print(json.dumps(loc, indent=2))
    lat = loc[0]["lat"]
    lng = loc[0]["lon"]
    print(lat, lng)

    processes = [] # Create the paralelism variable array as empty

    # Create the poll to manage the process
    with mp.Pool() as pool:
        # Loop that get the request for each API
        for api_func in [api0, api1, api2, api3, api4, api5]:
            process = pool.apply_async(api_func, args=(lat, lng)) # Create the process to run any "api" funtion
            processes.append(process) # Append the function to the "processes" array

        responses = [process.get() for process in processes] # Use the "GET" method for each element in the "processes" array

    weather_data = []   # Create the weather data array as empty

    # Loop for get the data of each element in "responses" array
    for response in responses:
        # Verify if the response of the APIs was successfully done
        if response.status_code == 200:
            weather_data.append(response.json()) # Uses the ".json" method to interpret the JSON for Python
        else:
            print("API ERROR")

    #debug
    print(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&units=metric&lang=pt_br&exclude=minutely,hourly,daily&appid={keys[1]}")
    print(f"https://api.hgbrasil.com/weather?key=SUA-CHAVE&lat={lat}2&lon={lng}&user_ip=remote")
    print(f"http://api.weatherapi.com/v1/current.json?key={keys[3]}&q={lat},{lng}&aqi=no")
    print(f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lng}&apikey={keys[5]}")
    
    default_temp = weather_data[1]["current"]["temp"] # Use OpenWeather to compare with other APIs data
    default_flike = weather_data[1]["current"]["feels_like"]
    default_wspeed = weather_data[1]["current"]["wind_speed"]
    margin = 3 # Define a margin

    temp_data = [
        weather_data[0]["current_weather"]["temperature"], 
        weather_data[1]["current"]["temp"], 
        weather_data[2]["results"]["temp"], 
        weather_data[3]["current"]["temp_c"], 
        weather_data[4]["days"][0]["temp"], 
        #weather_data[5]["data"]["values"]["temperature"]
    ]

    flike_data = [
        weather_data[1]["current"]["feels_like"], 
        weather_data[3]["current"]["feelslike_c"], 
        weather_data[4]["days"][0]["feelslike"], 
        #weather_data[5]["data"]["values"]["temperatureApparent"]
    ]

    wspeed_data = [
        weather_data[0]["current_weather"]["windspeed"] / 3.6, 
        weather_data[1]["current"]["wind_speed"], 
        weather_data[3]["current"]["wind_kph"] / 3.6, 
        weather_data[4]["days"][0]["windspeed"] / 3.6, 
        #weather_data[5]["data"]["values"]["windSpeed"]
    ]

    print("--------------------")
    print("Temperature")

    i = 0
    while i < 5:
        if temp_data[i] > default_temp - margin and temp_data[i] < default_temp + margin:
            temperature += temp_data[i]
            apicountT += 1
            print(temp_data[i])
        else:
            print(f"API{i} T ERROR ({temp_data[i]})")
        i += 1

    print("--------------------")
    print("Feels Like")

    i = 0
    while i < 3:
        if flike_data[i] > default_flike - margin and flike_data[i] < default_flike + margin:
            feels_like += flike_data[i]
            apicountFL += 1
            print(flike_data[i])
        else:
            print(f"API{i} FL ERROR ({flike_data[i]})")
        i += 1

    print("--------------------")
    print("Wind Speed")
    
    i = 0
    while i < 4:
        if wspeed_data[i] > default_wspeed - margin and wspeed_data[i] < default_wspeed + margin:
            wind_speed += wspeed_data[i]
            apicountWS += 1
            print(wspeed_data[i])
        else:
            print(f"API{i} WS ERROR ({wspeed_data[i]})")
        i += 1


    # Data that will be returned
    final_api = {
        'temperature': round(temperature / apicountT, 2), # Do a arithmetic average of the sum of all temperature data and the number of API data collected
        'location':{
            'adresstype': loc[0]["addresstype"],
            'name': weather_data[3]["location"]["name"],
            'region': weather_data[3]["location"]["region"],
            'country': weather_data[3]["location"]["country"]
        },
        'local_time': weather_data[3]["location"]["localtime"],
        'timezone': weather_data[1]["timezone"],
        'dt': weather_data[1]["current"]["dt"],
        'sunrise': weather_data[1]["current"]["sunrise"],
        'sunset': weather_data[1]["current"]["sunset"],
        'feels_like': round(feels_like / apicountFL, 2),
        'humidity': weather_data[1]["current"]["humidity"],
        'clouds': weather_data[1]["current"]["clouds"],
        'wind_speed': round(wind_speed / apicountWS, 2),
        'weather':{
            'id': weather_data[1]["current"]["weather"][0]["id"],
            'main': weather_data[1]["current"]["weather"][0]["main"],
            'description': weather_data[1]["current"]["weather"][0]["description"]
        }
    }

    return jsonify(final_api), 200 # Return the JSON version of the "final_api" dict and the conection code 200

@app.route('/get/')
def get_html():
    index_city = request.args.get("search")
    if index_city != None:
        return get_weather(index_city)
    return home()

# Main page
@app.route('/')
def home():
    return render_template("index.html"), 200

# Error 404 if the page is not found
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
