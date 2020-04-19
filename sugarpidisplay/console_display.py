from .trend import Trend
from .graph import *


class ConsoleDisplay:

	__logger = None

	def __init__(self, logger):
		self.__logger = logger
		return None

	def open(self):
		return True

	def close(self):
		return True

	def clear(self):
		pass

	def show_centered(self,logLevel,line0,line1):
		text = (line0 if line0 is not None else "") + " || " + (line1 if line1 is not None else "")
		self.__logger.debug("Display: " + text)
		print(text)

	def update(self,updates):
		print("got update")
		if 'readings' in updates.keys():
			testDrawGraph(updates['readings'])

	def update_value_time_trend(self,value,mins,trend):
		valStr = "--"
		if (value > 0):
			valStr = str(value)

		print(valStr + "   " + self.__get_trend_word(trend) + "   " + str(mins))
		valStr = valStr.rjust(3)
		self.update_age(mins)


	def update_age(self, mins):
		ageStr = "now"
		if (mins > 50):
			ageStr = "50+"
		elif (mins > 0):
			ageStr = str(mins) + "m"

		ageStr = ageStr.rjust(3)

	def updateAnimation(self):
		pass

	def __get_trend_word(self,trend):
		if(trend == Trend.DoubleUp):
			return "DoubleUp"
		elif(trend == Trend.SingleUp):
			return "SingleUp"
		elif(trend == Trend.FortyFiveUp):
			return "FortyFiveUp"
		elif(trend == Trend.Flat):
			return "Flat"
		elif(trend == Trend.FortyFiveDown):
			return "FortyFiveDown"
		elif(trend == Trend.SingleDown):
			return "SingleDown"
		elif(trend == Trend.DoubleDown):
			return "DoubleDown"
		elif(trend == Trend.NotComputable):
			return "NOT COMPUTABLE"
		elif(trend == Trend.RateOutOfRange):
			return "RATE OUT OF RANGE"
		else:
			return "NONE"
