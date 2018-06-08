# -*- coding: utf-8 -*-

"""Main module."""
import websockets


class Route:
    pass


class Session:
    pass


"""
router:
broker (pubsub)
dealer (rpc)
"""

"""
realm:
route message
"""

"""
roles:
rpc:
 callee, caller, dealer
pubsub:
 subscriber, publisher, broker
"""

"""
ids:
sessions
publications
subscriptions
registrations
requests
"""

"""
transports:
websocket
session lifetime
protocol errors
"""

"""
messages:
MessageType
uri (string 5.1.1)
id (integer 5.1.2)

session lifecycle:
 - hello
 - welcome
 - abort
 - goodbye
 - error
 
publish and subscribe:
 - publish
 - published
 - subscribe
 - subscribed
 - unsubscribe
 - unsubscribed
 - event

routed remote procedure calls
 - call
 - result
 - register
 - registered
 - unregister
 - unregistered
 - invocation
 - yield
"""

"""
sessions:
establishment
 1. client hello
 2. client role and feature announcement
 3. router welcome
 4. router role and feature announcement
 
abort
session closing

"""

"""
websocket
message
connection
applications
wamp
publish
subscribe
rpc
router
components
receive
topic
distribute
event
callee
procedure
callers
invoke
result
forward
broker
dealer
client
connections
transport
session
realm
basic profile
advanced profile


"""


async def handler(websocket, path):
    name = await websocket.recv()
    print("< {}".format(name))

    greeting = "Hello {}!".format(name)

    await websocket.send(greeting)
    print("> {}".format(greeting))


start_router = websockets.serve(handler, 'localhost', 9001)
