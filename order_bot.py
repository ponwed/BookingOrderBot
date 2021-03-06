import os
import time
import datetime
import re
import logging
import booking_order
from slackclient import SlackClient

logging.basicConfig()

slack_client = SlackClient(booking_order.token)
order_bot_id = None

# Constants
RTM_READ_DELAY = 2
COMMAND = "get","register","view","help"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
	for event in slack_events:
		if event["type"] == "message" and not "subtype" in event:
			user_id, message = parse_direct_mention(event["text"])
			if user_id == order_bot_id:
				return message, event["channel"]
	return None, None
	
def parse_direct_mention(message_text):
	matches = re.search(MENTION_REGEX, message_text)
	return (matches.group(1), matches.group(2).strip()) if matches else (None, None)
	
def handle_command(command, channel):
	default_response = "Not sure what you mean :/"
	response = None
	
	if command.startswith(COMMAND):
		if "help" in command:
			response = get_help()
		elif "get next booker" in command:
			response = get_booker()
		elif "register booking" in command:
			set_booking(command)
			response = get_booking()
		elif "view booking":
			response = get_booking()

	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response or default_response
	)

def get_help():
	commands = "Accepted prompts: {}".format(', '.join(COMMAND))
	examples = "\n\nExamples:\nget next booker\nregister booking <BXX> <BYY> (one or many) HH:MM \nview booking"
	return commands + examples
	
def set_booking(command):
	courts = re.findall(r'B\d+', command)
	booked_time = re.findall(r'\d\d:\d\d', command)
	booking = open("data/booking", 'w')
	booking.write("Booked courts: {} Time: {}".format(' '.join(courts), booked_time[0]))
	booking.close()
	
def get_booking():
	booking =  open("data/booking")
	booked = file.read(booking)
	booking.close()
	
	return booked;
	
def get_booker():
	last_booking =  open("data/last_booking")
	booker = file.read(last_booking)
	last_booking.close()
	
	return booker

if __name__ == "__main__":
	if slack_client.rtm_connect(with_team_state=False):
		print("Order Bot connected and running!")
		order_bot_id = slack_client.api_call("auth.test")["user_id"]
		while True:
			try:
				command, channel = parse_bot_commands(slack_client.rtm_read())
			except:
				print("Lost connection to slack, reconnecting...")
				if not slack_client.rtm_connect(with_team_state=False):
					print("Failed to reconnect to to Slack")
					time.sleep(1)
				else:
					print("Reconnected to Slack!")
					
			if command:
				handle_command(command, channel)
			time.sleep(RTM_READ_DELAY)
	else:
		print("Order Bot connection failed")
		

	
