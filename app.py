from flask import Flask, render_template, redirect, request, url_for, jsonify, session
from flask_assets import Bundle, Environment
from zeep import Client

app = Flask(__name__)
app.secret_key = "super secret key"

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js',
            'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui.min.css', 'css/clarity-icons.min.css')
env.register('css_all', css)
soap_client = Client('http://no-code-team:8080/Service_distance_war6475660720881532110/services/GpsDistance?wsdl')


@app.route('/', methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
        latitude_from = request.form["latitude_from"]
        longitude_from = request.form["longitude_from"]
        latitude_to = request.form["latitude_to"]
        longitude_to = request.form["longitude_to"]

        distance = soap_client.service.getGPSDistance(latitude_from, longitude_from, latitude_to, longitude_to)
        return render_template('index.html', distance=distance)
    return render_template('index.html')


# @app.route('/vms')
# def vms():
#     return "<h1> VMS </h1>"
#
#
# @app.route('/workflows')
# def vms():
#     return "<h1> workflows </h1>"


if __name__ == '__main__':
    app.run(debug=True)