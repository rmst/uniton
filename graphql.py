import requests
import json
from xbrain import xb


# def t():
import requests
import json
import pyperclip
from time import sleep

for i in range(50):
  print("R", i)
  r = requests.post('https://github.com/login/device/code', json=dict(client_id="8b9263c9919eea0291f4", scope='read:user'), headers=dict(Accept='application/json'))
  if r.status_code != 200:
    raise Exception(f"Query failed to run with a {r.status_code}.")
  d = r.json()
  print(d["user_code"])
  pyperclip.copy(d["user_code"])
  # input()

  while 1:
    sleep(5)
    r2 = requests.post("https://github.com/login/oauth/access_token", json={"client_id": "8b9263c9919eea0291f4", "grant_type": "urn:ietf:params:oauth:grant-type:device_code", "device_code": d["device_code"]}, headers=dict(Accept='application/json'))
    if r2.status_code != 200:
      raise Exception(f"Query failed to run with a {r.status_code}.")

    d2 = r2.json()
    if "access_token" in d2:
      print(d2["access_token"])
      break

    print('retry')






endpoint = f"https://api.github.com/graphql"
headers = {"Authorization": f"Bearer {xb.github.rmst.empty_token}"}

query = """query{
  viewer {
    sponsorshipsAsSponsor(first: 1) {
      nodes {
        tier {
          monthlyPriceInCents
          name
          description
          id
        }
      }
    }
  }
}"""

r = requests.post(endpoint, json={"query": query}, headers=headers)
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))

else:
    raise Exception(f"Query failed to run with a {r.status_code}.")