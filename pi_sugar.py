#!/usr/bin/env python
import os
import sys
import platform
import http.client
import datetime
import time
from enum import Enum
import re
import logging
from logging.handlers import RotatingFileHandler
import json
from pathlib import Path

from utils import *
from nightscout_reader import NightscoutReader
from dexcom_reader import DexcomReader

debug_mode = False
if (len(sys.argv) > 1 and sys.argv[1] == "debug"):
	debug_mode = True

if (debug_mode):
	from console_display import ConsoleDisplay
else:
	from twoline_display import TwolineDisplay
	
class Reading():
	timestamp = None
	value = 0
	trend = 0



LOG_FILENAME="pi-sugar.log"
folder_name = '.pi-sugar'
config_file = 'config.json'
pi_sugar_path = os.path.join(str(Path.home()), folder_name)
Path(pi_sugar_path).mkdir(exist_ok=True) 
interval_seconds = 300

class PiSugar():

	logger = None
	config = {}
	glucoseDisplay = None
	reader = None
	

	def initialize(self):
		self.__init_logger()
		self.logger.info("Application Start")
		#self.logger.info(platform.python_version())
		if (debug_mode):
			self.glucoseDisplay = ConsoleDisplay()
		else:
			self.glucoseDisplay = TwolineDisplay()
		self.glucoseDisplay.clear()

		
	def __init_logger(self):
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.INFO)

		handler = RotatingFileHandler(os.path.join(pi_sugar_path, LOG_FILENAME), maxBytes=131072, backupCount=10)
		handler.setLevel(logging.INFO)

		formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)

	def get_reader(self):
		if (self.config["data_source"] == "dexcom"):
			self.logger.info('Loading dexcom reader')
			self.reader = DexcomReader(self.logger)
			return self.reader.set_config(self.config)
		elif (self.config["data_source"] == "nightscout"):
			self.logger.info('Loading nightscout reader')




			self.reader = NightscoutReader(self.logger)
			return self.reader.set_config(self.config)
		else:
			self.reader = None
			return False

	def read_config(self):
		try:
			f = open(os.path.join(pi_sugar_path, config_file), "r")
			self.config = json.load(f)
			f.close()
		except:
			self.logger.error("Error reading config file")
			return False

		if 'data_source' not in self.config.keys():
			self.logger.error('Invalid config values')
			self.config.clear()
			return False
		return True


	def run(self):
		shouldExit = False
		login_attempts = 0
		lastReading = None
		validToken = False
		
		ip_show_seconds = 6
		if (debug_mode):
			ip_show_seconds = 2
		self.show_ip(2)
		self.glucoseDisplay.show_centered(0, "Initializing")
		
		while True:
			if (not self.read_config()):
				self.glucoseDisplay.show_centered(0, "Invalid")
				self.glucoseDisplay.show_centered(1, "Acct Info")
				time.sleep(10)
				continue;
			if(self.get_reader()):
				break;

		nextRunTime = now_plus_seconds(0)
		while True:
			time.sleep(4)

			if lastReading is not None:
				readingAgeMins = get_reading_age_minutes(lastReading.timestamp)
				self.glucoseDisplay.update_age(readingAgeMins)

			if (nextRunTime > datetime.datetime.utcnow()):
				continue

			if (not validToken):
				login_attempts += 1
				validToken = self.reader.login()
				if (not validToken):
					if (login_attempts > 3):
						nextRunTime = now_plus_seconds(60)
						self.glucoseDisplay.show_centered(0, "Login Failed")
					else:
						nextRunTime = now_plus_seconds(20)
					continue
			login_attempts = 0

			resp = self.reader.get_latest_gv()
			if 'invalidResponse' in resp.keys():
				nextRunTime = now_plus_seconds(60)
				continue

			#self.logger.info(resp)  todo move to reader
			if 'tokenFailed' in resp.keys():
				validToken = False
				nextRunTime = now_plus_seconds(1)
				continue

			reading = Reading()
			reading.timestamp = resp['timestamp']
			reading.value = resp['value']
			reading.trend = resp['trend']
			
			isNewReading = ((lastReading is None) or (lastReading.timestamp != reading.timestamp))
			readingAgeMins = get_reading_age_minutes(reading.timestamp)
			if (isNewReading):
				self.glucoseDisplay.update_value_time_trend(reading.value, readingAgeMins, reading.trend)
				lastReading = reading
				nextRunTime = reading.timestamp + datetime.timedelta(seconds=(interval_seconds+10))
			else:
				if (readingAgeMins >= 20):
					self.glucoseDisplay.update_value_time_trend(0, readingAgeMins, 0)
					
				if (readingAgeMins >= 10):
					nextRunTime = now_plus_seconds(60)
				elif (readingAgeMins >= 6):
					nextRunTime = now_plus_seconds(30)
				elif (readingAgeMins >= 5):
					nextRunTime = now_plus_seconds(10)
				else:
					# We shouldn't get here.  A non-new reading should be older than 5 minutes
					nextRunTime = lastReading.timestamp + datetime.timedelta(seconds=310)



	def show_ip(self,seconds):
		for x in range(0, seconds):
			ip = get_ip_address('wlan0')
			print(ip)
			self.glucoseDisplay.show_centered(0,ip)
			time.sleep(1)

		

app = PiSugar()
app.initialize()
app.run()


