#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

import datetime
import json
import time
import urllib3
from xml.etree import ElementTree

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class BartHandler(webapp2.RequestHandler):
    def get(self):
        self.response.content_type = "text/plain"
        
        station = self.request.get('s')
        direction = self.request.get('d')
        travel_time = 5
        try:
            travel_time = int(self.request.get('t', '0'))
        except:
            pass

        if station == '':
            who = self.request.get('w')
            if who == 'g':
                station = 'woak'
                direction = 's'
                travel_time = 11
            else:
                station = '16th'
                direction = 'n'
                travel_time = 7
        
        http = urllib3.PoolManager()
        uri = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=%s&dir=%s&key=MW9S-E7SL-26DU-VV8V"% (station, direction)
        response = http.request('GET', uri)
        root = ElementTree.fromstring(response.data)

        min_travel_time = -1
        for estimate in root.iter('estimate'):
            try:
                t = int(estimate.find('minutes').text)
                if t > travel_time and (min_travel_time == -1 or t < min_travel_time):
                    min_travel_time = t
            except:
                pass

        min_travel_time -= travel_time
        self.response.write("%d" % max(0, min_travel_time))
            

class WeatherHandler(webapp2.RequestHandler):
    def get(self):
        white = [255,255,255]
        gray  = [100,100,100]
        black = [  0,  0,  0]
        blue  = [  0,  0,200]
        
        self.response.content_type = "text/plain"
        
        http = urllib3.PoolManager()
        weather_id = self.request.get('i')
        if weather_id == '':
            who = self.request.get('w')
            if who == 'g':
                weather_id = 5378538
            else:
                weather_id = 5391959
        uri = "http://api.openweathermap.org/data/2.5/forecast?id=%s&units=imperial&appid=bd82977b86bf27fb59a04b61b657fb6f"% (weather_id)
        response = http.request('GET', uri)
        data = json.loads(response.data)
        
        now = datetime.datetime.now()
        max_temp = max([l['main']['temp_max'] for l in data['list'] if (datetime.datetime.fromtimestamp(l['dt']) - now).total_seconds() < (24 * 60 * 60)])
        min_temp = min([l['main']['temp_min'] for l in data['list'] if (datetime.datetime.fromtimestamp(l['dt']) - now).total_seconds() < (24 * 60 * 60)])
        
        ## Taken from https://temboo.com/processing/display-temperature
        minTemp = 40
        maxTemp = 85
        max_temperature_color = min([255, max([0, int(255 * (max_temp - minTemp) / (maxTemp - minTemp))])])
        min_temperature_color = min([255, max([0, int(255 * (min_temp - minTemp) / (maxTemp - minTemp))])])

        self.response.write("%d,%d" % (min_temperature_color << 16 | (255 - min_temperature_color), max_temperature_color << 16 | (255 - max_temperature_color)))


class TimeHandler(webapp2.RequestHandler):
    def get(self):
        self.response.content_type = "text/plain"
        self.response.write("%d" % time.time())


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bart', BartHandler),
    ('/weather', WeatherHandler),
    ('/b', BartHandler),
    ('/w', WeatherHandler),
    ('/t', TimeHandler),
], debug=True)
