import datetime
import json

class Message:
    def setTimeNow(self):
        self.time = str(datetime.datetime.now())

    def __str__(self):
        return json.dumps(self.__dict__)

    def fromJson(self, json_str):
        self.__dict__ = json.loads(json_str)
        #print(self, json.loads(json_str))