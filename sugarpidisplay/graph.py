from PIL import Image,ImageDraw,ImageFont
from .utils import *

gW = 122
gH = 128

topMargin = 4
botMargin = 4
leftMargin = 1
rightMargin = 1
xZeroOffset = gW - 6 -1
yZeroOffset = gH - botMargin - 1
maxBgVal = 400.0
minBgVal = 60.0
minTimeVal = -55
maxTimeVal = 0

def drawAxes(draw):

    # x-axis
    draw.line(((leftMargin, yZeroOffset), (gW-rightMargin-1, yZeroOffset)), fill = 0, width=1)

    # lines at 70 and 180
    drawSafeBgGridLine(draw, 70, 3)
    drawSafeBgGridLine(draw, 180, 3)

    # x-ticks
    for t in range(maxTimeVal,minTimeVal-1,-5):
        x = xZeroOffset + translateTimeToX(t)
        draw.line(((x,yZeroOffset-1), (x,yZeroOffset+1)), fill = 0, width=1)

    # x-gridlines
    for t in range(maxTimeVal,minTimeVal-1,-10):
        drawTimeGridLine(draw, t, 4)

def drawSafeBgGridLine(draw, value, gap):
    y = yZeroOffset - translateBgToY(value)
    x = leftMargin
    while True:
        draw.point((x,y), fill=0)
        x += gap
        if x > gW - rightMargin - 1:
            break

def drawTimeGridLine(draw, time, gap):
    x = xZeroOffset + translateTimeToX(time)
    y = yZeroOffset - gap
    while True:
        draw.point((x,y), fill=0)
        y -= gap
        if (y<topMargin):
            break

def drawXYDot(draw, xy):
    x, y = xy
    xP = xZeroOffset + x
    yP = yZeroOffset - y
    draw.line(((xP-2,yP),(xP+2,yP)), fill = 0, width=3)
    draw.line(((xP,yP-2),(xP,yP+2)), fill = 0, width=3)



def translateBgToY(y):
    valHeight = maxBgVal - minBgVal
    pixelHeight = gH - topMargin - botMargin
    yScaled = ((y - minBgVal) / valHeight) * pixelHeight
    return yScaled

def translateTimeToX(bg):
    return bg * 2

def translateValToXY(value):
    time, bg = value
    bg = min((bg, maxBgVal))
    bg = max((bg, minBgVal))
    return (translateTimeToX(time), translateBgToY(bg))

def inTimeRange(value):
    time, bg = value
    return (time >= minTimeVal and time <= maxTimeVal)

def valuesFromReadings(readings):
    values = []
    for reading in readings:
        value = (0 - get_reading_age_minutes(reading.timestamp), reading.value)
        values.append(value)
    return values

def drawGraph(draw, readings):
    values = valuesFromReadings(readings)
    drawAxes(draw)

    xyArray = []
    for val in values:
        if inTimeRange(val):
            xyArray.append(translateValToXY(val))

    for xy in xyArray:
        drawXYDot(draw, xy)


def testDrawGraph(readings):
    graphImg = Image.new('1', (gW, gH), 255)
    draw = ImageDraw.Draw(graphImg)
    drawGraph(draw, readings)
    graphImg.save("/Users/bryan/graph.png","PNG")


# values = [
#     (0,100),
#     (-5,120),
#     (-10,140),
#     (-15,150),
#     (-20,180),
#     (-25,240),
#     (-30,300),
#     (-35,350)
# ]
# drawGraph(values)
