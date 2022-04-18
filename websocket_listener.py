import _thread
import json
import ssl
import time
import os

import websocket
import requests
import json


# ************* DEVELOPER NOTE **************************
# * Depending on how you're using this sample code, you may use a MCP ip or a CEC External API Link
# * For CEC users:
# *   - Open your lab info dialog page
# *   - Click the "External API Access" button
# *   - Copy the "External API" link (it should end with "&path=")
# *   - Paste the value in quotes to set the "HOST" constant in this file
# *   - This link will only work for the duration of your lab, you must repeat this process if you create a new lab
# *
# * For MCP Standalone Users:
# *   - Copy the direct FQDN / IP address of MCP (for example: "https://192.168.1.101")
# *   - Paste the value in quotes to set the "HOST" constant in this file
# *
# ************** DEVELOPER NOTE **************************


"""
Connection info for MCP
Username and password come from the user's personal username and password.
Admin users will have more functionality than non-admin users
"""
HOST = os.environ.get("MCP_SERVER")
USERNAME = "admin"
PASSWORD = "adminpw"


def authorize_with_MCP(host, username, password):

    path = "/tron/api/v1/tokens"

    # build the URL String
    url = f"https://{host}{path}"

    auth_payload = f"username={username}&password={password}&tenant=master"
    auth_headers = {
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
    }

    # TODO Do not use "verify=False" for production applications. Always modify to fit your HTTP certificate model
    response = requests.post(url, data=auth_payload, headers=auth_headers, verify=False)
    data = response.json()
    print(f"token from MCP: {data['token']}")

    return data["token"]


def parse_message(body):
    result = {}
    if ('value' in body):
        value = json.loads(body['value'])
        # print(f"value: {value}")
        alarm = value['event']['alarm']
        # print(f"alarm: {json.dumps(alarm)}")
        result['id'] = alarm['data']['id']
        result['node-type'] = alarm['data']['attributes']['node-type']
        result['severity'] = alarm['data']['attributes']['condition-severity']
    return result


def forward_it(payload):
    print(f"Send the payload somewhere intersting: {json.dumps(payload)}")


def on_ws_message(ws, message):
    """
    MCP Websocket on_message handler. Called when websocket server emits a message. Prints message and returns
    :param ws: Websocket instance
    :param message: Message sent from websocket
    :return: None
    """
    json_message = json.loads(message)
    if ('body' in json_message['payload']):
        parsed = parse_message(json_message['payload']['body'])
        forward_it(parsed)
    else:
        print(f"Received MCP WS Message: {json.dumps(json_message['payload'])}")


def on_ws_error(ws, error):
    """
    MCP Websocket on_error handler. Called when websocket server emits an error. Prints Error and returns
    :param ws: Websocket instance
    :param error: error sent from websocket
    :return: None
    """
    print(f"Received MCP WS Error Message: {error}")


def on_close(ws, close_status_code, close_msg):
    """
    MCP Websocket on_close handler. Called when websocket connection is terminated (either by the server or the client). Prints disconnection and returns
    :param ws: Websocket instance
    :return: None
    """
    print("MCP Websocket connection closed")


def on_ping(wsapp, message):
    print("Got a ping! A pong reply has already been automatically sent.")


def on_pong(wsapp, message):
    print("Got a pong! No need to respond")


def on_ws_open(ws):
    """
    MCP Websocket on_open handler. Called when the websocket connection is established.
    Subscribes to the alarms topic and begins sending heartbeats to the server to keep the connection alive.
    :param ws: Websocket instance
    :return: None
    """
    print(f"Opening Connection")
    alarms_topic = "topics:bp.aeprocessor.v2_0.alarms"
    print(f"subscribing to topic: {alarms_topic}")
    register_to_topic(ws, alarms_topic)

    def run(*args):
        while True:
            time.sleep(1)

    _thread.start_new_thread(run, ())


def register_to_topic(ws, topic):
    """
    Register to a topic offered by MCP. Once registered topic-based messages will begin to be received.
    Messages will continue until disconnection.
    :param ws: Websocket instance
    :param topic: The topic name
    :return: None
    """
    registration_body = {"topic": topic, "ref": 0, "event": "phx_join", "payload": {}}
    ws.send(json.dumps(registration_body))


if __name__ == "__main__":
    token = authorize_with_MCP(HOST, USERNAME, PASSWORD)
    websocket_endpoint = f"wss://{HOST}/kafkacomet/socket/websocket"

    ws = websocket.WebSocketApp(
        websocket_endpoint,
        on_message=on_ws_message,
        on_error=on_ws_error,
        on_close=on_close,
        on_open=on_ws_open,
        header={"Authorization": f"Bearer {token}"},
    )
    # ws.on_open = on_ws_open
    # TODO Do not use disable certificate verification for production applications.
    # Always modify to fit your HTTP certificate model
    ws.run_forever(
        ping_interval=25,
        sslopt={"cert_reqs": ssl.CERT_NONE},
        ping_timeout=10,
        ping_payload="I love you MCP",
    )
    print("Websocket opened, messages will be received shortly....")
