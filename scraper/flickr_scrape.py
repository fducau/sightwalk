#!/usr/bin/env python
# @Author: Maria Elena Villaobos Ponte
# @Date:   2016-11-07 10:32:30
# @Last Modified by:   Maria Elena Villalobos Ponte
# @Last Modified time: 2016-12-17 18:43:53
import flickrapi as fk
import socket
from pymongo import MongoClient

# TODO: store these in a config file
# Flickr API config
socket.setdefaulttimeout(5)
api_key = None
api_secret = None
flickr = fk.FlickrAPI(api_key, api_secret, format="json")
hourly_limit = 3600

# MongoClient config
# client = MongoClient("mongodb://localhost:27017/")
client = MongoClient("crunchy6.cims.nyu.edu")
db = client.sightWalk
db_photos = db.photos


class TimeoutException(Exception):
    pass

def handler(signum, frame):
    """Register an handler for the timeout"""
    print "Timeout reached!"
    raise TimeoutException()

class Unbuffered:
   def __init__(self, stream):
       self.stream = stream

   def write(self, data):
       self.stream.write(data)
       self.stream.flush()

   def __getattr__(self, attr):
       return getattr(self.stream, attr)
