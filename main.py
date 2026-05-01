import requests
import pprint
from environs import Env

env = Env()
env.read_env()
token = env.str("DEVMAN_API_TOKEN")


url = 'https://dvmn.org/api/user_reviews/'
headers = {
    "Authorization": f"Token {token}"
}

response = requests.get(url, headers=headers)
pprint.pprint(response.json())