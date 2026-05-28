# Taffic Team App

A web app built to allow users to upload traffic videos and have them analysed by an object detection model to count vehicles.

## Installation

It is recommended to use python >= 3.10, as the application was developed in that version. It is also recommended to install this application through the use of a virtual environment so as to not clutter your global installation.

Clone this repository in your desired folder
```bash
git clone https://github.com/JoshuaDjordjevic/traffic-team-app
```

Create a new virtual environment
```bash
python -m venv .venv
```

Install the required modules after activating environment
```bash
pip install -r requirements.txt
```

Run the Flask app - Note that this will run in debug mode
```bash
python run.py
```

## The Interface

![Screenshot of the web app's interface](images/app_interface.jpg)