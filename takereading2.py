#!/usr/bin/python

#Uses: python 2.7.9
# This script takes readings from connected temperature and humidity sensors.
# The readings are added to a queue and another thread reads the queue to upload the readings to the database.

import sys
import Adafruit_DHT
import Queue
import thread
import datetime
import time
import json
import urllib2
import pytz

#type of sensor that we are working with
sensor_type = Adafruit_DHT.AM2302

#what sensors are connected to which pins, these labels determine which sensor_description is sent
pins_to_read = { 4:'main_area', 24:'wardrobe', 23:'outside'}
unit_description = 'camper'

#setup queue
q = Queue.Queue()

#This function is responsible for getting readings from the sensor specified in (pin) and adding them to the queue
def collector(pin):
        while True:
                number_of_readings_to_take = 5
                readings = [ None ] * number_of_readings_to_take
                #make reading
                for i in range(number_of_readings_to_take):
                        humidity, temperature = Adafruit_DHT.read_retry(sensor_type, pin)
                        timestamp = datetime.datetime.now(pytz.timezone("Pacific/Auckland"))  #adjust to NZT
                        timestamp = datetime.datetime(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second, 0)  #truncate microseconds
                        readings[i] = {'h':humidity, 't':temperature, 'time':timestamp}

                #sort list of readings by temperature
                readings.sort(key=lambda x: x['t'])
                reading_to_submit = {'s_key':pin, 'temp': readings[2]['t'], 'humid':readings[2]['h'], 'time':readings[2]['time'].isoformat()} #take middle reading of sorted list.
                #print ("{s_key:",pin," temp:", readings[2]['t']," humid:",readings[2]['h']," time:", readings[2]['time'].isoformat(),"}")

                q.put(reading_to_submit)
                time.sleep(295)  #delay approx 5 mins

def upload(item):
        #setup request
        #req = urllib2.Request('http://localhost:8010/temp-log-168303/us-central1/index')
        req = urllib2.Request('https://us-central1-temp-log-168303.cloudfunctions.net/index')
        req.add_header('Content-Type', 'application/json')

        #translate item object to sendable format
        data = { 'secret':1,
                'unit_desc': unit_description,
                'sensor_desc': pins_to_read[item['s_key']],
                'temperature': float('%.3f'%item['temp']),
                'humidity': float('%.3f'%item['humid']),
                'timestamp': item['time']
                }
        #print 'Uploading item: ' + json.dumps(data, separators=(',',':'))
        response = urllib2.urlopen(req, json.dumps(data, separators=(',',':')))

#start collector(s) one for each sensor
for k in pins_to_read:
        thread.start_new_thread(collector, (k,))

#start sender/uploader
while True:
        try:
                item = q.get(False)
                thread.start_new_thread(upload, (item,))
        except Queue.Empty:
                pass
                #print "Nothing in queue."
        time.sleep(4)