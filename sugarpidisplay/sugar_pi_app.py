#!/usr/bin/env python3
import os
import sys
import platform
import signal
import threading
import http.client
import datetime
import time
from enum import Enum

import logging
from logging.handlers import RotatingFileHandler
import json
from pathlib import Path

from .utils import *
from .config_utils import *
from .nightscout_reader import NightscoutReader
from .dexcom_reader import DexcomReader

class State(Enum):
	GetWifi = 1
	ShowWifi = 2
	LoadConfig = 3
	FirstLogin = 4
	ReLogin = 5
	ReadValues = 6


class SugarPiApp():
	exit_event_handler = None
	LOG_FILENAME="sugarpidisplay.log"
	folder_name = '.sugarpidisplay'
	config_file = 'config.json'
	pi_sugar_path = os.path.join(str(Path.home()), folder_name)
	interval_seconds = 300
	ip_show_seconds = 6
	ip_show_seconds_pc_mode = 2
	__args = {'debug_mode': False, 'pc_mode': False }

	logger = None
	config = {}
	glucoseDisplay = None
	reader = None
	LastReading = None

	def config_server_worker(self):
		from .sugarpiconfig import app
		HOST = '0.0.0.0'
		PORT = 8080
		app.run(HOST, PORT)

	def start_config_server(self):
		thread = threading.Thread(target=self.config_server_worker, daemon=True)
		thread.start()

	def initialize(self):
		self.exit_event_handler = ExitEventHandler()
		
		self.__parse_args()

		Path(self.pi_sugar_path).mkdir(exist_ok=True) 
		
		self.__init_logger()
		self.logger.info("Application Start")
		
		self.start_config_server()
		
		#self.logger.info(platform.python_version())
		if (self.__args['pc_mode']):
			from .console_display import ConsoleDisplay
			self.glucoseDisplay = ConsoleDisplay(self.logger)
		else:
			from .twoline_display import TwolineDisplay
			self.glucoseDisplay = TwolineDisplay(self.logger)
		self.glucoseDisplay.open()
		self.glucoseDisplay.clear()

	def __parse_args(self):
		if (len(sys.argv) > 1 and sys.argv[1] == "debug"):
			self.__args['debug_mode'] = True

		if (len(sys.argv) > 1 and sys.argv[1] == "pc"):
			self.__args['pc_mode'] = True

		
	def __init_logger(self):
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.INFO)

		handler = RotatingFileHandler(os.path.join(self.pi_sugar_path, self.LOG_FILENAME), maxBytes=131072, backupCount=10)
		handler.setLevel(logging.INFO)
		if (self.__args['debug_mode']):
			self.logger.setLevel(logging.DEBUG)
			handler.setLevel(logging.DEBUG)
			
		formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)

	def __get_reader(self):
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

	def __read_config(self):
		self.config.update(loadConfigDefaults())
		try:
			f = open(os.path.join(self.pi_sugar_path, self.config_file), "r")
			configFromFile = json.load(f)
			f.close()
		except:
			self.logger.error("Error reading config file")
			return False
		self.config.update(configFromFile)
		if 'data_source' not in self.config:
			self.logger.error('Invalid config values')
			self.config.clear()
			return False

		self.logger.info("Loaded config")
		return True

	
	class StateManager:
		__NextRunTime = None
		__RunUntilTime = None
		__stateChangedFlag = False
		CurrentState = None
		PreviousState = None
		StateFunc = None		
		IsNewState = False

		def setNextState(self,state):
			self.PreviousState = self.CurrentState
			self.CurrentState = state
			self.__stateChangedFlag = True
			self.setNextRunDelaySeconds(0)
	
		def preRun(self):
			self.IsNewState = False
			if(self.__stateChangedFlag):
				self.IsNewState = True
				self.__stateChangedFlag = False

		def setNextRunDelaySeconds(self,seconds):
			self.__NextRunTime = now_plus_seconds(seconds)

		def setNextRunTimeTimestamp(self,time):
			self.__NextRunTime = time

		def setNextRunTimeTimestampPlusSeconds(self,timestamp,seconds):
			self.__NextRunTime = timestamp + datetime.timedelta(seconds=(seconds+10))

		def isNextRunTime(self):
			return (self.__NextRunTime <= datetime.datetime.utcnow())

		def setRunDuration(self,seconds):
			self.__RunUntilTime = now_plus_seconds(seconds)

		def isRunDurationOver(self):
			return (self.__RunUntilTime <= datetime.datetime.utcnow())

	
	def run(self):
		ctx = SugarPiApp.StateManager()
		ctx.setNextState(State.GetWifi)
		ctx.setNextRunDelaySeconds(0)
		
		self.glucoseDisplay.show_centered("Initializing", "")
		
		while (not self.exit_event_handler.exit_now):
			if (ctx.CurrentState == State.ReadValues or ctx.CurrentState == State.ReLogin):
				self.__updateTickers()
			if (ctx.isNextRunTime()):
				stateFunc = self.__getStateFunction(ctx)
				ctx.preRun()
				stateFunc(ctx)

			# TODO - Only sleep if delay requires it
			time.sleep(2)							
					
		print("Exiting SugarPiDisplay")
		self.glucoseDisplay.close()
	
	def __getStateFunction(self,ctx):
		if (ctx.CurrentState == State.GetWifi):
			stateFunc = self.__getWifi
		elif (ctx.CurrentState == State.ShowWifi):
			stateFunc = self.__showWifi
		elif (ctx.CurrentState == State.LoadConfig):
			stateFunc = self.__runLoadConfig
		elif (ctx.CurrentState == State.FirstLogin):
			stateFunc = self.__runFirstLogin
		elif (ctx.CurrentState == State.ReLogin):
			stateFunc = self.__runReLogin
		elif (ctx.CurrentState == State.ReadValues):
			stateFunc = self.__runReader
		return stateFunc
		
	def __updateTickers(self):
		if self.LastReading is not None:
			readingAgeMins = get_reading_age_minutes(self.LastReading.timestamp)
			self.glucoseDisplay.update({'age': readingAgeMins})

		if (self.config['use_animation']):
			self.glucoseDisplay.updateAnimation()

	def __getWifi(self,ctx):
		self.glucoseDisplay.show_centered("Waiting", "Wifi")
		ip = get_ip_address('wlan0')
		if (ip == ""):
			ctx.setNextRunDelaySeconds(1)
		else:
			ctx.setNextState(State.ShowWifi)
			
	def __showWifi(self,ctx):
		if (ctx.IsNewState):
			ip = get_ip_address('wlan0')
			self.logger.info("Wifi IP: " + ip)
			self.glucoseDisplay.show_centered(ip, "")
			seconds = self.ip_show_seconds_pc_mode if self.__args['pc_mode'] else self.ip_show_seconds
			ctx.setRunDuration(seconds)
			return
		if (ctx.isRunDurationOver()):
			ctx.setNextState(State.LoadConfig)

	def __runLoadConfig(self,ctx):
		self.glucoseDisplay.show_centered("Loading", "Config")
		if (not self.__read_config() or not self.__get_reader()):
			self.glucoseDisplay.show_centered("Invalid Config", "Will Retry")
			ctx.setNextRunDelaySeconds(5)
			return
		ctx.setNextState(State.FirstLogin)

	def __runFirstLogin(self,ctx):
		self.glucoseDisplay.show_centered("Attempting", "Login")
		if (not self.reader.login()):
			ctx.setNextRunDelaySeconds(180)
			self.glucoseDisplay.show_centered("Login Failed", "Will Retry")
			return
		self.logger.info("Successful login")
		ctx.setNextState(State.ReadValues)

	def __runReLogin(self,ctx):
		if (not self.reader.login()):
			ctx.setNextState(State.FirstLogin)
			self.glucoseDisplay.show_centered("Re-login Failed", "Will Retry")
			return
		self.logger.info("Successful login refresh")
		ctx.setNextState(State.ReadValues)

	def __runReader(self,ctx):
		if (ctx.IsNewState and ctx.PreviousState == State.FirstLogin):
			self.glucoseDisplay.update({'oldreading':True})

		resp = self.reader.get_latest_gv()
		if 'errorMsg' in resp.keys():
			ctx.setNextRunDelaySeconds(120)
			return
		if 'tokenFailed' in resp.keys():
			ctx.setNextState(State.ReLogin)
			return

		reading = resp['reading']
		readingAgeMins = get_reading_age_minutes(reading.timestamp)
		self.glucoseDisplay.update({'age':readingAgeMins})
		if (readingAgeMins >= 20):
			self.glucoseDisplay.update({'oldreading':True})
		else:
			self.glucoseDisplay.update({'value':reading.value, 'trend':reading.trend})

		isNewReading = ((self.LastReading is None) or (self.LastReading.timestamp != reading.timestamp))
		self.LastReading = reading
		if (isNewReading):
			ctx.setNextRunTimeTimestampPlusSeconds(reading.timestamp, self.interval_seconds+10)
		else:
			ctx.setNextRunDelaySeconds(self.__getReadingWaitBackoff(readingAgeMins))

	def __getReadingWaitBackoff(self,readingAgeMins):
		if (readingAgeMins >= 10):
			return 60
		elif (readingAgeMins >= 6):
			return 30
		elif (readingAgeMins >= 5):
			return 15
		else:
			# We shouldn't get here.  A non-new reading should be older than 5 minutes
			return 60


class ExitEventHandler:
	exit_now = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.handle_exit_signal)
		signal.signal(signal.SIGTERM, self.handle_exit_signal)

	def handle_exit_signal(self,signum, frame):
		self.exit_now = True



