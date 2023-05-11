# ip_to_geo_kml_html
take an ipv4 list from a text file, one per line and output an html using google maps to view it, and a kml

requires GeoLite2-City.mmdb from maxmind, if IP isn't found in mmdb it will try to find it in ipinfo.io

inpinfo might rate limit you if a lot of requests are sent, so try to have a complete mmdb

install

pip install pandas numpy geoip2 simplekml gmplot requests

run

python3 geop.py ip_list.txt output.kml output.html

code checks for local ip's and outputs a list that can't be geo-ip'd succesfully

todo

add a list of unwanted ip addresses
