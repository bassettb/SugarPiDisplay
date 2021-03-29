from datetime import datetime, timezone

from .trend import Trend
from .utils import (Reading, get_reading_age_minutes, get_stale_minutes,
                    is_stale_reading)


class ConsoleDisplay:
    __logger = None

    def __init__(self, logger):
        self.__logger = logger
        self.LastScreenData = ScreenData()
        return None

    def set_config(self, config):
        return

    def open(self):
        return True

    def close(self):
        return True

    def clear(self):
        pass

    def show_centered(self, logLevel, line0, line1):
        text = (line0 if line0 is not None else "") + \
            " || " + (line1 if line1 is not None else "")
        self.__logger.debug("Display: " + text)
        print(text)

    def update(self, readings):
        newScreenData = ScreenData(
            readings[0].timestamp, readings[0].value, readings[0].trend)

        if (newScreenData.isDiff(self.LastScreenData)):
            self.__update_console(newScreenData)
            self.LastScreenData = newScreenData

    def __update_console(self, screenData):
        valStr = "---"
        if (screenData.Value > 0):
            valStr = str(screenData.Value).rjust(3)
        age = self.__get_age_str(screenData.Age, screenData.IsStale)
        trendWord = self.__get_trend_word(screenData.Trend)
        print(str(screenData.ReadingTime) + ":  " +
              valStr + "   " + trendWord + "   " + str(age))

    def __get_age_str(self, age, isStale):
        ageStr = "now"
        if (age > get_stale_minutes()):
            ageStr = str(get_stale_minutes()) + "+"
        elif (age > 0):
            ageStr = str(age) + "m"
        return ageStr.rjust(3)

    def updateAnimation(self):
        pass

    def __get_trend_word(self, trend):
        if(trend == Trend.DoubleUp):
            return "DoubleUp"
        if(trend == Trend.SingleUp):
            return "SingleUp"
        if(trend == Trend.FortyFiveUp):
            return "FortyFiveUp"
        if(trend == Trend.Flat):
            return "Flat"
        if(trend == Trend.FortyFiveDown):
            return "FortyFiveDown"
        if(trend == Trend.SingleDown):
            return "SingleDown"
        if(trend == Trend.DoubleDown):
            return "DoubleDown"
        if(trend == Trend.NotComputable):
            return "NOT COMPUTABLE"
        if(trend == Trend.RateOutOfRange):
            return "RATE OUT OF RANGE"

        return "NONE"


class ScreenData:

    def __init__(self, readingTime=None, value=0, trend=Trend.NONE):
        self.ReadingTime = readingTime
        self.Value = value
        self.Trend = trend
        self.Age = 999
        self.IsStale = True
        if (readingTime is not None):
            self.Age = get_reading_age_minutes(readingTime)
            self.IsStale = self.Age >= get_stale_minutes()
        self.UpdateTime = datetime.now(timezone.utc)

    def isDiff(self, other):
        # include age, we can update the console every minute
        return (self.ReadingTime != other.ReadingTime or
                self.Age != other.Age or
                self.Value != other.Value or
                self.Trend != other.Trend or
                self.IsStale != other.IsStale)
