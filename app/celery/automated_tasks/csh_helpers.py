import json

def check_route(metadata, route_keys):
    current_position = json.loads(metadata)
    for key in route_keys:
        if key in current_position:
            current_position = current_position[key]
        else:
            print("the key {} form the route{} is not in the dict".format(key, route_keys), )
            #if a key is missing return false
            return False
    #if the route exists return the value
    return current_position
