import datetime
import time

try:
	import sys
	import socket
	import fcntl
	import struct
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
	delta = datetime.datetime.utcnow() - timestamp
	minutes_old = int(delta.total_seconds() / 60)
	return minutes_old

def now_plus_seconds(seconds):
	return datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)

class Reading():
	timestamp = None
	value = 0
	trend = 0
