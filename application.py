import json

import requests
from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
from zeep import Client

from sncf_api import get_departures_time, found_station

app = Flask(__name__)

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js',
            'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui.min.css', 'css/clarity-icons.min.css', 'css/overwrite.css')
env.register('css_all', css)

# Soap client
soap_client = Client('http://40.89.190.93/Service_distance_war/services/GpsDistance?wsdl')

SERVER_IP = "town-info.azurewebsites.net"


def get_town_information(town_name):
    """

    :param town_name:
    :return:
    """
    try:
        town = town_name[town_name.find('(') + 1:town_name.find(')')].lower().strip()
    except Exception:
        town = town_name
    responce = requests.post("http://{}".format(SERVER_IP),
                             data=json.dumps({"wikipedia": town}),
                             headers={'Content-type': 'application/json'})
    try:
        return responce.json()["summary"]
    except KeyError:
        return "Information non trouver"


@app.route('/', methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        # If he enter the station name
        if "select_station" in request.form:
            start_station = request.form["start"]
            destination_station = request.form["destination"]
            stations_found_start = found_station(start_station)
            stations_found_end = found_station(destination_station)
            return render_template('index.html', gare_list={"start": stations_found_start, "end": stations_found_end})
        elif "info_city" in request.form:
            nom = request.form["info_city"]
            return render_template('index.html', town_info=nom)

        # If he select the final station name
        start_station = request.form["station_start"]
        destination_station = request.form["station_end"]
        date_departure = request.form["departure_time"].replace('T', ' ')
        departure_result = get_departures_time(start_station, destination_station, date_departure)
        if departure_result is None:
            return render_template('index.html')
        latitude_from = departure_result["lat_start"]
        longitude_from = departure_result["lon_start"]
        latitude_to = departure_result["lat_end"]
        longitude_to = departure_result["lon_end"]
        # Get the distance with the soap
        distance = round(soap_client.service.getGPSDistance(latitude_from, longitude_from, latitude_to, longitude_to),
                         2)
        # Get the price
        price = round(soap_client.service.getPrice(distance, 6), 2)
        if request.form.getlist('town_info'):
            town_info = get_town_information(destination_station)
        else:
            town_info = ""
        out_put_json = {"start": departure_result["station_start_name"],
                        "end": departure_result["station_end_name"], "distance": distance, "price": price,
                        "departures": departure_result["departures"],
                        "town_info": town_info}
        return render_template('index.html', informations=out_put_json)
    return render_template('index.html')
