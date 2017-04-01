# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, jsonify, request
from twilio.rest import TwilioRestClient
import serial
from haversine import haversine
import json


with open('data.json', 'r') as data_file:
    SERIAL_TO_PHONE = json.load(data_file)

# Initialize the Flask application
app = Flask(__name__)
PORT = "COM17"
DEBUG = True
# Find these values at https://twilio.com/user/account
account_sid = 
auth_token = 
from_number = 
SMS_BODY = "Hi, the pollution levels in your vincinity are as follows\nAir "\
    "Quality: %s \nSmoke Level: %s"


# Define a route for the default URL, which loads the form
@app.route('/')
def main():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        name = request.form.get("name")
        serial = request.form.get("serial")
        phone = request.form.get("phone")
        data = {
            'name': name,
            'serial': serial,
            'phone': phone,
        }
        SERIAL_TO_PHONE[serial] = data

        with open('data.json', 'w') as outfile:
            json.dump(SERIAL_TO_PHONE, outfile)
        return ("User registered", 200)
    return render_template('register.html')


@app.route('/log/', methods=['GET'])
def auto_location():
    try:
        lat = float(request.args.get('latitude'))
        lon = float(request.args.get('longitude'))
        phone_serial = request.args.get('serial')
    except (TypeError, ValueError):
        return ("Please verify latitude, longitude"
                " and Serial Number value\nExpected: "
                "/log/?latitude=lat&longitude=lon&serial=serial", 406)
    if lat is None:
        return ("Missing Latitude parameter.\nExpected: "
                "/log/?latitude=lat&longitude=lon&serial=serial", 406)
    if lon is None:
        return ("Missing Longitude parameter\nExpected: "
                "/log/?latitude=lat&longitude=lon&serial=serial", 406)
    if phone_serial is None:
        return ("Missing Serial number parameter\nExpected: "
                "/log/?latitude=lat&longitude=lon&serial=serial", 406)

    if not DEBUG:
        ser = serial.Serial(port=PORT, baudrate=9600)
        line = ser.readline()
    else:
        line = "20.917453474.76927800030000100"
    m_lat = float(line[:10])
    m_lon = float(line[10:20])
    dist = haversine((lat, lon), (m_lat, m_lon))
    print("Haversine: %s " % dist)
    print("Serial: %s" % phone_serial)
    if dist < 1:
        print("In proximity of sensor. Sending sms")
        return send_sms(phone_serial)
    return ("Away from sensors", 200)


@app.route('/update/', methods=['POST'])
def update_map():
    try:
        if not DEBUG:
            ser = serial.Serial(port=PORT, baudrate=9600)
            line = ser.readline()
        else:
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
        print("Unable to decode: %s " % line)
    return jsonify({})


def send_sms(phone_serial):
    try:
        if not DEBUG:
            ser = serial.Serial(port=PORT, baudrate=9600)
            line = ser.readline()
        else:
            line = "20.917453474.76927800030000100"
        line.decode('ascii')
        val1 = int(line[20:25])
        val2 = int(line[25:30])
    except UnicodeDecodeError:
        print("Unable to decode: %s " % line)
        return jsonify({})
    client = TwilioRestClient(account_sid, auth_token)
    body = SMS_BODY % (val1, val2)
    try:
        to_number = SERIAL_TO_PHONE[phone_serial]['phone']
    except KeyError:
        print("USER not registered. Please register before trying again.")
        return ("USER not registered. Please register before trying again.",
                406)
    client.messages.create(
        to=to_number, from_=from_number,
        body=body)
    print("MESSAGE SENT to %s" % to_number)
    return ("MESSAGE SENT to %s" % to_number, 200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
