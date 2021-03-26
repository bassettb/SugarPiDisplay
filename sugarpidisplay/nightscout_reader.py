import http.client
import json
import re
from datetime import datetime, timezone

from .trend import Trend
from .utils import Reading, get_reading_age_minutes

ns_login_resource = "/api/v2/authorization/request"
ns_latestgv_resource = "/api/v1/entries/sgv?count=12"


class NightscoutReader():
    __logger = None
    __token = ""
    __config = {}

    def __init__(self, logger):
        self.__logger = logger

    def set_config(self, config):
        self.__config.clear()
        if 'nightscout_url' not in config.keys() or 'nightscout_access_token' not in config.keys():
            self.__logger.error('Invalid Nightscout config values')
            return False
        self.__config['url'] = config['nightscout_url']
        self.__config['accessToken'] = config['nightscout_access_token']
        return True

    def login(self):
        self.__sessionId = ""
        try:
            resource = ns_login_resource + "/" + self.__config['accessToken']
            conn = self.__get_connection()
            conn.request("GET", resource)

            resp = conn.getresponse()
            if (resp.status != 200):
                self.__logger.warning(
                    'Login request return status ' + str(resp.status))
                return False
            respStr = resp.read().decode("utf-8")
            #print(respStr.decode("utf-8"))

            respObj = json.loads(respStr)
            self.__token = respObj['token']
            self.__logger.debug(self.__token)
            return True
        except Exception as e:
            self.__logger.error('Exception during login ' + str(e))
            return False

    def get_latest_gv(self):
        result = self.__make_request()
        if (self.__check_session_expire(result)):
            return {'tokenFailed': True}
        if (result['error'] is not None):
            return {'errorMsg': result['error']}
        if (result['status'] != 200):
            self.__logger.warning(
                "Response during get_latest_gv was " + str(result['status']))
            return {'errorMsg': "HTTP " + str(result['status'])}

        readings = self.__parse_gv(result['content'])
        if (readings is None):
            return {'errorMsg': 'Bad Resp'}
        return {'readings': readings}

    def __make_request(self):
        result = {'status': 0, 'content': '', 'error': None}
        try:
            conn = self.__get_connection()

            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + self.__token
            }
            resource = ns_latestgv_resource

            conn.request("GET", resource, headers=headers)
            resp = conn.getresponse()

            result['status'] = resp.status
            if (resp.status != 200):
                return result
            # Nightscout doesn't need content to check auth error
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

    def __parse_gv(self, data):
        try:
            self.__logger.debug(data)
            list = json.loads(data)
            if (len(list) == 0):
                self.__logger.warning("Nightscout responded with empty list")
                return None

            readings = []
            for obj in list:
                result = self.__readingFromReturnedObject(obj)
                if result is not None:
                    readings.append(result)
            return readings

        except Exception as e:
            self.__logger.error('Exception during parse ' + str(e))
            return None

    def __readingFromReturnedObject(self, obj):
        if (obj['type'] != 'sgv'):
            self.__logger.warning("Nightscout: entry was not sgv")
            return None
        epoch = obj['date']
        timestamp = datetime.fromtimestamp(int(epoch//1000), timezone.utc)
        minutes_old = get_reading_age_minutes(timestamp)
        value = obj['sgv']
        trend = self.__translateTrend(obj['direction'])
        # Change this loglevel to INFO if you want each reading logged
        self.__logger.debug("parsed: " + str(timestamp) + "   " + str(value) +
                            "   " + str(trend) + "   " + str(minutes_old) + " mins")
        utcnow = datetime.now(timezone.utc)
        if(timestamp > utcnow):
            timestamp = utcnow
            self.__logger.warning("Corrected timestamp to now")

        return Reading(timestamp, value, trend)

    def __check_session_expire(self, result):
        if (result['status'] == 401):
            return True
        return False

    def __get_connection(self):
        url = self.__config['url'].lower()
        if (url.startswith('http://')):
            url = url[7:]
            return http.client.HTTPConnection(url)
        if (url.startswith('https://')):
            url = url[8:]
            return http.client.HTTPSConnection(url)
        return http.client.HTTPConnection(url)

    def __translateTrend(self, trendStr):
        if(trendStr == "DoubleUp"):
            return Trend.DoubleUp
        if(trendStr == "SingleUp"):
            return Trend.SingleUp
        if(trendStr == "FortyFiveUp"):
            return Trend.FortyFiveUp
        if(trendStr == "Flat"):
            return Trend.Flat
        if(trendStr == "FortyFiveDown"):
            return Trend.FortyFiveDown
        if(trendStr == "SingleDown"):
            return Trend.SingleDown
        if(trendStr == "DoubleDown"):
            return Trend.DoubleDown
        #if(trendStr == "NotComputable"):
        #    return Trend.
        #if(trendStr == "RateOutOfRange"):
        #    return Trend.
        return Trend.NONE
