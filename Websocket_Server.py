import websockets
import json
import logging
import asyncio
import os

logging.basicConfig()

PORT = int(os.environ.get('PORT', 5000))
# data model
STATE = {"id": 0, "message": "", "author": "", "path": ""}
# dictionary of messages
STATELIST = {"messages": []}

# set of user connections, gives us the number unique connections connected to the server
USERS = set()

#function to send message back to client
def state_event():
    #return json message
    return json.dumps({"type": "state", **STATE})

#to be ignored, used for future testing
#async def notify_state():
 #   if USERS:
  ##     await asyncio.wait([user.send(message) for user in USERS])

#register connection
async def register(websocket):
    USERS.add(websocket)
    print(f'{len(USERS)} have connected!')

#disconnect connection
async def unregister(websocket):
    USERS.remove(websocket)

#this is the main server login
async def getMessage(websocket, path):
    #connect client to server (websocket = connection)
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            # get the message data from client
            data = json.loads(message)
            STATE["id"] = data["id"]
            STATE["message"] = data["message"]
            STATE["author"] = data["author"]
            STATE["path"] = data["path"]
            STATELIST["messages"].append(data)
            #send message back to all the connected user
            if USERS:
                message = state_event()
                print("message:" + message)
                for user in USERS:
                    print(path)
                    # dont send the message back to client that sent the message
                    if user != websocket:
                        await user.send(message)
    finally:
        await unregister(websocket)

#setup
start_server = websockets.serve(getMessage, "0.0.0.0", PORT)
print(start_server)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
