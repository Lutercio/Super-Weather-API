from flask import Flask, jsonify
import requests
import multiprocessing as mp
import time

app = Flask(__name__)

# Keys of acess of the base APIs 
keys = ["", "", "", "", "", ""]

# Functions to "GET" requests of the base APIs
def api0(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m")
    endtime = time.time()
    conecttime = endtime - starttime
    print(f"Pass0 in {conecttime} seconds")
    return response
def api1(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&units=metric&lang=pt_br&exclude=minutely,hourly,daily&appid={keys[1]}")
    endtime = time.time()
    conecttime = endtime - starttime
    print(f"Pass1 in {conecttime} seconds")
    return response
def api2(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.hgbrasil.com/weather?key=SUA-CHAVE&lat={lat}2&lon={lng}&user_ip=remote")
    endtime = time.time()
    conecttime = endtime - starttime
    print(f"Pass2 in {conecttime} seconds")
    return response
def api3(lat, lng):
    starttime = time.time()
    response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={keys[3]}&q={lat},{lng}&aqi=no")
    endtime = time.time()
    conecttime = endtime - starttime
    print(f"Pass3 in {conecttime} seconds")
    return response
def api4(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat}%2C%20{lng}?unitGroup=metric&include=days&key={keys[4]}&contentType=json")
    endtime = time.time()
    conecttime = endtime - starttime
    print(f"Pass4 in {conecttime} seconds")
    return response
def api5(lat, lng):
    starttime = time.time()
    response = requests.get(f"https://api.tomorrow.io/v4/weather/realtime?location={lat},{lng}&apikey={keys[5]}")
    endtime = time.time()
    conecttime = endtime - starttime
    print(f"Pass5 in {conecttime} seconds")
    return response

# Main function of my API
@app.route('/get/<city>')
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
    location = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={keys[0]}")
    loc = location.json()
    lat = loc["results"][0]["geometry"]["location"]["lat"]
    lng = loc["results"][0]["geometry"]["location"]["lng"]
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
        weather_data[5]["data"]["values"]["temperature"]
    ]

    flike_data = [
        weather_data[1]["current"]["feels_like"], 
        weather_data[3]["current"]["feelslike_c"], 
        weather_data[4]["days"][0]["feelslike"], 
        weather_data[5]["data"]["values"]["temperatureApparent"]
    ]

    wspeed_data = [
        weather_data[0]["current_weather"]["windspeed"], 
        weather_data[1]["current"]["wind_speed"], 
        weather_data[3]["current"]["wind_kph"], 
        weather_data[4]["days"][0]["windspeed"], 
        weather_data[5]["data"]["values"]["windSpeed"]
    ]

    print("--------------------")
    print("Temperature")

    i = 0
    while i < 6:
        if temp_data[i] > default_temp - margin and temp_data[i] < default_temp + margin:
            temperature += temp_data[i]
            apicountT += 1
            print(temp_data[i])
        else:
            print(f"API{i} T ERROR")
        i += 1

    print("--------------------")
    print("Feels Like")

    i = 0
    while i < 4:
        if flike_data[i] > default_flike - margin and flike_data[i] < default_flike + margin:
            feels_like += flike_data[i]
            apicountFL += 1
            print(flike_data[i])
        else:
            print(f"API{i} FL ERROR")
        i += 1

    print("--------------------")
    print("Wind Speed")
    
    i = 0
    while i < 5:
        if wspeed_data[i] > default_wspeed - margin and wspeed_data[i] < default_wspeed + margin:
            wind_speed += wspeed_data[i]
            apicountWS += 1
            print(wspeed_data[i])
        else:
            print(f"API{i} WS ERROR")
        i += 1


    # Data that will be returned
    final_api = {
        'temperature': round(temperature / apicountT, 2), # Do a arithmetic average of the sum of all temperature data and the number of API data collected
        'local_time': weather_data[3]["location"]["localtime"],
        'feels_like': round(feels_like / apicountFL, 2),
        'humidity': 0,
        'clouds': 0,
        'wind_speed': round(wind_speed / apicountWS, 2),
        'weather':{
            'id': weather_data[1]["current"]["weather"][0]["id"],
            'main': weather_data[1]["current"]["weather"][0]["main"],
            'description': weather_data[1]["current"]["weather"][0]["description"]
        }
    }

    return jsonify(final_api), 200 # Return the JSON version of the "final_api" dict and the conection code 200

# Main page
@app.route('/')
def home():
    return "", 200

# Error 404 if the page is not found
@app.errorhandler(404)
def page_not_found(error):
    return "<div class='error'><h1>Error 404</h1><p>Page not found<p></div><style>.error{display:grid;place-items:center;}</style>", 404

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
