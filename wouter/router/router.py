# -*- coding: utf-8 -*-

"""Main module."""
import asyncio
from typing import Set, Any

import websockets
from wouter.router import session



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


sessions = set()  # type: Set[session.Session]
connections = set()   # type: Set[websockets.WebSocketServerProtocol]


async def consumer_handler(websocket, path):
    """Await message from connected websocket"""
    session_ = session.Session(websocket)
    sessions.add(session_)

    while True:
        message = await websocket.recv()
        print('consumed message ' + str(message))


async def connection_handler(websocket, path):
    # Register.
    connections.add(websocket)
    try:
        await consumer_handler(websocket, path)
    finally:
        # Unregister.
        connections.remove(websocket)


start_router = websockets.serve(connection_handler, 'localhost', 9001)
