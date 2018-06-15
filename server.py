from flask import Flask, render_template, send_from_directory
from flask_sslify import SSLify
import ssl
import os

app = Flask(__name__)
sslify = SSLify(app)

@app.route("/")
def index():
    return render_template("website.html")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon2.ico', mimetype='image/x-icon')

##app.add_url_rule('/favicon.ico',
##                 redirect_to=url_for('static', filename='favicon.ico'))

if __name__ == "__main__":        
    context = ('server.crt', 'server.key')
    app.run(host='localhost', port='443', debug=False, ssl_context=context)
