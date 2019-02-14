from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
from zeep import Client

from sncf_api import get_departures_time

app = Flask(__name__)

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js',
            'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui.min.css', 'css/clarity-icons.min.css', 'css/overwrite.css')
env.register('css_all', css)
soap_client = Client('http://40.89.190.93/Service_distance_war/services/GpsDistance?wsdl')


@app.route('/', methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        start_station = request.form["start"]
        destination_station = request.form["destination"]
        date_departure = request.form["departure_time"].replace('T', ' ')
        departure_result = get_departures_time(start_station, destination_station, date_departure)
        if departure_result is None:
            return render_template('index.html')
        latitude_from = departure_result["lat_start"]
        longitude_from = departure_result["lon_start"]
        latitude_to = departure_result["lat_end"]
        longitude_to = departure_result["lon_end"]
        distance = round(soap_client.service.getGPSDistance(latitude_from, longitude_from, latitude_to, longitude_to),
                         2)
        price = round(soap_client.service.getPrice(distance, 6), 2)
        out_put_json = {"start": departure_result["station_start_name"],
                        "end": departure_result["station_end_name"], "distance": distance, "price": price,
                        "departures": departure_result["departures"]}
        return render_template('index.html', informations=out_put_json)
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
