from concurrent.futures import ThreadPoolExecutor
import time
import requests
import time
import hashlib


def create_signature(data: list, reverse=False):
    data.sort(reverse=reverse)
    key = ''.join(data)
    return hashlib.sha1(key.encode()).hexdigest()


url = 'http://127.0.0.1:8000/members/c56a9de4'

timestamp = str(int(time.time()))
params = {
    'app_id': 'b748ee815e954e06900f64a4f4804e87',
    'app_secret': '1c40426230f411eaa70400e070812cea',
    'timestamp': timestamp,
    'signature': create_signature(data=[timestamp, '12345'])

}
r = requests.get(url, params=params)
print(r.url)
print(r.text)
