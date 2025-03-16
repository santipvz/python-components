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

class DataUtil():
    def __init__(self, encodeToUtf8: bool = False):
        """
        Constructor.
        :param encodeToUtf8: Si es True, la salida JSON se codificará en UTF-8.
        """
        self.encodeToUtf8 = encodeToUtf8
        logging.info("Created DataUtil instance.")

    def actuatorDataToJson(self, data: ActuatorData = None, useDecForFloat: bool = False) -> str:
        """
        Convierte un objeto ActuatorData a una cadena JSON.
        """
        if not data:
            logging.debug("ActuatorData is null. Returning empty string.")
            return ""
        jsonData = self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)
        return jsonData

    def sensorDataToJson(self, data: SensorData = None, useDecForFloat: bool = False) -> str:
        """
        Convierte un objeto SensorData a una cadena JSON.
        """
        if not data:
            logging.debug("SensorData is null. Returning empty string.")
            return ""
        jsonData = self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)
        return jsonData

    def systemPerformanceDataToJson(self, data: SystemPerformanceData = None, useDecForFloat: bool = False) -> str:
        """
        Convierte un objeto SystemPerformanceData a una cadena JSON.
        """
        if not data:
            logging.debug("SystemPerformanceData is null. Returning empty string.")
            return ""
        jsonData = self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)
        return jsonData

    def jsonToActuatorData(self, jsonData: str = None, useDecForFloat: bool = False) -> ActuatorData:
        """
        Convierte una cadena JSON a una instancia de ActuatorData.
        """
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning None.")
            return None
        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
        ad = ActuatorData()
        self._updateIotData(jsonStruct, ad)
        return ad

    def jsonToSensorData(self, jsonData: str = None, useDecForFloat: bool = False) -> SensorData:
        """
        Convierte una cadena JSON a una instancia de SensorData.
        """
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning None.")
            return None
        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
        sd = SensorData()
        self._updateIotData(jsonStruct, sd)
        return sd

    def jsonToSystemPerformanceData(self, jsonData: str = None, useDecForFloat: bool = False) -> SystemPerformanceData:
        """
        Convierte una cadena JSON a una instancia de SystemPerformanceData.
        """
        if not jsonData:
            logging.warning("JSON data is empty or null. Returning None.")
            return None
        jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
        spd = SystemPerformanceData()
        self._updateIotData(jsonStruct, spd)
        return spd

    def _formatDataAndLoadDictionary(self, jsonData: str, useDecForFloat: bool = False) -> dict:
        """
        Reemplaza las comillas y valores booleanos para asegurar la compatibilidad,
        y carga la cadena JSON en un diccionario.
        """
        jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')
        if useDecForFloat:
            jsonStruct = json.loads(jsonData, parse_float=Decimal)
        else:
            jsonStruct = json.loads(jsonData)
        return jsonStruct

    def _generateJsonData(self, obj, useDecForFloat: bool = False) -> str:
        """
        Genera una cadena JSON a partir de un objeto, utilizando JsonDataEncoder.
        """
        if self.encodeToUtf8:
            jsonData = json.dumps(obj, cls=JsonDataEncoder).encode('utf8')
        else:
            jsonData = json.dumps(obj, cls=JsonDataEncoder, indent=4)
        if jsonData:
            # Si se codificó en UTF-8, se decodifica para realizar el reemplazo
            if isinstance(jsonData, bytes):
                jsonData = jsonData.decode('utf8')
            jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')
        return jsonData

    def _updateIotData(self, jsonStruct: dict, obj):
        """
        Actualiza los atributos de un objeto basado en los pares clave/valor del diccionario JSON.
        """
        varStruct = vars(obj)
        for key in jsonStruct:
            if key in varStruct:
                setattr(obj, key, jsonStruct[key])
            else:
                logging.warning("JSON data contains key not mappable to object: %s", key)

class JsonDataEncoder(JSONEncoder):
    """
    Clase auxiliar para facilitar la codificación JSON de un objeto que puede convertirse a diccionario.
    """
    def default(self, o):
        return o.__dict__
