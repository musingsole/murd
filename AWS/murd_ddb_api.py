import json
from LambdaPage import LambdaPage
from woodwell_DDB import DDBwoodwell


aww = DDBwoodwell(name="aww")


class Curator:
    def __init__(self, name=""):
        pass


def plant_handler(event):
    """ /plant Endpoint Handler """

    # Check authorization

    # Get new trees from event
    trees = []

    # Store new trees in memory
    aww.plant(trees=trees)


def harvest_handler(event):
    """ /harvest Endpoint Handler """
    # Check authorization

    # Get harvest constraints
    harvest_kwargs = {}

    harvest = aww.harvest(**harvest_kwargs)

    return 200, json.dumps(harvest)


def cut_handler(event):
    """ /cut Endpoint Handler """
    # Check authorization

    # Get trees to cut
    trees = []
    aww.cut(trees)
    
    return 200

def create_lambda_page():
    page = LambdaPage()
    page.add_endpoint("post", "/woodwell", plant_handler, 'application/json')
    page.add_endpoint("post", "/woodwell/plant", plant_handler, 'application/json')
    page.add_endpoint("get", "/woodwell", harvest, 'application/json')
    page.add_endpoint("get", "/woodwell/harvest", harvest, 'application/json')
    page.add_endpoint("post", "/woodwell/cut", cut, 'application/json')
    page.add_endpoint("post", "/woodwell/cut", cut, 'application/json')
    
    return page


def lambda_handler(event, handler):
    page = create_lambda_page()
    print("Received Event:\n{}".format(event))
    return page.handle_request(event)

