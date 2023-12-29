import requests

url = 'https://selfcheckin.sunlightpower.my/license'
api_key = 'mforce'  

headers = {
    'X-API-Key': api_key,
}

response = requests.post(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}, {response.json()}")