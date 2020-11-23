import logging
import os
import time
import traceback
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont

import sugarpidisplay.epd2in13_V2 as epd2in13

from .graph import drawGraph
from .trend import Trend
from .utils import get_reading_age_minutes, get_stale_minutes, seconds_since

minLogLevel = logging.INFO
idleRefreshSeconds = 330

class Panel:
    def __init__(self,xy,size):
        self.xy = xy
        self.size = size
        self.image = Image.new('1', size, 255)

class ScreenData:

    def __init__(self, readingTime = None, value = 0, trend = Trend.NONE):
        self.ReadingTime = readingTime
        self.Value = value
        self.Trend = trend
        self.Age = 999
        self.IsStale = True
        if (readingTime is not None):
            self.Age = get_reading_age_minutes(readingTime)
            self.IsStale = self.Age >= get_stale_minutes()
        if (self.Trend is None or self.IsStale):
            self.Trend = Trend.NONE

        self.UpdateTime = datetime.now(timezone.utc)

    def isDiff(self, other):
        # exclude age, because it will increment every minute
        return (self.ReadingTime != other.ReadingTime or
        self.Value != other.Value or 
        self.Trend != other.Trend or
        self.IsStale != other.IsStale)

class EpaperDisplay:
    __epd = None
    __screenMode = ""
    __logger = None
    __hPortraitImage = None
    __hLandscapeImage = None

    __dirty = False

    __lastScreenData = None
    __arrowImgSingle = None
    __arrowImgDouble = None

    def __init__(self, logger):
        self.__logger = logger
        self.__hPortraitImage = Image.new('1', (epd2in13.EPD_WIDTH, epd2in13.EPD_HEIGHT), 255)   # 122x250
        self.__hLandscapeImage = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)   # 250x122

        self.__bgPanel = Panel((0,0), (122,70))
        self.__agePanel = Panel((0,70), (70,52))
        self.__trendPanel = Panel((70,70), (52,52))
        self.__graphPanel = Panel((0,122), (122,128))
        self.__bannerPanel = Panel((0,0), (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH))

        self.__allPanels = [self.__bgPanel, self.__agePanel, self.__trendPanel, self.__graphPanel, self.__bannerPanel]

        absFilePath = os.path.abspath(__file__)
        dir = os.path.dirname(absFilePath)
        fontPath = os.path.join(dir, 'Inconsolata-Regular.ttf')
        self.__fontMsg = ImageFont.truetype(fontPath, 30)
        self.__fontBG = ImageFont.truetype(fontPath, 74)
        self.__fontAge = ImageFont.truetype(fontPath, 22)
        self.__fontTime = ImageFont.truetype(fontPath, 18)

        self.__initTrendImages(self.__trendPanel.size)
        self.__lastScreenData = ScreenData()
        return None

    def open(self):
        self.__epd = epd2in13.EPD()
        #self.__create_custom_chars()
        return True

    def close(self):
        self.__epd.init(self.__epd.FULL_UPDATE)
        self.__epd.Clear(0xFF)
        self.__epd.sleep()
        self.__epd = None
        return True

    def __drawScreen(self):
        if (not self.__dirty):
            return
        self.__dirty = False
        if self.__screenMode == "egv":
            self.__wipeImage(self.__hPortraitImage)
            self.__hPortraitImage.paste(self.__bgPanel.image, self.__bgPanel.xy)
            self.__hPortraitImage.paste(self.__agePanel.image, self.__agePanel.xy)
            self.__hPortraitImage.paste(self.__trendPanel.image, self.__trendPanel.xy)
            self.__hPortraitImage.paste(self.__graphPanel.image, self.__graphPanel.xy)

            self.__epd.init(self.__epd.FULL_UPDATE)
            self.__epd.display(self.__epd.getbuffer(self.__hPortraitImage))
            self.__epd.sleep()
        if self.__screenMode == "text":
            self.__wipeImage(self.__hLandscapeImage)
            self.__hLandscapeImage.paste(self.__bannerPanel.image, self.__bannerPanel.xy)
            self.__epd.init(self.__epd.FULL_UPDATE)
            self.__epd.display(self.__epd.getbuffer(self.__hLandscapeImage))
            self.__epd.sleep()

    def __wipeImage(self, img):
        if (img is None):
            return
        draw = ImageDraw.Draw(img)
        draw.rectangle(((0,0), img.size), fill = (255) )
        #size = (img.size[0]-1, img.size[1]-1)
        #draw.rectangle(((0,0), size), outline = (0), fill = (255) )

    def __wipePanel(self, panel):
        self.__wipeImage(panel.image)

    def clear(self):
        self.__epd.init(self.__epd.FULL_UPDATE)
        print("Clear...")
        self.__epd.Clear(0xFF)
        self.__epd.sleep()
        for panel in self.__allPanels:
            self.__wipePanel(panel)
        self.__wipeImage(self.__hPortraitImage)
        self.__wipeImage(self.__hLandscapeImage)
        self.__screenMode = ""

    def show_centered(self, logLevel, line0, line1):
        if logLevel < minLogLevel:
            return
        self.__setScreenModeToText()
        line0 = line0 if line0 is not None else ""
        line1 = line1 if line1 is not None else ""

        self.__logger.debug("Display: " + line0 + " || " + line1)
        print("Display: " + line0 + " || " + line1)

        self.__wipePanel(self.__bannerPanel)
        draw = ImageDraw.Draw(self.__bannerPanel.image)
        self.__drawText(draw, (5,5), line0, self.__fontMsg)
        self.__drawText(draw, (5,40), line1, self.__fontMsg)
        self.__dirty = True
        self.__drawScreen()

    def update(self, readings):
        self.__setScreenModeToEgv()

        newScreenData = ScreenData(readings[0].timestamp, readings[0].value, readings[0].trend)

        shouldUpdate = newScreenData.isDiff(self.__lastScreenData) or seconds_since(self.__lastScreenData.UpdateTime) > idleRefreshSeconds
        if not shouldUpdate:
            return

        self.__update_value(newScreenData.Value, newScreenData.IsStale)
        self.__update_trend(newScreenData.Trend)
        #self.__update_age(newScreenData.ReadingTime, newScreenData.Age)
        self.__update_clock(newScreenData.UpdateTime)
        self.__update_graph(readings)

        self.__dirty = True
        self.__lastScreenData = newScreenData
        self.__drawScreen()

    def __update_value(self, value, isStale):
        strikeThrough = isStale or value is None
        valStr = ""
        if (value is not None):
            valStr = str(value)
        valStr = valStr.rjust(3)
        #print(valStr + "   " + str(mins))
        self.__wipePanel(self.__bgPanel)
        drawBg = ImageDraw.Draw(self.__bgPanel.image)
        textXY = (5, 8)

        textSize = self.__drawText(drawBg, textXY, valStr, self.__fontBG)
        if (strikeThrough):
            drawBg.line((textXY[0], textXY[1] + textSize[1]//2, textXY[0]+textSize[0], textXY[1] + textSize[1]//2), fill = 0, width=2)

    def __drawText(self, draw, xy, text, font):
        offset = font.getoffset(text)
        textSize = draw.textsize(text, font = font)
        textSize = (textSize[0] - offset[0], textSize[1] - offset[1])
        draw.text((xy[0]-offset[0], xy[1]-offset[1]), text, font = font, fill = 0)
        return textSize

    def __update_trend(self, trend):
        self.__wipePanel(self.__trendPanel)
        arrowImg = self.__get_trend_image(trend)
        if (arrowImg is not None):
            self.__trendPanel.image.paste(arrowImg, (0,0))

    #def __update_age(self, timestamp, age):
        #mins = (mins//2) * 2 # round to even number
        # if (mins == self.__lastAge):
        #     return
        # self.__lastAge = mins
        # ageStr = "now"
        # if (mins > 0):
        #     ageStr = str(mins) + "m"
        # ageStr = ageStr.rjust(4)

        # Get string in local time
        # TODO - what I'm calling a timestamp is really a datetime.  need to rename

    def __update_clock(self, ts):
        atTime = datetime.fromtimestamp(ts.timestamp()).strftime('%I:%M%p')
        atTime = atTime.replace("AM", "a").replace("PM", "p")
        atTime = atTime.rjust(6)

        self.__wipePanel(self.__agePanel)
        draw = ImageDraw.Draw(self.__agePanel.image)
        # self.__drawText(draw, (5,6), ageStr, self.__fontAge)
        self.__drawText(draw, (5,12), atTime, self.__fontTime)
        self.__dirty = True

    def __update_graph(self, readings):
        self.__wipePanel(self.__graphPanel)
        draw = ImageDraw.Draw(self.__graphPanel.image)
        drawGraph(readings, draw)
        self.__dirty = True

    def updateAnimation(self):
        self.__setScreenModeToEgv()

    def __setScreenModeToEgv(self):
        if (not self.__screenMode == "egv"):
            self.__logger.debug("Display mode EGV")
            self.__screenMode = "egv"
            self.__lastScreenData = ScreenData()

    def __setScreenModeToText(self):
        if (not self.__screenMode == "text"):
            self.__logger.debug("Display mode Text")
            self.__screenMode = "text"

    def __initTrendImages(self, size):
        w = size[0]
        h = size[1]
        x2 = w - 1
        #y2 = h - 1
        lw = 3
        self.__arrowImgSingle = Image.new('1', size, 255)
        draw = ImageDraw.Draw(self.__arrowImgSingle)
        aw = w//4
        ay = h//2
        draw.line((0, ay, x2, ay), fill = 0, width=lw)
        draw.line((x2 - aw, ay - 0.7*aw, x2,ay,  x2 - aw, ay + 0.7*aw), fill = 0, width=lw)

        self.__arrowImgDouble = Image.new('1', size, 255)
        draw = ImageDraw.Draw(self.__arrowImgDouble)
        aw = w//4
        ay = h//2 - 0.8*aw
        draw.line((0, ay, x2, ay), fill = 0, width=lw)
        draw.line((x2 - aw, ay - 0.7*aw, x2,ay,  x2 - aw, ay + 0.7*aw), fill = 0, width=lw)
        ay = h//2 + 0.8*aw
        draw.line((0, ay, x2, ay), fill = 0, width=lw)
        draw.line((x2 - aw, ay - 0.7*aw, x2,ay,  x2 - aw, ay + 0.7*aw), fill = 0, width=lw)

    def __goodRotate(self, img, degrees):
        w = img.size[0]
        h = img.size[1]
        bigImg = Image.new('1', (w*3,h*3), 255)
        bigImg.paste(img, (w,h))
        bitRotatedImg = bigImg.rotate(degrees)
        return bitRotatedImg.crop((w,h, w+w, h+h))

    def __get_trend_image(self, trend):

        if(trend == Trend.NONE):
            return None #"**"
        if(trend == Trend.DoubleUp):
            return self.__goodRotate(self.__arrowImgDouble, 90)
        if(trend == Trend.SingleUp):
            return self.__goodRotate(self.__arrowImgSingle, 90)
        if(trend == Trend.FortyFiveUp):
            return self.__goodRotate(self.__arrowImgSingle, 45)
        if(trend == Trend.Flat):
            return self.__goodRotate(self.__arrowImgSingle, 0)
        if(trend == Trend.FortyFiveDown):
            return self.__goodRotate(self.__arrowImgSingle, -45)
        if(trend == Trend.SingleDown):
            return self.__goodRotate(self.__arrowImgSingle, -90)
        if(trend == Trend.DoubleDown):
            return self.__goodRotate(self.__arrowImgDouble, -90)
        if(trend == Trend.NotComputable):
            return None #"NC"
        if(trend == Trend.RateOutOfRange):
            return None #"HI"
        return self.__arrowImgDouble.rotate(0) #"??"
