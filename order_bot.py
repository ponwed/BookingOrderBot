import os
import time
import datetime
import re
import booking_order
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
order_bot_id = None

# Constants
RTM_READ_DELAY = 2
COMMAND = "get"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
BOOKING_ORDER = booking_order.booking_order

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
		if "next booker" in command:
			response = get_booker()

	slack_client.api_call(
		"chat.postMessage",
		channel=channel,
		text=response or default_response
	)

def update_next_booker():
	# Get the last person to book
	last_booking =  open("last_booking")
	last_booker = file.read(last_booking)
	last_booking.close()

	# Get index of last booker and add one to get next booker 
	last_booker_index = BOOKING_ORDER.index(last_booker) # Special case if last booker was last in array, then reset
	if last_booker_index == len(BOOKING_ORDER) - 1:
		new_booker_index = 0
	else:
		new_booker_index = last_booker_index + 1
		
	new_booker = BOOKING_ORDER[new_booker_index]

	# Write the new "last booker" to the last booker file for next week
	last_booking =  open("last_booking", "w")
	last_booking.write(new_booker)
	last_booking.close()
	
def get_booker():
	last_booking =  open("last_booking")
	booker = file.read(last_booking)
	last_booking.close()
	
	return booker;
	
def time_for_new_booker():
	last_write_time = os.path.getmtime("last_booking") # Get time of last modification of file
	current_time = time.time()

	if (current_time - last_write_time) > 604800: # If file was written to more than a week ago it's time for a new booker
		return True
		
	return False


if __name__ == "__main__":
	if slack_client.rtm_connect(with_team_state=False):
		print("Order Bot connected and running!")
		order_bot_id = slack_client.api_call("auth.test")["user_id"]
		while True:
			try:
				command, channel = parse_bot_commands(slack_client.rtm_read())
			except WebSocketConnectionClosedException:
				print("Lost connection to slack, reconnecting...")
				if not slack_client.rtm_connect(with_team_state=False):
					print("Failed to reconnect to to Slack")
					time.sleep(1)
				else:
					print("Reconnected to Slack!")
					
			if command:
				handle_command(command, channel)
			time.sleep(RTM_READ_DELAY)
			
			if time_for_new_booker():
				update_next_booker()
	else:
		print("Order Bot connection failed")
		

	
