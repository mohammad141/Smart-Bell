from pymongo import MongoClient
import RPi.GPIO as GPIO
import pytz
from datetime import datetime
import time
from bson.objectid import ObjectId
import save
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)

mongo_db = MongoClient('localhost',27017)
db_log = mongo_db.smartbell.logs

LOCAL_TZ = pytz.timezone('Europe/Helsinki')

'''
This function is to blink led when checking a permission to access
'''

def led():
	GPIO.output(27,True)
	time.sleep(2)
	GPIO.output(27,False)

'''
This function is to check permission of the visitor and save entrance log, if he or she has permission to access.
First, we check access permission using visitor's id. (access value is 'true' or 'false')
If the visitor doesn't have permission to access, we would close the door and led blinks 5 times.
If the visitor has the permission, we would open the door and save the log which is about firstname, lastname and time, and led blinks once.
'''

def save_log(firstname, lastname, frame):
	
	log_time = datetime.now(pytz.utc).astimezone(LOCAL_TZ).strftime('%Y-%m-%d %H:%M:%S')
	path = 'log/' + str(log_time)
	save.make_directory(path)
	photo_path = save.save_photo(path, '/img0.jpg', frame)
	
	# Save the log
	db_log.insert_one({"firstname":firstname, "lastname":lastname, "time":log_time, "photopath": photo_path})

def permission_check(__id, frame):
	# Check permission to access 
	db_visitors = mongo_db.smartbell.visitors
	try:
		valid = db_visitors.find_one({"_id": ObjectId(__id[0])})
	except EOFError:
		return 0
	
	save_log(valid['firstname'], valid['lastname'], frame)
	
	# If permission to access is true,
	if valid['access']:
		print("Available face, open")
		led()
		
	else:
		print("No permission, closed")
		for n in range(5):
			led()
