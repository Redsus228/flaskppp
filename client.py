import requests
from config import BASE_URL
r = requests.get(f'{BASE_URL}/')
print(r.status_code)
print(r.text)