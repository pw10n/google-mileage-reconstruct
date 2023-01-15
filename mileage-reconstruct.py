#!/usr/bin/env python3
"""
Google Location History Mileage Reconstruction Tool
"""

import argparse
import zipfile
import re
import googlemaps
import json
import logging
import os
import csv
import datetime 

__author__ = "me@prenticew.com"
__version__ = "0.1.0"
__license__ = "MIT"

G_API_KEY_KEY = 'G_API_KEY'

gmaps = None
if G_API_KEY_KEY in os.environ: 
    gmaps = googlemaps.Client(key=os.environ[G_API_KEY_KEY])

def e7tod(e7):
    """converts E7 format to decimal"""
    return "%s.%s"%(str(e7)[:-7],str(e7)[-7:])

def resolveLocation(j):
    coord = (e7tod(j["latitudeE7"]), e7tod(j["longitudeE7"]))
    addr = j["address"] if "address" in j else ""

    if gmaps:
        logging.info("address not found for %s" % str(coord))
        reverse_geocode_result = gmaps.reverse_geocode(coord)
        addr = reverse_geocode_result[0]["formatted_address"]
    
    return coord, addr

def convertDateTime(s):
    try:
        return datetime.datetime.strptime(s,'%Y-%m-%dT%H:%M:%S.%fZ') 
    except ValueError:
        return datetime.datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ')  

def reconstruct(googleTakeoutZipFilename, year):
    """ Main entry point of the app """
    result = []
    totalDistace = 0
    with zipfile.ZipFile(googleTakeoutZipFilename) as datazip:
        p = re.compile('Takeout/Location History/Semantic Location History/%s/.*\.json'%(year))
        selectedNames = [name for name in datazip.namelist() if p.match(name)]
        for name in selectedNames:
            with datazip.open(name) as datafile:
                data = json.load(datafile)
                for segment in data["timelineObjects"]:
                    if "activitySegment" in segment and segment["activitySegment"]["activityType"] in ("IN_PASSENGER_VEHICLE", "IN_VEHICLE"):
                        logging.debug("processing activitySegment")
                        startLocation = resolveLocation(segment["activitySegment"]["startLocation"])
                        endLocation = resolveLocation(segment["activitySegment"]["endLocation"])
                        distance = segment["activitySegment"]["distance"] if "distance" in segment["activitySegment"] else segment["activitySegment"]["simplifiedRawPath"]["distanceMeters"] 
                        startTimestamp = convertDateTime(segment["activitySegment"]["duration"]["startTimestamp"])
                        endTimestamp = convertDateTime(segment["activitySegment"]["duration"]["endTimestamp"])
                        result.append((startTimestamp, endTimestamp, startLocation[0][0], startLocation[0][1], startLocation[1], endLocation[0][0], endLocation[0][1], endLocation[1], distance))
                        totalDistace+=distance
    result.sort(key=lambda x: x[0])
    return result, totalDistace

if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser(
                    prog = 'mileage-reconstruct',
                    description = 'Reconstructs mileage history from Google location history.')

    parser.add_argument('googleTakeoutZipFilename')
    parser.add_argument('year')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    result, totalDistance = reconstruct(args.googleTakeoutZipFilename, args.year)

    with open("%s.csv" % args.year, "w") as stream:
        writer = csv.writer(stream)
        writer.writerows(result)

    print(totalDistance)




