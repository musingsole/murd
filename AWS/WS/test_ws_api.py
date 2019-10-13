import json
from websocket import create_connection
from IPython import embed

url = "wss://6zlsr9hpq3.execute-api.us-east-1.amazonaws.com/prod"
ws = create_connection(url)

read_request = {
    "action": "read",
    "route": "read",
    "row": "varanus"
}
ws.send(json.dumps(read_request).encode("utf-8"))
data = ws.recv()
print(data)

print("Starting console\n")
embed()
