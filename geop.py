import os
import pandas as pd
import numpy as np
import socket, struct, ipaddress
import geoip2.database
import simplekml
from gmplot import gmplot
import argparse
import requests
import json

# charliex/2023

# convert an ip string to a number
def ip2int(ip):
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

# verify if the ip address is valid and not private or reserved as best as we can do for now
def is_valid_public_ipv4(ip):
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        # reject if the ip is private or reserved
        if ip_obj.is_private or ip_obj.is_reserved:
            return False
        return True
    except ipaddress.AddressValueError:
        return False

# lookup ip information using ipinfo.io
def lookup_ip(ip):
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    data = json.loads(response.text)
    if "loc" in data:
        lat, lon = data["loc"].split(",")
        return float(lat), float(lon)
    else:
        return None

# create the argument parser
parser = argparse.ArgumentParser(description='generate a kml file and a heatmap from a list of ip addresses')
parser.add_argument('input_file', type=str, help='the input file containing the list of ip addresses')
parser.add_argument('output_kml', type=str, help='the output kml file')
parser.add_argument('output_heatmap', type=str, help='the output heatmap html file')

# parse the command-line arguments
args = parser.parse_args()

print("ip to geo kml/html map convertor - charliex 2023")

# check if geolite2 database exists
if not os.path.isfile('GeoLite2-City.mmdb'):
    print("error: 'GeoLite2-City.mmdb' file does not exist")
    print("please download the geolite2 database from https://www.maxmind.com")
    print("you may need to create a free account and follow the instructions to download 'GeoLite2-City.mmdb'")
    exit()

# read the list of ips
with open(args.input_file, 'r') as file:
    ip_list = file.read().splitlines()

# load the geoip database
reader = geoip2.database.Reader('GeoLite2-City.mmdb')

# convert the ips to lat/lon
locations = []
for ip in ip_list:
    if is_valid_public_ipv4(ip):
        try:
            location = reader.city(ip).location
            locations.append((location.latitude, location.longitude))
        except geoip2.errors.AddressNotFoundError:
            print(f"ip address {ip} not found in database. trying ipinfo.io...")
            latlon = lookup_ip(ip)
            if latlon is not None:
                locations.append(latlon)
            else:
                print(f"warning: ip address {ip} could not be located by either database")

# create a dataframe from the locations
df = pd.DataFrame(locations, columns=['latitude', 'longitude'])

kml = simplekml.Kml()

# add placemarks for each location
for latitude, longitude in locations:
    kml.newpoint(coords=[(longitude, latitude)])

kml.save(args.output_kml)

# create the heatmap
gmap = gmplot.GoogleMapPlotter(df['latitude'].mean(), df['longitude'].mean(), 5)
gmap.heatmap(df['latitude'], df['longitude'])

# draw the heatmap into an html file
gmap.draw(args.output_heatmap)

reader.close()

print("done")

