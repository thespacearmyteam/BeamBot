"""
This module has two functions.
prepCMD prepares the raw websockets data for getResp to return the appropriate response.
This makes it even easier for modding, since you can simply pass the command from the
new code instead of having to figure out how to create the correct packet.
"""

from datetime import datetime
import responses
import callbacks
import os.path
import pickle
import json

initTime = datetime.now().strftime('%H.%M.%S')
config = json.load(open('data/config.json', 'r'))

if os.path.exists('data/bannedUsers{}.p'.format(config['CHANNEL'])):
	bannedUsers = pickle.load(open('data/bannedUsers{}.p'.format(config['CHANNEL']), 'rb'))
else:
	bannedUsers = []
	pickle.dump(bannedUsers, open('data/bannedUsers{}.p'.format(config['CHANNEL']), 'wb'))

def prepCMD(msg, msgLocalID, msgs_acted):

	print ('msg:\t\t',msg)

	user_id = msg['user_id']
	user_name = msg['user_name']
	msg_id = msg['id']

	is_mod = False
	user_roles = msg['user_roles']
	if 'Owner' in user_roles or 'Mod' in user_roles:
		print ('Elevated user!')
		is_mod = True

	response = None					# Have to declare variable as None to avoid UnboundLocalError
	goodbye  = False 				# Have to declare variable as False to avoid UnboundLocalError

	if user_name in bannedUsers:		# Is the user chatbanned?
		session = requests.session()

		login_r = session.post(
			addr + '/api/v1/users/login',
			data=_get_auth_body()
		)

		if login_r.status_code != requests.codes.ok:
			print (login_r.text)
			print ("Not Authenticated!")
			quit()

		del_r = session.delete(addr + '/api/v1/chats/' + str(channel) + '/message/' + msg_id)	# Delete the message

		if del_r.status_code != requests.codes.ok:
			print ('Response:\t\t',del_r.json())
			quit()

		session.close()

	cur_item = ''

	"""
	This loop goes through the message. If there is a link in the message, then it will show up every second
	part of the message.

	When there *is* a link, it won't have any text for the current part of the message, so use the "data" key
	of the current part of the message.
	"""

	for i in range(0, len(msg['message'])):
		if i % 2:		# Every 2 messages
			cur_item += msg['message'][i]['text']
		else:
			cur_item += msg['message'][i]['data']

	for item in msg['message']:	# Iterate through the message

		if len(cur_item) >= 1:	# Just make sure it's an actual message

			if cur_item[0] == '!' and msg_id not in msgs_acted:	# It's a command! Pay attention!

				response, goodbye = getResp(cur_item, user_name, msgLocalID, is_mod)

	return response, goodbye

def getResp(cur_item, user_name=None, msgLocalID=None, is_mod=False):

	# ----------------------------------------------------------
	# Commands
	# ----------------------------------------------------------
	cmd = cur_item[1:].split()
	# Doesn't work yet, working on figuring out none-blocking time tracking
	# if cmd[0] == "throw":			# Throw a ball at another user
	# 	timer = callbacks.Timer(2)
	#
	# 	print (timer.callback())
	#
	# 	response = "Blargh"

	if cmd[0][0:5] == "blame":	# Blame a user
		response = responses.blame(user_name, cur_item, is_mod)

	elif cmd[0] == "commands":		# Get list of commands
		response = responses.cmdList(user_name, cur_item, is_mod)

	elif cmd[0] == "hey":				# Say hey
		response = responses.hey(user_name)

	elif cmd[0] == "ping":				# Ping Pong Command
		response = responses.ping(user_name)

	elif cmd[0] == "dimes" or cmd[0] == "currency":			# Get user balance
		response = responses.dimes(user_name, cur_item, is_mod)

	elif cmd[0] == "give":	# Give dimes to a user
		response = responses.give(user_name, cur_item, is_mod)

	elif cmd[0] == "ban":	# Ban a user from chatting
		response, banUser = responses.ban(user_name, cur_item, is_mod)
		bannedUsers.append(banUser)

		print ("bannedUsers",bannedUsers)

		pickle.dump(bannedUsers, open('data/bannedUsers{}.p'.format(config['CHANNEL']), "wb"))

	elif cmd[0] == "unban":	# Unban a user
		response, uBanUser = responses.unban(user_name, cur_item, is_mod)
		bannedUsers.remove(uBanUser)

		pickle.dump(bannedUsers, open('data/bannedUsers{}.p'.format(config['CHANNEL']), "wb"))

	elif cmd[0] == "quote":	# Get random quote from DB
		response = responses.quote(user_name, cur_item, is_mod)

	elif cmd[0] == "tackle":# Tackle a user!
		response = responses.tackle(user_name, cur_item, is_mod)

	elif cmd[0] == "slap":	# Slap someone
		response = responses.slap(user_name)

	elif cmd[0] == "uptime":# Bot uptime
		response = responses.uptime(user_name, initTime)

	elif cmd[0] == "hug":	# Give hugs!
		response = responses.hug(user_name, cur_item, is_mod)

	elif cmd[0] == "raid":	# Go raid peoples
		response = responses.raid(user_name, cur_item, is_mod)

	elif cmd[0] == "raided":	# You done got raided son!
		response = responses.raided(user_name, cur_item, is_mod)

	elif cmd[0] == "twitch":	# Go raid peoples on Twitch.tv!
		response = responses.twitch(user_name, cur_item, is_mod)

	elif cmd[0] == "whoami":	# Who am I? I'M A GOAT. DUH.
		response = responses.whoami(user_name)

	elif cmd[0] == "command":	# Add command for any users
		response = responses.command(user_name, cur_item, is_mod)

	elif cmd[0] == "command+":	# Add mod-only command
		response = responses.commandMod(user_name, cur_item, is_mod)

	elif cmd[0] == "command-":	# Remove a command
		response = responses.commandRM(user_name, cur_item, is_mod)

	elif cmd[0] == "whitelist":	# Whitelist a user
		if len(cmd) >= 3:	# True means it has something like `add` or `remove`
			if cmd[1] == 'add':
				response = responses.whitelist(user_name, cur_item, is_mod)
			elif cmd[1] == 'remove':
				response = responses.whitelistRM(user_name, cur_item, is_mod)
			else: 	# Not add or remove
				response = None
		else:		# Just get the whitelist
			response = responses.whitelistLS(user_name, cur_item, is_mod)

	elif cmd[0] == "goodbye":	# Turn off the bot correctly

		packet = {
			"type":"method",
			"method":"msg",
			"arguments":['See you later my dear sir, wot wot!'],
			"id":msgLocalID
		}

		return packet, True	# Return the Goodbye message packet &

	else:					# Unknown or custom command
		response = responses.custom(user_name, cur_item, is_mod)

	print ('command:\t',cmd,'\n',
		'response:\t',response,'\n')	# Console logging

	return response, False 		# Return the response to calling statement
