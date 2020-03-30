import http.client
from datetime import datetime,timezone
import re
import json
from .utils import *
from .trend import Trend

host = "share2.dexcom.com"
login_resource = "/ShareWebServices/Services/General/LoginPublisherAccountByName"
latestgv_resource = "/ShareWebServices/Services/Publisher/ReadPublisherLatestGlucoseValues"
user_agent = "Dexcom Share/3.0.2.11 CFNetwork/711.2.23 Darwin/14.0.0"
dex_applicationId = "05D6B4A1-5C22-4B17-929B-5913F2186EAB"

class DexcomReader():

	__logger = None
	__sessionId = ""
	__config = {}

	def __init__(self, logger):
		self.__logger = logger

	def set_config(self, __config):
		if 'dexcom_username' not in __config.keys() or 'dexcom_password' not in __config.keys():
			self.__logger.error('Invalid Dexcom __config values')
			return False
		self.__config['username'] = __config['dexcom_username']
		self.__config['password'] = __config['dexcom_password']
		return True

	def login(self):
		self.__sessionId = ""
		try:
			conn = http.client.HTTPSConnection(host)
			payload = self.__get_payload_for_login()
			headers = {
				'Accept':'application/json',
				'Content-Type':'application/json',
				'User-Agent': user_agent
				}
			conn.request("POST", login_resource, payload, headers)

			resp = conn.getresponse()
			if (resp.status != 200):
				self.__logger.warning('Login request return status ' + str(resp.status))
				return False
			respStr = resp.read().decode("utf-8")
			#print(respStr.decode("utf-8"))
			sessionId = respStr.strip("\"")
			self.__logger.debug(sessionId)
			self.__sessionId = sessionId
			return True
		except Exception as e:
			self.__logger.error('Exception during login ' + str(e))
			return False

	def __get_payload_for_login(self):
		loginObj = {
			'accountName': self.__config['username'],
			'password': self.__config['password'],
			'applicationId': dex_applicationId
			}
		return json.dumps(loginObj)

	def get_latest_gv(self):
		result = self.__make_request()
		if (self.__check_session_expire(result)):
			return {"tokenFailed" : True}
		if (result['error'] is not None):
			return {'errorMsg' : result['error']}
		if (result['status'] != 200):
			self.__logger.warning ("Response during get_latest_gv was " + str(result['status']))
			return {'errorMsg' : "HTTP " + str(result['status'])}

		reading = self.__parse_gv(result['content'])
		if (reading is None):
			return {'errorMsg' : 'Bad Resp'}
		return { 'reading' : reading }

	def __make_request(self):
		result = { 'status': 0, 'content': '', 'error': None}
		try:
			conn = http.client.HTTPSConnection(host)

			headers = {
				'Accept':'application/json',
				'Content-Type':'application/json',
				'Content-Length':'0',
				'User-Agent': user_agent
			}
			resource = latestgv_resource + "?minutes=1440&maxCount=1&sessionID=" + str(self.__sessionId)

			conn.request("POST", resource, headers=headers)
			resp = conn.getresponse()

			result['status'] = resp.status
			result['content'] = resp.read().decode("utf-8")
			return result
		except http.client.HTTPException as e:
			self.__logger.error('HTTPException during get_latest_gv ' + str(e))
			result['error'] = "Network error"
			return result
		except Exception as e:
			self.__logger.error('Exception during get_latest_gv ' + str(e))
			result['error'] = "Req error"
			return result

	def __parse_gv(self,data):
		try:
			self.__logger.debug(data)
			list = json.loads(data)
			if (len(list) == 0):
				self.__logger.warning("Dexcom responded with empty list")
				return None
			obj = list[0]
			epochStr = re.sub('[^0-9]','', obj["WT"])
			timestamp = datetime.fromtimestamp(int(epochStr)//1000, timezone.utc)
			minutes_old = get_reading_age_minutes(timestamp)
			value = obj["Value"]
			trend = self.__translateTrend(obj["Trend"])
			# Change this loglevel to INFO if you want each reading logged
			self.__logger.debug("parsed: " + str(timestamp) + "   " + str(value) + "   " + str(trend) + "   " + str(minutes_old) + " mins" )
			utcnow = datetime.now(timezone.utc)
			if(timestamp > utcnow):
				timestamp = utcnow
				self.__logger.warning("Corrected timestamp to now")

			reading = Reading()
			reading.timestamp = timestamp
			reading.value = value
			reading.trend = trend
			return reading
		except Exception as e:
			self.__logger.error('Exception during parse ' + str(e))
			return None

	def __check_session_expire(self, result):
        # Returns 200 with "SessionNotValid" if expired sessionId
        # Returns 500 with "SessionIdNotFound" if unknown sessionId
        # Returns 400 if sessionId is wrong length/format (no way to catch this without catching other 400 reasons)
		if ('content' in result and ("SessionNotValid" in result['content'] or "SessionIdNotFound" in result['content'])):
			return True
        # Just in case it ever returns a sensible result.
		if (result['status'] == 401 or result['status'] == 403):
		    return True
		return False

	def __translateTrend(self, trendNum):
		if(trendNum == 1):
			return Trend.DoubleUp
		elif(trendNum == 2):
			return Trend.SingleUp
		elif(trendNum == 3):
			return Trend.FortyFiveUp
		elif(trendNum == 4):
			return Trend.Flat
		elif(trendNum == 5):
			return Trend.FortyFiveDown
		elif(trendNum == 6):
			return Trend.SingleDown
		elif(trendNum == 7):
			return Trend.DoubleDown
		elif(trendNum == 8):
			return Trend.NotComputable
		elif(trendNum == 9):
			return Trend.RateOutOfRange
		else:
			return Trend.NONE
