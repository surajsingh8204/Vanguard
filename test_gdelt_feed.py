import requests

url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

r = requests.get(url)

print(r.text)