from RPi import GPIO
import smbus
#from RPLCD.gpio import CharLCD
from RPLCD.i2c import CharLCD


class TwolineDisplay:

	__lcd = None

	def __init__(self):

		#	lcd = CharLCD(pin_rs=36, pin_rw=38, pin_e=40, pins_data=[31, 33, 35, 37],
		#				  numbering_mode=GPIO.BOARD,
		#				  cols=16, rows=2, 
		#				  dotsize=8,
		#				  charmap='A02',
		#				  auto_linebreaks=True)
		
		port = 1
		addr = self.find_device(port)
		if (addr < 1):
			raise exception
		self.__lcd = CharLCD(i2c_expander='PCF8574', address=addr, port=port,
				  cols=16, rows=2, dotsize=8,
				  #charmap='A02',
				  auto_linebreaks=True,
				  backlight_enabled=True)
		self.__lcd.clear()

		self.__create_custom_chars()	
		return None


	def find_device(self,port):

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
		
	def show_centered(self,line,text):
		print(text)
		self.__lcd.cursor_pos = (line, 0)
		self.__lcd.write_string(text.center(16))
	

	# NONE = 0
	# DoubleUp = 1
	# SingleUp = 2
	# FortyFiveUp = 3
	# Flat = 4
	# FortyFiveDown = 5
	# SingleDown = 6
	# DoubleDown = 7
	#  'NOT COMPUTABLE': 8
	#  'RATE OUT OF RANGE': 9

	def update_value_time_trend(self,value,mins,trend):
		valStr = "--"
		trendChars = "  "
		if (mins < 20):
			valStr = str(value)
			trendChars = self.__get_trend_chars(trend)
	
		print(valStr + "   " + str(mins))

		valStr = valStr.replace("0","O")
		valStr = valStr.rjust(6)
		self.__lcd.cursor_pos = (0, 0)
		self.__lcd.write_string(valStr + "          ")   # this is lazy

		self.__lcd.cursor_pos = (1, 4)
		self.__lcd.write_string(trendChars)

		ageStr = self.update_age(mins)		
		

	def update_age(self, mins):
		ageStr = "now"
		if (mins > 50):
			ageStr = "50+"
		elif (mins > 0):
			ageStr = str(mins) + "m"

		ageStr = ageStr.replace("0","O")
		ageStr = ageStr.rjust(3)
		
		#pos = 16 - len(ageStr)
		self.__lcd.cursor_pos = (1, 13)
		self.__lcd.write_string(ageStr)
		

	def __get_trend_chars(self,trend):
		if(trend == 0):
			return "**"
		if(trend == 1):
			return "\x02\x02"
		if(trend == 2):
			return "\x02 "
		if(trend == 3):
			return "\x03 "
		if(trend == 4):
			return "-\x7e"
		if(trend == 5):
			return "\x05 "
		if(trend == 6):
			return "\x06 "
		if(trend == 7):
			return "\x06\x06"
		if(trend == 8):
			return "NC"
		if(trend == 9):
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
		self.__lcd.create_char(2, upArrow)

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
		self.__lcd.create_char(3, upSlight)

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
		self.__lcd.create_char(5, dnSlight)

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
		self.__lcd.create_char(6, dnArrow)

