from PIL import Image,ImageDraw,ImageFont
from .utils import get_reading_age_minutes

# screen dimensions
gW = 122
gH = 128

topMargin = 4
botMargin = 4
leftMargin = 1
rightMargin = 1
# x is time, from -55 minutes to 0
# y is BG, from 60-400
# xZero,yZero is in the bottom right corner
maxBgVal = 400.0
minBgVal = 60.0
minTimeVal = -55
maxTimeVal = 0
xZeroOffset = gW - 6 -1
yZeroOffset = gH - botMargin - 1


def drawAxes(draw):

    # x-axis
    draw.line(((leftMargin, yZeroOffset), (gW-rightMargin-1, yZeroOffset)), fill = 0, width=1)

    # lines at 70 and 180
    drawSafeBgGridLine(draw, 70, 3)
    drawSafeBgGridLine(draw, 180, 3)

    # x-ticks
    for t in range(maxTimeVal,minTimeVal-1,-5):
        x = translateTimeToX(t)
        draw.line(((x,yZeroOffset-1), (x,yZeroOffset+1)), fill = 0, width=1)

    # x-gridlines
    for t in range(maxTimeVal,minTimeVal-1,-10):
        drawTimeGridLine(draw, t, 4)

def drawSafeBgGridLine(draw, value, gap):
    y = translateBgToY(value)
    x = leftMargin
    while True:
        draw.point((x,y), fill=0)
        x += gap
        if x > gW - rightMargin - 1:
            break

def drawTimeGridLine(draw, time, gap):
    x = translateTimeToX(time)
    y = yZeroOffset - gap
    while True:
        draw.point((x,y), fill=0)
        y -= gap
        if (y<topMargin):
            break

def drawXYDot(draw, xy):
    x, y = xy
    xP = x
    yP = y
    draw.line(((xP-2,yP),(xP+2,yP)), fill = 0, width=3)
    draw.line(((xP,yP-2),(xP,yP+2)), fill = 0, width=3)

def translateBgToY(bg):
    bg = min((bg, maxBgVal))
    bg = max((bg, minBgVal))
    valHeight = maxBgVal - minBgVal
    pixelHeight = gH - topMargin - botMargin
    yScaled = ((bg - minBgVal) / valHeight) * pixelHeight
    return yZeroOffset - yScaled

def translateTimeToX(time):
    return xZeroOffset + (time * 2)

def translateValToXY(value):
    time, bg = value
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

def drawGraph(readings, draw):
    values = valuesFromReadings(readings)
    drawAxes(draw)

    xyArray = []
    for val in values:
        if inTimeRange(val):
            xyArray.append(translateValToXY(val))

    for xy in xyArray:
        drawXYDot(draw, xy)

def drawGraphToFile(readings, filename):
    graphImg = Image.new('1', (gW, gH), 255)
    draw = ImageDraw.Draw(graphImg)
    drawGraph(readings, draw)
    graphImg.save(filename)
