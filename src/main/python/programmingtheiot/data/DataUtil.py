#####
#
# This class is part of the Programming the Internet of Things project.
#
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import json
import logging
from decimal import Decimal
from json import JSONEncoder

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class DataUtil:
    """
    Shell representation of class for student implementation.

    """

    def __init__(self, encodeToUtf8=False):
        self.encodeToUtf8 = encodeToUtf8
        logging.info("Created DataUtil instance.")

    def actuatorDataToJson(
        self, actuatorData: ActuatorData = None, useDecForFloat: bool = False
    ):
        if not actuatorData:
            logging.debug("ActuatorData is null. Returning empty string.")
            return ""

        logging.debug("Encoding ActuatorData to JSON [pre] --> %s", str(actuatorData))
        jsonData = self._generateJsonData(actuatorData, useDecForFloat=False)
        logging.debug("Encoding ActuatorData to JSON [post] --> %s", str(jsonData))

        return jsonData

    def sensorDataToJson(
        self, sensorData: SensorData = None, useDecForFloat: bool = False
    ):
        if not sensorData:
            logging.debug("SensorData is null. Returning empty string.")
            return ""

        logging.debug("Encoding SensorData to JSON [pre] --> %s", str(sensorData))
        jsonData = self._generateJsonData(obj=sensorData, useDecForFloat=False)
        logging.debug("Encoding SensorData to JSON [post] --> %s", str(jsonData))

        return jsonData

    def systemPerformanceDataToJson(
        self, sysPerfData: SystemPerformanceData = None
    ):
        if not sysPerfData:
            logging.debug("SystemPerformanceData is null. Returning empty string.")
            return ""

        logging.debug(
            "Encoding SystemPerformanceData to JSON [pre] --> %s", str(sysPerfData)
        )
        
        # Create a dictionary from the object's attributes
        sysPerfDict = vars(sysPerfData)
        
        # Remove unwanted keys for Ubidots
        keys_to_remove = ['statusCode', 'typeID', 'longitude', 'elevation', 'latitude']
        for key in keys_to_remove:
            if key in sysPerfDict:
                del sysPerfDict[key]
                
        # Convert the modified dictionary to JSON
        jsonData = json.dumps(sysPerfDict, indent=4)
        
        # The base _generateJsonData also does some replacements, apply them here
        if jsonData:
            jsonData = (
                jsonData.replace("'", '"')
                .replace("False", "false")
                .replace("True", "true")
            )


        logging.debug(
            "Encoding SystemPerformanceData to JSON [post] --> %s", str(jsonData)
        )

        return jsonData

    def jsonToActuatorData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning null.")
            return None

        jsonStruct = self._formatDataAndLoadDictionary(
            jsonData, useDecForFloat=useDecForFloat
        )
        ad = ActuatorData()
        self._updateIotData(jsonStruct, ad)
        return ad

    def jsonToSensorData(self, jsonData: str = None, useDecForFloat: bool = False):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning null.")
            return None

        jsonStruct = self._formatDataAndLoadDictionary(
            jsonData, useDecForFloat=useDecForFloat
        )
        sd = SensorData()
        self._updateIotData(jsonStruct, sd)
        return sd

    def jsonToSystemPerformanceData(
        self, jsonData: str = None, useDecForFloat: bool = False
    ):
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning null.")
            return None

        jsonStruct = self._formatDataAndLoadDictionary(
            jsonData, useDecForFloat=useDecForFloat
        )
        spd = SystemPerformanceData()
        self._updateIotData(jsonStruct, spd)
        return spd

    def _generateJsonData(self, obj, useDecForFloat: bool = False) -> str:
        # NOTE: by default, json.dumps sets ensure_ascii = True, so setting the parameter here is moot and, therefore, excluded from the sample code
        jsonData = None

        if self.encodeToUtf8:
            jsonData = self._formatDataAndLoadDictionary(
                self._convertToJson(obj), useDecForFloat=useDecForFloat
            )
        else:
            jsonData = json.dumps(obj, cls=JsonDataEncoder, indent=4)

        if jsonData:
            jsonData = (
                jsonData.replace("'", '"')
                .replace("False", "false")
                .replace("True", "true")
            )

        return jsonData

    def _formatDataAndLoadDictionary(
        self, jsonData: str, useDecForFloat: bool = False
    ) -> dict:
        jsonData = (
            jsonData.replace(
                "'",
                '"',
            )
            .replace("False", "false")
            .replace("True", "true")
        )

        jsonStruct = None

        if useDecForFloat:
            jsonStruct = json.loads(jsonData, parse_float=Decimal)
        else:
            jsonStruct = json.loads(jsonData)

        return jsonStruct

    def _updateIotData(self, jsonStruct, obj):
        varStruct = vars(obj)
        for key in jsonStruct:
            if key in varStruct:
                setattr(obj, key, jsonStruct[key])
            else:
                logging.warning("JSON data key not mappable to object: %s", key)


class JsonDataEncoder(JSONEncoder):
    """
    Convenience class to facilitate JSON encoding of an object that
    can be converted to a dict.

    """

    def default(self, o):
        return o.__dict__