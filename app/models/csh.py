# identifier exists [resource -> resource identifier]

def evaluate(json_data, schema_version):
    if(schema_version == "3.1"):
        current_pos = check_route(json_data, ["resource", "resource_identifier"])

    print(current_pos)


def check_route(json_data, route_keys):
    current_position = json_data

    for key in route_keys:
        if key in current_position:
            current_position = current_position[key]
        else:
            #if a key is missing return false
            return False
    #if the route exists return the value
    return current_position