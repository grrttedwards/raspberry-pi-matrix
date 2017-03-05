#!/usr/bin/env python
# Display a WeatherClock with double-buffering.
import sys
sys.path.append('./matrix/python')

import os
import sys
import time as time_sleep
import requests
from datetime import datetime, time, timedelta
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from PIL import Image


try:
    CITY_ID = os.environ['WEATHER_CITY_ID']
    API_KEY = os.environ['WEATHER_API_KEY']
except KeyError:
    print("WEATHER_CITY_ID or WEATHER_API_KEY is not set. Exiting.")
    sys.exit(1)

WEATHER_ICONS = {
    '01d': "img/sunny.bmp",          # clear sky
    '02d': "img/partly-cloudy.bmp",  # few clouds
    '03d': "img/cloudy.bmp",         # scattered clouds
    '04d': "img/cloudy.bmp",         # broken clouds
    '09d': "img/rainy.bmp",          # shower rain
    '10d': "img/rainy.bmp",          # rain
    '11d': "img/thundery.bmp",       # thunderstorm
    '13d': "img/snowy.bmp",          # snow
    '50d': "img/misty.bmp",          # mist
    '01n': "img/moony.bmp",          # night clear sky
    '02n': "img/partly-cloudy-night.bmp" # night few clouds
}

# configuration for the matrix
options = RGBMatrixOptions()
options.rows = 16
options.chain_length = 1
options.parallel = 2
options.brightness = 50

matrix = RGBMatrix(options = options)

# time styling and positioning
font = graphics.Font()
font.LoadFont("matrix/fonts/6x10.bdf")
time_color = graphics.Color(255, 110, 255)
time_x, time_y = 2, 10

# weather icon styling and positioning
icon_x, icon_y = 2, 16

# temp styling and positioning
font_temp = graphics.Font()
font_temp.LoadFont("matrix/fonts/5x7.bdf")
temp_color = graphics.Color(0, 179, 239)
temp_x, temp_y = 17, 24

def run():
    offscreen_canvas = matrix.CreateFrameCanvas()
    # schedule one weather update immediately
    time_to_update = datetime.now()
    # colon toggle for time
    colon = True
    while True:

        offscreen_canvas.Clear()

        # when to go blank for the night
        if datetime.now().time() >= time(12, 00):
            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            return

        # set up the time display
        cur_time = datetime.now().strftime('%H:%M')
        if colon:
            cur_time = cur_time.replace(':', ' ')
        colon = not colon
        graphics.DrawText(offscreen_canvas, font, time_x, time_y, time_color, cur_time)

        # make request for weather if enough time has passed
        if datetime.now() >= time_to_update:
            temperature, glyph = get_weather()
            time_to_update = datetime.now() + timedelta(hours=1)
        # set up the weather glyph to display
        offscreen_canvas.SetImage(glyph, icon_x, icon_y)
        # set up the temperature display
        graphics.DrawText(offscreen_canvas, font_temp, temp_x, temp_y, temp_color, temperature)

        # swap the canvas with the offscreen
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

        time_sleep.sleep(1)

def get_weather():
    req = requests.get("http://api.openweathermap.org/data/2.5/weather?id={}&APPID={}"
                       .format(CITY_ID, API_KEY))
    json = req.json()
    if req.status_code != 200:
        print(req, json)
    icon = json['weather'][0]['icon']
    # see if there is a night glyph else get the day variant to make everything easier
    try:
    	icon_path = WEATHER_ICONS[icon]
    except KeyError:
    	icon_path = WEATHER_ICONS[icon.replace('n', 'd')]
    glyph = Image.open(icon_path).convert('RGB')
    # convert kelvin to degrees F
    temperature = json['main']['temp'] * 9 / 5 - 459.67
    temperature = "{}F".format(int(temperature))
    return temperature, glyph


# Main function
if __name__ == "__main__":
    while True:
        if datetime.now().time() >= time(7, 30):
            run()
        time_sleep.sleep(60)
