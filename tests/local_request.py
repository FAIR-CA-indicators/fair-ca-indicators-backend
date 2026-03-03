import requests
import json
import time

print("TESTING THE SERVER")


def check_hsh_metadata(metadata):


  # metadata that will be used for development
  metadata_test = {
    "link": {
      "external": True,
      "url": "https://doi.org/10.1371/journal.pone.0246819.s001"
    },
    "resource": {
      "chronicDiseases": False,
      "classification": {
        "type": "Dataset"
      },
      "collection": [
        "COVID-19",
        "coverCHILD study platform"
      ],
      "contributors": [
        {
          "affiliations": [
            {
              "address": "Charitéplatz 1, 10117 Berlin",
              "identifiers": [
                {
                  "identifier": "001w7jn25",
                  "scheme": "ROR"
                }
              ],
              "name": "Department of Audiology and Phoniatrics, Charité – Universitätsmedizin Berlin",
              "webpage": "https://www.charite.de/en/"
            }
          ],
          "nameType": "Organisational",
          "organisational": {
            "name": "Department of Audiology and Phoniatrics, Charité – Universitätsmedizin Berlin",
            "type": "Contact"
          }
        }
      ],
      "descriptions": [
        {
          "language": "EN (English)",
          "text": "R-readable data frame. In addition to data for ID, condition, cumulative PM, and SPL, the emission rates for the six size classes (C1-C6), corresponding to >0.3–0.5, >0.5–1.0, >1.0–3.0, >3.0–5.0, >5.0–10.0, and >10.0–25 μm), are given."
        }
      ],
      "identifier": "314",
      "ids": [
        {
          "identifier": "10.1371/journal.pone.0246819",
          "relationType": "A is described by B",
          "scheme": "DOI",
          "typeGeneral": "Journal article"
        }
      ],
      "idsNfdi4health": [
        {
          "identifier": "29a2d0954bec454b8a00756477ea6d3a",
          "relationType": "A is supplement to B"
        },
        {
          "identifier": "559bbd5254324038af85de49903a0b37",
          "relationType": "A is continued by B"
        }
      ],
      "keywords": [
        {
          "code": "http://purl.bioontology.org/ontology/MESH/D000086382",
          "label": "COVID-19 | MESH > D000086382"
        },
        {
          "code": "http://purl.bioontology.org/ontology/MESH/D000293",
          "label": "Adolescent | MESH > D000293"
        },
        {
          "code": "http://snomed.info/id/81059003",
          "label": "Emission (finding) | SNOMED > 81059003"
        }
      ],
      "languages": [
        "EN (English)"
      ],
      "nonStudyDetails": {
        "useRights": {
          "confirmations": {
            "authority": True,
            "irrevocability": True,
            "supportByLicensing": True,
            "terms": True
          },
          "label": "CC BY 4.0 (Creative Commons Attribution 4.0 International)"
        }
      },
      "provenance": {
        "dataSource": "Manually collected"
      },
      "titles": [
        {
          "language": "EN (English)",
          "text": "S1 File. Raw data."
        }
      ]
    },
    "versions": [
      {
        "create_timestamp": "2023-07-27T07:13:03Z",
        "id": 842,
        "last_update_timestamp": "2023-07-27T07:48:12Z",
        "name": "1.0",
        "release_timestamp": "2023-07-27T07:48:12Z",
        "status": "PUBLISHED"
      }
    ]
  }

  if not metadata:
    metadata = metadata_test

  body = {
      'subject_type': 'hsh',  # Make sure subject_type is provided
      'metadata': json.dumps(metadata)
  }


  # Send an HTTP POST request with JSON content
  response = requests.post(url, data=body)

  session_id = response.json()['id']
  status = response.json()['status']

  # Check the response
  if response.status_code == 200:
    print("Request was successful.")
    tasks = response.json()['tasks']
    for values in tasks.values():
      print(values['name'], ":  ", values['status'])
    print('status: ', response.json()['status'])

    count = 0
    while status != 'finished' and count < 2:
      print(count)
      time.sleep(3)
      print("not finished!")
      response_update = requests.get(url + '/' +  session_id, )
      status = response_update.json()['status']
      count += 1



    if(response.json()['status'] != 'finished'):
      tasks = response_update.json()['tasks']
    for values in tasks.values():
      print(values['name'], ":  ", values['status'])

      #response = requests.get(url + '/' +  response.json()['id'], )
      #print(response.json())
  else:
      print("Request failed with status code:", response.status_code)
      print(response.text)


def get_metadata(hsh_id):
  hsh_url = 'https://health-study-hub.de/api/resource/'
  #NCT06079359

  print("HSH ID: ", hsh_id)
  response = requests.get(hsh_url + hsh_id)

  if response.status_code == 200:
    return response.json()
  else:
    return ("Error")


  # Define the URL of the local server
url = 'http://localhost:8000/session'


ids = ['NCT06079359', 'DRKS00010675']
mode = "local"

if mode == "hsh_api":
  for id in ids:
    overall_scores = {}
    md = get_metadata(id)
    check_hsh_metadata(md)
elif mode == "local":
  with open('tests/data/hsh/t3.json', 'r') as file:
    data = json.load(file)

  check_hsh_metadata(data)

  print(json.dumps(data, indent=4))

