# Example MCP Websocket application

Subscribe to a Websocket on a Ciena MCP server.

Use this application to parse the response and send it somewhere.

## Setup

```bash
pipenv shell
pipenv install
```

## Usage

NOTE: to make MCP send an alarm, you can acknowldeg/unacknowledge it.

Run this:

```bash
export MCP_SERVER=10.75.1.32
python3 websocket_listener.py
```

Should display something like:

```sh
token from MCP: f580d2ada138ebb4b00e
Opening Connection
subscribing to topic: topics:bp.aeprocessor.v2_0.alarms
Received MCP WS Message: {"status": "ok"}
Send the payload somewhere intersting: {"id": "1004277672264008754", "node-type": "3928", "severity": "MAJOR"}
Send the payload somewhere intersting: {"id": "3042801328102244676", "node-type": "3928", "severity": "MAJOR"}
Send the payload somewhere intersting: {"id": "4937116465260737204", "node-type": "3928", "severity": "INFO"}
```

Customize the parsing by changing the `parse_message` function.

Send it somewhere interesting by changing the `send_it` function.
