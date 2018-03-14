from trend import Trend

class ConsoleDisplay:

	def __init__(self):
		return None
	
	def clear(self):
		pass
		
	def show_centered(self,line,text):
		print(text)

	def update_value_time_trend(self,value,mins,trend):
		valStr = "--"
		trendChars = "  "
		if (mins < 20):
			valStr = str(value)
			#trendChars = self.__getTrendChars(trend)
	
		print(valStr + "   " + self.__get_trend_word(trend) + "   " + str(mins))
		valStr = valStr.rjust(3)
		ageStr = self.update_age(mins)	
		

	def update_age(self, mins):
		ageStr = "now"
		if (mins > 50):
			ageStr = "50+"
		elif (mins > 0):
			ageStr = str(mins) + "m"

		ageStr = ageStr.rjust(3)

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
