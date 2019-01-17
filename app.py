from flask import Flask, render_template, redirect, request, url_for, jsonify, session
from flask_assets import Bundle, Environment

app = Flask(__name__)
app.secret_key = "super secret key"

env = Environment(app)
js = Bundle('js/clarity-icons.min.js', 'js/clarity-icons-api.js',
            'js/clarity-icons-element.js', 'js/custom-elements.min.js')
env.register('js_all', js)
css = Bundle('css/clarity-ui.min.css', 'css/clarity-icons.min.css')
env.register('css_all', css)


@app.route('/', methods=["GET", "POST"])
def homepage():
    if request.method == "POST": 
        attempted_username = request.form['username']
        print(attempted_username)
        attempted_password = request.form['password']
        print(attempted_password)
        if attempted_username == "admin" and attempted_password == "password":
            session['logged_in'] = True
            session['wrong_pass'] = False
            session['username'] = request.form['username']
            return redirect(url_for('homepage'))
        else:
            session['logged_in'] = False
            session['wrong_pass'] = True
    return render_template('index.html')


@app.route('/vms')
def vms():
    return "<h1> VMS </h1>"


@app.route('/workflows')
def vms():
    return "<h1> workflows </h1>"


if __name__ == '__main__':
    app.run(debug=True)