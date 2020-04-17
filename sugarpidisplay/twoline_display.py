import smbus
from RPLCD.i2c import CharLCD
from .trend import Trend

class TwolineDisplay:
	__lcd = None
	__animIdx = -1
	__animChars = []
	__screenMode = ""
	__port = 1
	__logger = None

	def __init__(self, logger):
		self.__logger = logger
		return None

	def open(self):
		addr = self.__find_device(self.__port)
		if (addr < 1):
			raise Exception
		self.__lcd = CharLCD(i2c_expander='PCF8574', address=addr, port=self.__port,
				  cols=16, rows=2, dotsize=8,
				  #charmap='A02',
				  auto_linebreaks=True,
				  backlight_enabled=True)
		self.__lcd.clear()
		self.__create_custom_chars()
		return True

	def close(self):
		self.__lcd.clear()
		self.__lcd.close()
		self.__lcd = None
		return True

	def __find_device(self,port):
		bus = smbus.SMBus(port) # 1 indicates /dev/i2c-1
		for device in range(128):
			try:
				bus.read_byte(device)
				#print(hex(device))
				return device
			except: # exception if read_byte fails
				pass
		return -1

	def clear(self):
		self.__lcd.clear()
		self.__screenMode = ""

	def show_centered(self,logLevel,line0,line1):
		self.__setScreenModeToText()
		self.__logger.debug("Display: " + (line0 if line0 is not None else "") + " || " + (line1 if line1 is not None else ""))
		if (line0 is not None):
			self.__lcd.cursor_pos = (0, 0)
			self.__lcd.write_string(line0.center(16))
		if (line1 is not None):
			self.__lcd.cursor_pos = (1, 0)
			self.__lcd.write_string(line1.center(16))

	def update(self,updates):
		self.__setScreenModeToEgv()
		if 'age' in updates.keys():
			self.__update_age(updates['age'])
		if 'oldReading' in updates.keys() and updates['oldReading']:
			self.__update_value(None)
			self.__update_trend(None)
			return
		if 'value' in updates.keys():
			self.__update_value(updates['value'])
		if 'trend' in updates.keys():
			self.__update_trend(updates['trend'])

	def __update_value(self,value):
		valStr = "--"
		if (value is not None):
			valStr = str(value)
		#print(valStr + "   " + str(mins))

		valStr = valStr.replace("0","O")
		valStr = valStr.rjust(6)
		self.__lcd.cursor_pos = (0, 0)
		self.__lcd.write_string(valStr)


	def __update_trend(self, trend):
		trendArrow = "  "
		if trend is not None:
			trendArrow = self.__get_trend_chars(trend)
		self.__lcd.cursor_pos = (1, 4)
		self.__lcd.write_string(trendArrow)


	def __update_age(self, mins):
		self.__setScreenModeToEgv()
		ageStr = "now"
		if (mins > 50):
			ageStr = "50+"
		elif (mins > 0):
			ageStr = str(mins) + "m"

		ageStr = ageStr.replace("0","O")
		ageStr = ageStr.rjust(3)

		self.__lcd.cursor_pos = (1, 13)
		self.__lcd.write_string(ageStr)


	def updateAnimation(self):
		self.__setScreenModeToEgv()
		self.__animIdx += 1
		if (self.__animIdx >= len(self.__animChars)):
			self.__animIdx = 0
		char = self.__animChars[self.__animIdx]
		self.__lcd.cursor_pos = (0, 15)
		self.__lcd.write_string(char)

	def __setScreenModeToEgv(self):
		if (not self.__screenMode == "egv"):
			self.__logger.debug("Display mode EGV")
			self.__screenMode = "egv"
			self.__lcd.clear()

	def __setScreenModeToText(self):
		if (not self.__screenMode == "text"):
			self.__logger.debug("Display mode Text")
			self.__screenMode = "text"
			self.__lcd.clear()

	def __get_trend_chars(self,trend):
		if(trend == Trend.NONE):
			return "**"
		if(trend == Trend.DoubleUp):
			return "\x01\x01"
		if(trend == Trend.SingleUp):
			return "\x01 "
		if(trend == Trend.FortyFiveUp):
			return "\x02 "
		if(trend == Trend.Flat):
			return "-\x7e"
		if(trend == Trend.FortyFiveDown):
			return "\x03 "
		if(trend == Trend.SingleDown):
			return "\x04 "
		if(trend == Trend.DoubleDown):
			return "\x04\x04"
		if(trend == Trend.NotComputable):
			return "NC"
		if(trend == Trend.RateOutOfRange):
			return "HI"
		return "??"
		#self.__lcd.write_string('\x02\x02 \x02 \x03 -\x7e \x05 \x06 \x06\x06')

	def __create_custom_chars(self):
		upArrow = (
			 0b00000,
			 0b00100,
			 0b01110,
			 0b10101,
			 0b00100,
			 0b00100,
			 0b00100,
			 0b00100
		)
		self.__lcd.create_char(1, upArrow)

		upSlight = (
			 0b00000,
			 0b00000,
			 0b00111,
			 0b00011,
			 0b00101,
			 0b01000,
			 0b10000,
			 0b00000
		)
		self.__lcd.create_char(2, upSlight)

		dnSlight = (
			 0b00000,
			 0b00000,
			 0b10000,
			 0b01000,
			 0b00101,
			 0b00011,
			 0b00111,
			 0b00000
		)
		self.__lcd.create_char(3, dnSlight)

		dnArrow = (
			 0b00000,
			 0b00100,
			 0b00100,
			 0b00100,
			 0b00100,
			 0b10101,
			 0b01110,
			 0b00100
		)
		self.__lcd.create_char(4, dnArrow)


		self.__animChars = [ '\x05', '\x06', '\x07' ]

		anim1 = (
			 0b00000,
			 0b00000,
			 0b00000,
			 0b00000,
			 0b00000,
			 0b00000,
			 0b00010,
			 0b00000
		)
		self.__lcd.create_char(5, anim1)

		anim2 = (
			 0b00000,
			 0b00000,
			 0b00000,
			 0b00100,
			 0b01010,
			 0b00100,
			 0b00000,
			 0b00000
		)
		self.__lcd.create_char(6, anim2)

		anim3 = (
			 0b01100,
			 0b10010,
			 0b10010,
			 0b01100,
			 0b00000,
			 0b00000,
			 0b00000,
			 0b00000
		)
		self.__lcd.create_char(7, anim3)
