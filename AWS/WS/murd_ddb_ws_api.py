import json
from murd_ddb import DDBMurd


murd = DDBMurd()


class Curator:
    def __init__(self, name=""):
        pass


def connect_handler(event):
    """ Handle new connetions to WS"""
    print("Handling connection")
    return {"statusCode": 200}


def disconnect_handler(event):
    """ Handle disconnections from WS"""
    return {"statusCode": 200}


def default_handler(event):
    """ Handle unrecognized routes"""
    return {"statusCode": 200}


def update_handler(event):
    """ /update Endpoint Handler """

    # Check authorization

    # Get new mems from event
    body = json.loads(event['body'])
    mems = json.loads(body['mems'])
    identifier = body['identifier'] if 'identifier' in body else 'Unidentified'

    # Store new mems in memory
    murd.update(mems=mems, identifier=identifier)

    return {"statusCode": 200}


def read_handler(event):
    """ /read Endpoint Handler """
    # Check authorization

    # Get read constraints
    # TODO: Check query params for request
    body = json.loads(event['body'])
    row = body['row']
    col = body['col'] if 'col' in body else None
    greater_than_col = body['greater_than_col'] if 'greater_than_col' in body else None
    less_than_col = body['less_than_col'] if 'less_than_col' in body else None

    read_kwargs = {
        "row": row,
        "col": col,
        "greater_than_col": greater_than_col,
        "less_than_col": less_than_col
    }

    read = murd.read(**read_kwargs)

    return {"statusCode": 200, "read": read}


def delete_handler(event):
    """ /delete Endpoint Handler """
    # Check authorization

    # Get new mems from event
    body = json.loads(event['body'])
    mems = body['mems']
    stubborn_mems = murd.delete(mems)

    return {"statusCode": 200, "stubborn_mems": stubborn_mems}


def serve_subscribers(event):
    print("Serving subscribers")


def lambda_handler(event, lambda_context):
    print("Received Event:\n{}".format(event))

    if 'serve_subscribers' in event:
        serve_subscribers(event)
    elif 'requestContext' in event:
        request_context = event['requestContext']
        if '$connect' == request_context['routeKey']:
            return_value = connect_handler(event)
        elif '$disconnect' == request_context['routeKey']:
            return_value = disconnect_handler(event)
        elif 'update' == request_context['routeKey']:
            return_value = update_handler(event)
        elif 'read' == request_context['routeKey']:
            return_value = read_handler(event)
        elif 'delete' == request_context['routeKey']:
            return_value = delete_handler(event)
        else:
            return_value = default_handler(event)

    return return_value
