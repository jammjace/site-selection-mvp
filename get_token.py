# template to get token from onemap API - run this once and copy the token to .env file as ONEMAP_API_TOKEN

# import requests

# url = "https://www.onemap.gov.sg/api/auth/post/getToken"

# payload = {
#     "email": "",
#     "password": ""
# }

# response = requests.post(url, json=payload, timeout=30)
# response.raise_for_status()

# data = response.json()
# print(data)