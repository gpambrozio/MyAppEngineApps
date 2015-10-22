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
import urllib3
from xml.etree import ElementTree

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class BartHandler(webapp2.RequestHandler):
    def get(self):
        self.response.content_type = "text/plain"
        
        http = urllib3.PoolManager()
        uri = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig=%s&dir=%s&key=MW9S-E7SL-26DU-VV8V"% (self.request.get('s'), self.request.get('d'))
        response = http.request('GET', uri)
        root = ElementTree.fromstring(response.data)

        travel_time = 5
        try:
            travel_time = int(self.request.get('t'))
        except:
            pass
        
        min_travel_time = -1
        for estimate in root.iter('estimate'):
            try:
                t = int(estimate.find('minutes').text)
                if t > travel_time and (min_travel_time == -1 or t < min_travel_time):
                    min_travel_time = t
            except:
                pass

        min_travel_time -= travel_time
        self.response.write("%d" % min_travel_time)
            

class WeatherHandler(webapp2.RequestHandler):
    def get(self):
        white = [255,255,255]
        gray  = [100,100,100]
        black = [  0,  0,  0]
        blue  = [  0,  0,200]
        
        self.response.content_type = "text/plain"
        
        http = urllib3.PoolManager()
        uri = "http://api.openweathermap.org/data/2.5/forecast?id=%s&units=imperial&appid=bd82977b86bf27fb59a04b61b657fb6f"% (self.request.get('i'))
        response = http.request('GET', uri)
        data = json.loads(response.data)
        
        now = datetime.datetime.now()
        max_temp = max([l['main']['temp_max'] for l in data['list'] if (datetime.datetime.fromtimestamp(l['dt']) - now).total_seconds() < (24 * 60 * 60)])
        min_temp = min([l['main']['temp_min'] for l in data['list'] if (datetime.datetime.fromtimestamp(l['dt']) - now).total_seconds() < (24 * 60 * 60)])
        
        ## Taken from https://temboo.com/processing/display-temperature
        minTemp = 40
        maxTemp = 95
        max_temperature_color = min([255, max([0, int(255 * (max_temp - minTemp) / (maxTemp - minTemp))])])
        min_temperature_color = min([255, max([0, int(255 * (min_temp - minTemp) / (maxTemp - minTemp))])])

        self.response.write("%d,%d" % (min_temperature_color << 16 | (255 - min_temperature_color), max_temperature_color << 16 | (255 - max_temperature_color)))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bart', BartHandler),
    ('/weather', WeatherHandler),
], debug=True)
