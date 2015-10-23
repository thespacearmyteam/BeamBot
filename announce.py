import messages
from datetime import datetime
import json
import asyncio
import os

global websocket

announce_users = {}

def registerWebsocket(chat_socket):
    global websocket

    websocket = chat_socket

def _updateConfig():
    if os.path.exists('data/config.json'):
        config = json.load(open('data/config.json', 'r'))

    return config

@asyncio.coroutine
def userJoin(result, result_user):
    global websocket

    cur_time = int(datetime.now().strftime("%M"))

    print ('User joined:\t', result_user,
            '-', result['data']['id'],
            end='\n\n')

    config = _updateConfig()

    if result['data']['id'] != 25873:		# PyBot ID
        if config['announce_enter'] == True and result_user != None:\

            if result_user not in announce_users:
                # Only if it's beyond 3 minutes of the original enter/leave send the messages
                response = "Welcome " + result_user + " to the stream!"
                yield from messages.sendMsg(websocket, response)

                announce_users[result_user] = cur_time
            else:
                if cur_time - int(announce_users[result_user]) > 3:
                    response = "Welcome " + result_user + " to the stream!"
                    yield from messages.sendMsg(websocket, response)

                    announce_users[result_user] = cur_time

@asyncio.coroutine
def userLeave(result, result_user):
    global websocket

    cur_time = int(datetime.now().strftime("%M"))

    print ('User left:\t', result_user,
            '-', result['data']['id'],
            end='\n\n')

    config = _updateConfig()

    if result['data']['id'] != 25873:		# PyBot ID
        if config['announce_leave'] == True and result_user != None:

            if result_user not in announce_users:
                response = "See you later " + result_user + "!"

                yield from messages.sendMsg(websocket, response)

                announce_users[result_user] = cur_time
