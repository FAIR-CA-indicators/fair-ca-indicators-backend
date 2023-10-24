import requests
import json

print("TESTING THE SERVER")

# Define the URL of the local server
url = 'http://localhost:8000/session'

# Define the data you want to send in the POST request (as a dictionary)
metadata = {
    "k1": "v1",
    "k2": "v2"
}

body = {
    'subject_type': 'csh',  # Make sure subject_type is provided
    'metadata': json.dumps(metadata)
}


# Send an HTTP POST request with JSON content
response = requests.post(url, data=body)

# Check the response
if response.status_code == 200:
    print("Request was successful.")
    print("Response:", response.json())
else:
    print("Request failed with status code:", response.status_code)
    print(response.text)
