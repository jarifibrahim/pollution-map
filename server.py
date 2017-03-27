# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, jsonify
from twilio.rest import TwilioRestClient
import serial
import os


# Initialize the Flask application
app = Flask(__name__)
PORT = "COM17"


# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('index.html')


@app.route('/update/', methods=['POST'])
def update_map():
    try:
        ser = serial.Serial(port=PORT, baudrate=9600)
        line = ser.readline()
        line = "20.917453474.76927800030000100"
        line.decode('ascii')
        lat = float(line[:10])
        lon = float(line[10:20])
        val1 = int(line[20:25])
        val2 = int(line[25:30])
        return jsonify({
            'lat': lat, 'lon': lon, 'val1': val1, 'val2': val2
        })
    except UnicodeDecodeError:
        return jsonify({})


@app.route('/send_sms/', methods=['POST'])
def send_sms():
    try:
        ser = serial.Serial(port=PORT, baudrate=9600)
        line = ser.readline()
        line = "20.917453474.76927800030000100"
        line.decode('ascii')
        val1 = int(line[20:25])
        val2 = int(line[25:30])

    except UnicodeDecodeError:
        return jsonify({})
    # Find these values at https://twilio.com/user/account
    account_sid = os.getenv("TWILIO_SID", "")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    client = TwilioRestClient(account_sid, auth_token)
    body = "Air Quality: %s and Smoke: %s" % (val1, val2)
    client.messages.create(
        to="+919049426428", from_="+18327357699",
        body=body)
    return jsonify({'status': True})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
