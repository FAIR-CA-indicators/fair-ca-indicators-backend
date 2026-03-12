import json
import requests

def check_route(metadata, route_keys):
    current_position = json.loads(metadata)
    for key in route_keys:
        print(key + "-->" + str(type(current_position)))
        if key in current_position:
            current_position = current_position[key]
        elif isinstance(current_position, list):
            print("LIST FOUND!!!!!")
            if key in current_position[0]:
                print("INSIDE!!!!!!!!")
                current_position = current_position[0][key]
        else:
            print("the key {} form the route{} is not in the dict".format(key, route_keys), )
            #if a key is missing return false
            return False
    #if the route exists return the value
    return current_position

def check_list(data, checks):
    for attr in checks:
        if not check_route(data, attr):
            print("check failed for: ", attr)
            return False
    return True

def is_url_reachable(url):
    try:
        response = requests.head(url, timeout=5)  # Send a HEAD request to check if the server is reachable
        return response.status_code < 400  # If the status code is less than 400, the URL is reachable
    except requests.RequestException:
        return False  # If any exception occurs (e.g., timeout), consider the URL unreachable

