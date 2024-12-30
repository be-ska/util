from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)  # Initialize Flask-Bootstrap4

# Simulated GNSS data
@app.route('/')
def index():
    data = {
        "title": "ALIGN RTK 1G",
        "gnss_info": {
            "fix": "3D Fix",
            "sat": 12,
            "lat": 37.7749,
            "lon": -122.4194,
            "alt": 30,
            "volt": 5000,
            "mode": "RTK"
        },
        "ap_mode": {
            "clients": 5,
            "ssid": "MyNetwork",
            "channel": 6
        },
        "external_server": {
            "caster_state": "Connected",
            "ssid": "ExternalNetwork",
            "caster": "192.168.1.100",
            "mount": "Mount1",
            "mount_pass": "pass123"
        },
        "survey_info": {
            "survey": "In Progress",
            "srvalid": "Valid",
            "curracc": 0.5,
            "mindur": 120,
            "acccm": 2
        },
        "static_position": {
            "static": "Enabled",
            "lat": 37.7749,
            "lon": -122.4194,
            "alt": 1000
        }
    }
    return render_template('index.html', data=data)  # Pass data to the template

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
