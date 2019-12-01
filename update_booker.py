import booking_order

BOOKING_ORDER = booking_order.booking_order

# Get the last person to book
last_booking =  open("/home/pi/bin/order_bot/data/last_booking")
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
last_booking =  open("/home/pi/bin/order_bot/data/last_booking", "w")
last_booking.write(new_booker)
last_booking.close()
