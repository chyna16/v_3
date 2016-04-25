# from urllib.request import urlopen
import requests
from requests.auth import HTTPBasicAuth
from json import load 
import json
import codecs

url = 'https://stash.mtvi.com/rest/api/1.0/projects' 
res = requests.get(url, auth=('username', 'password'))

reader = codecs.getreader("utf-8")
# response = requests.open(res)
json_obj = json.loads(res.text)

print (res)
print (json_obj['values'])

# for names in json_obj['values']:
#     print(names['name'])
