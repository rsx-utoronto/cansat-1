# test code to send dummy values over serial

from serial import *
import datetime, time
from random import randint

serialPort = "/dev/ttyUSB1"
baudRate = 57600
ser = Serial(serialPort , baudRate, timeout=0, writeTimeout=0)

# TEAM_ID,MISSION_TIME,ALT_SENSOR,OUTSIDE_TEMP,INSIDE_TEMP,VOLTAGE,FSW_STATE,ACC_X,ACC_Y,ACC_Z

while True:

	team_id = "1171"
	date_time = datetime.datetime.now()
	altitude = randint(0, 1000)
	temp_outside = randint(22, 32)
	temp_inside = randint(22, 32)
	voltage = randint(2, 10)
	state = "ASCENT"
	acc_x = randint(-500, 500)
	acc_y = randint(-500, 500)
	acc_z = randint(-500, 500)		

	ser.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (team_id, date_time, altitude, temp_outside, temp_inside, voltage, state, acc_x, acc_y, acc_z))

	time.sleep(1)
