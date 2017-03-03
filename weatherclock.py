#!/usr/bin/env python
# Display a WeatherClock with double-buffering.
import sys
sys.path.append('./matrix/python')

import time
import datetime
import requests
import schedule
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from PIL import Image


ZIP_CODE = "14623"
API_KEY = "44a751f5ab2cd6e17bbcbdbd0057140e"

WEATHER_ICONS = {
    '01d': "img/sunny.bmp",          # clear sky
    '02d': "img/partly-cloudy.bmp",  # few clouds
    '03d': "img/cloudy.bmp",         # scattered clouds
    '04d': "img/cloudy.bmp",         # broken clouds
    '09d': "img/rainy.bmp",          # shower rain
    '10d': "img/rainy.bmp",          # rain
    '11d': "img/thundery.bmp",       # thunderstorm
    '13d': "img/snowy.bmp",          # snow
    '50d': "img/misty.bmp"           # mist
}


# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 16
options.chain_length = 1
options.parallel = 2
options.brightness = 50

matrix = RGBMatrix(options = options)

def run():
    offscreen_canvas = matrix.CreateFrameCanvas()
    font = graphics.Font()
    font.LoadFont("matrix/fonts/6x10.bdf")

    font_temp = graphics.Font()
    font_temp.LoadFont("matrix/fonts/5x7.bdf")

    colon = True
    time_x = 2
    time_y = 10
    time_color = graphics.Color(255, 110, 255)

    icon_x = 2
    icon_y = 16

    temp_x = 17
    temp_y = 24
    temp_color = graphics.Color(255, 255, 255)

    temperature, weather_icon = get_weather() #270.23, "../img/sunny.bmp"
    temperature = temperature * 9 / 5 - 459.67
    temperature = "{}F".format(int(temperature))


    while True:
        offscreen_canvas.Clear()

        # set up the time display
        cur_time = datetime.datetime.now().strftime('%H:%M')
        if colon:
            cur_time = cur_time.replace(':', ' ')
        colon = not colon
        graphics.DrawText(offscreen_canvas, font, time_x, time_y, time_color, cur_time)

        # set up the temperature display
        graphics.DrawText(offscreen_canvas, font_temp, temp_x, temp_y, temp_color, temperature)

        # set up the weather glyph to display and apply to canvas
        image = Image.open(weather_icon).convert('RGB')
        offscreen_canvas.SetImage(image, icon_x, icon_y)

        # swap the canvas with the offscreen
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

        if datetime.datetime.now().time() > datetime.time(9, 00):
            #pass
            return

        time.sleep(1)

def get_weather():
    req = requests.get("http://api.openweathermap.org/data/2.5/weather?zip={},us&APPID={}"
                       .format(ZIP_CODE, API_KEY))
    json = req.json()
    if req.status_code != 200:
        print(req, json)
    # remove the 'n' for night icons with 'd' to make everything easier
    icon = WEATHER_ICONS[json['weather'][0]['icon'].replace('n', 'd')]
    return json['main']['temp'], icon


# Main function
if __name__ == "__main__":
    schedule.every().day.at("07:30")
    run()
