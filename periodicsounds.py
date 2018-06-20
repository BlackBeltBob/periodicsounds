import threading
import json
import datetime
import time
import os

from shutil import copyfile
#requires $>sudo pip install playsound..
from playsound import playsound


def readfile(location):
	file = open(location, "r")
	content = file.read()
	return content

def playSource(source):
	debugPrint('Playing '+source.lower())
	try:
		playsound('./' + source.lower());
	except:
		pass



def checkIfWorkingDay():
	d = datetime.datetime.now()
	if d.isoweekday() not in range(1,6):
		debugPrint('Not a workday.')
		return False
	debugPrint('Today is a workday.');
	return True

def checkTimeEquals(time_now, time_str):
	return str(time_now)[:5] == time_str[:5]

def checkWeekDayEquals(time_now, weekday):
	str_wd = time_now.strftime("%A").strip()
	return str_wd.lower() == weekday.lower()

def checkMonthDayEquals(time_now, monthday):
	str_md = str(monthday)
	str_nw = time_now.strftime("%e").strip()
	return str_md == str_nw



def playDailyScheduled(jsonData):
	time_now = datetime.datetime.now().time()
	for item in jsonData:		
		time_json = item["time"]
		if checkTimeEquals(time_now, time_json):
			playSource(item["source"])

def playWeeklyScheduled(jsonData):
	today = datetime.date.today()
	time_now = datetime.datetime.now().time()
	for item in jsonData:		
		time_json = item["time"]
		weekday = item["weekday"]
		source = item["source"]
		if checkTimeEquals(time_now, time_json) and checkWeekDayEquals(today, weekday):
			playSource(source)

def playMonthlyScheduled(jsonData):
	today = datetime.date.today()
	time_now = datetime.datetime.now().time()
	for item in jsonData:		
		time_json = item["time"]
		monthday = item["monthday"]
		source = item["source"]
		if checkTimeEquals(time_now, time_json) and checkMonthDayEquals(today, monthday):
			playSource(source)



def readFileToJSon(location):
	content = readfile(location)
	if (len(content) == 0):
		return
	try:
		jsonData = json.loads(content)
	except:
		debugPrint('JSon file is empty or malformed. Check syntax!')
		jsonData = {}
		pass
	return jsonData	



def findDataFileInFolder(base_location, sounddatafile):
	files_in_base = os.listdir(base_location);
	for file in files_in_base:
		if file[0] == '.':
			continue

		full_location = base_location + '/' + file
		if os.path.isdir(full_location):
			jsonLocation = findDataFileInFolder(full_location, sounddatafile)
			if jsonLocation != False:
				debugPrint('File ' + sounddatafile + ' was found at: '+str(jsonLocation))
				return jsonLocation
			filepath = full_location + '/' + sounddatafile
			if (os.path.isfile(filepath)):
				return full_location
	return False



def copyDataToScript(dataLocation, sounddatafile):
	if dataLocation == False:
		debugPrint('File ' + sounddatafile + ' was not found.')
		return
	debugPrint('Copying ' + dataLocation + '/' + sounddatafile + ' to script.')
	copyfile(dataLocation + '/' + sounddatafile, './'+sounddatafile) # might fail. In that case, will be retried next attempt.

	# also copy all mp3 and wav files.
	files_in_base = os.listdir(dataLocation);
	for file in files_in_base:
		filename = dataLocation + '/' + file
		if os.path.isdir(filename):
			continue
		extension = os.path.splitext(filename)[1]
		if (extension.lower() == '.mp3' or extension.lower() == '.wav'):
			debugPrint('Copying ' + file + ' to script.')
			copyfile(filename, './' + file.lower())



def debugPrint(text):
	return   # uncomment this line to stop printing debug messages.
	print(text)



#Threading to make this repeat every minute.
def checkAndPlay():
	sounddatafile = 'sounddata.json'
	# First, we attempt to find the file on the usb disk.
	jsonLocation = findDataFileInFolder('/media/bob', sounddatafile)
	copyDataToScript(jsonLocation, sounddatafile)

	if checkIfWorkingDay() == False:
		return
	debugPrint("Checking file and playing sounds where needed.")

	time_current = datetime.datetime.now().time()
	jsonData = readFileToJSon('./'+sounddatafile) # reads the copy written next to the script.
	if "daily" in jsonData:
		playDailyScheduled(jsonData["daily"])
	if "weekly" in jsonData:
		playWeeklyScheduled(jsonData["weekly"])
	if "monthly" in jsonData:
		playMonthlyScheduled(jsonData["monthly"])

debugPrint('Starting...')
starttime = time.time()
#Repeat forever:
while(True):
	checkAndPlay()
	time.sleep(60.0 - ((time.time() - starttime) % 60.0))
