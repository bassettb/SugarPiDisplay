import time
from datetime import datetime, timedelta, timezone
from os import uname, path

try:
    import fcntl
    import socket
    import struct
    import sys

    def get_ip_address(ifname):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(ifname[:15], 'utf-8'))
            )[20:24])
        except:
            return ""
except:
    def get_ip_address(ifname):
        return "No IP on PC"


def get_reading_age_minutes(timestamp):
    delta = datetime.now(timezone.utc) - timestamp
    minutes_old = int(delta.total_seconds() / 60)
    return minutes_old


def now_plus_seconds(seconds):
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)


def seconds_since(x):
    delta = datetime.now(timezone.utc) - x
    return int(delta.total_seconds())


def get_stale_minutes():
    return 20

def is_stale_reading(reading):
    readingAgeMins = get_reading_age_minutes(reading.timestamp)
    return readingAgeMins >= get_stale_minutes()

def is_raspberry_pi():
    unameResult = uname()
    return "raspberry" in unameResult.nodename

def get_font_path(ttf):
    absFilePath = path.abspath(__file__)
    dir = path.dirname(absFilePath)
    return path.join(dir, ttf)


class Reading():
    timestamp = None
    value = 0
    trend = 0

    def __init__(self, timestamp, value, trend):
        self.timestamp = timestamp
        self.value = value
        self.trend = trend
