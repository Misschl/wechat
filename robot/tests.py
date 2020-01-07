from concurrent.futures import ThreadPoolExecutor
import time
import requests

url = 'http://127.0.0.1:8000/send?app_id=b748ee815e954e06900f64a4f4804e87&app_secret=1c40426230f411eaa70400e070812cea'

data = {'msg_type': 'text', 'puid': '1fee435b', 'text': '666'}

r = requests.post(url, json=data)

print(r.json())
