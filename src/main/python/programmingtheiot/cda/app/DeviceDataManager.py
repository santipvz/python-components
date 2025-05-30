#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager
from programmingtheiot.common import ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class DeviceDataManager(IDataMessageListener):
    """
    Shell representation of class for student implementation.
    """
    
    def __init__(self):
        self.configUtil = ConfigUtil()

        self.enableSystemPerf = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_SYSTEM_PERF_KEY
        )

        self.enableSensing = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_SENSING_KEY
        )

        self.enableActuation = True

        self.sysPerfMgr = None
        self.sensorAdapterMgr = None
        self.actuatorAdapterMgr = None

        self.enableMqttClient = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_MQTT_CLIENT_KEY
        )

        self.mqttClient = None

        if self.enableMqttClient:
            self.mqttClient = MqttClientConnector()
            self.mqttClient.setDataMessageListener(self)

        self.coapClient = None
        self.coapServer = None

        self.actuatorResponseCache = {}
        self.sensorDataCache = {}
        self.systemPerfDataCache = {}

        if self.enableSystemPerf:
            self.sysPerfMgr = SystemPerformanceManager()
            self.sysPerfMgr.setDataMessageListener(self)
            logging.info("Local system performance tracking enabled")

        if self.enableSensing:
            self.sensorAdapterMgr = SensorAdapterManager()
            self.sensorAdapterMgr.setDataMessageListener(self)
            logging.info("Local sensor tracking enabled")

        if self.enableActuation:
            self.actuatorAdapterMgr = ActuatorAdapterManager(dataMsgListener=self)
            logging.info("Local actuation capabilities enabled")

        self.handleTempChangeOnDevice = self.configUtil.getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.HANDLE_TEMP_CHANGE_ON_DEVICE_KEY
        )

        self.triggerHvacTempFloor = self.configUtil.getFloat(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.TRIGGER_HVAC_TEMP_FLOOR_KEY
        )

        self.triggerHvacTempCeiling = self.configUtil.getFloat(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.TRIGGER_HVAC_TEMP_CEILING_KEY
        )

    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
        """
        Retrieves the named actuator data (response) item from the internal data cache.

        @param name
        @return ActuatorData
        """
        if name in self.actuatorResponseCache:
            return self.actuatorResponseCache[name]
        return None

    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
        """
        Retrieves the named sensor data item from the internal data cache.

        @param name
        @return SensorData
        """
        if name in self.sensorDataCache:
            return self.sensorDataCache[name]
        return None

    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
        """
        Retrieves the named system performance data from the internal data cache.

        @param name
        @return SystemPerformanceData
        """
        if name in self.systemPerfDataCache:
            return self.systemPerfDataCache[name]
        return None

    def handleActuatorCommandMessage(self, data: ActuatorData) -> ActuatorData:
        if data:
            logging.info("Processing actuator command message.")
            # TODO: add further validation before sending the command
            return self.actuatorAdapterMgr.sendActuatorCommand(data)
        else:
            logging.warning("Received invalid ActuatorData command message. Ignoring.")
            return None

    def handleActuatorCommandResponse(self, data: ActuatorData = None) -> bool:
        if data:
            logging.debug("Incoming actuator response received (from actuator manager): %s", str(data))
            # store the data in the cache
            self.actuatorResponseCache[data.getName()] = data

            # convert ActuatorData to JSON and get the msg resource
            actuatorMsg = DataUtil().actuatorDataToJson(data)
            resourceName = ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE

            # delegate to the transmit function any potential upstream comm's
            self._handleUpstreamTransmission(resource=resourceName, msg=actuatorMsg)
            return True

        logging.warning("Incoming actuator response is invalid (null). Ignoring.")
        return False

    def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
        """
        This callback method is generic and designed to handle any incoming string-based
        message, which will likely be JSON-formatted and need to be converted to the appropriate
        data type. You may not need to use this callback at all.

        @param data The incoming JSON message.
        @return boolean
        """
        pass

    def handleSensorMessage(self, data: SensorData = None) -> bool:
        if data:
            logging.info("Incoming sensor data received (from sensor manager): %s", str(data))
            # TODO: Optionally, implement `_handleSensorDataAnalysis()` to handle internal analytics
            self._handleSensorDataAnalysis(data)
            # store the data in the cache
            self.sensorDataCache[data.getName()] = data

            # Convert the `SensorData` instance to JSON
            jsonData = DataUtil().sensorDataToJson(sensorData=data)
            # Pass the resource and newly generated JSON data to `_handleUpstreamTransmission()`
            self._handleUpstreamTransmission(
                resource=ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, msg=jsonData
            )
            return True

        logging.warning("Incoming sensor data is invalid (null). Ignoring.")
        return False

    def handleSystemPerformanceMessage(self, data: SystemPerformanceData = None) -> bool:
        if data:
            logging.debug("Incoming system performance message received (from sys perf manager): %s", str(data))
            # store the data in the cache
            self.systemPerfDataCache[data.getName()] = data

            # Convert the `SystemPerformanceData` instance to JSON
            jsonData = DataUtil().systemPerformanceDataToJson(data)
            # Pass the resource and newly generated JSON data to `_handleUpstreamTransmission()`
            self._handleUpstreamTransmission(
                resource=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE, msg=jsonData
            )
            return True

        logging.warning("Incoming system performance data is invalid (null). Ignoring.")
        return False

    def setSystemPerformanceDataListener(self, listener: ISystemPerformanceDataListener = None):
        if listener:
            self.sysPerfMgr.setDataMessageListener(listener)

    def setTelemetryDataListener(self, name: str = None, listener: ITelemetryDataListener = None):
        pass  # NOTE: Not implemented in this version

    def startManager(self):
        logging.info("Starting DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.startManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.startManager()

        logging.info("Started DeviceDataManager.")

        if self.mqttClient:
            self.mqttClient.connectClient()
            self.mqttClient.subscribeToTopic(
                ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, qos=ConfigConst.DEFAULT_QOS
            )

    def stopManager(self):
        logging.info("Stopping DeviceDataManager...")

        if self.sysPerfMgr:
            self.sysPerfMgr.stopManager()

        if self.sensorAdapterMgr:
            self.sensorAdapterMgr.stopManager()

        logging.info("Stopped DeviceDataManager.")

        if self.mqttClient:
            self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
            self.mqttClient.disconnectClient()

    def _handleIncomingDataAnalysis(self, msg: str):
        """
        Call this from handleIncomeMessage() to determine if there's
        any action to take on the message. Steps to take:
        1) Validate msg: Most will be ActuatorData, but you may pass other info as well.
        2) Convert msg: Use DataUtil to convert if appropriate.
        3) Act on msg: Determine what - if any - action is required, and execute.
        """
        pass

    def _handleSensorDataAnalysis(self, data: SensorData):
        if self.handleTempChangeOnDevice and data.getTypeID() == ConfigConst.TEMP_SENSOR_TYPE:
            logging.info(
                "Handle temp change: %s - type ID: %s",
                str(self.handleTempChangeOnDevice),
                str(data.getTypeID()),
            )

            ad = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)

            if data.getValue() > self.triggerHvacTempCeiling:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempCeiling)
            elif data.getValue() < self.triggerHvacTempFloor:
                ad.setCommand(ConfigConst.COMMAND_ON)
                ad.setValue(self.triggerHvacTempFloor)
            else:
                ad.setCommand(ConfigConst.COMMAND_OFF)

            self.actuatorAdapterMgr.sendActuatorCommand(ad)

    def _handleUpstreamTransmission(self, resource=None, msg: str = None):
        """
        Handles the upstream transmission of data to the cloud.
        Currently supports MQTT.

        @param resource The resource enumeration.
        @param msg The message to send.
        """
        logging.info("Upstream transmission invoked. Checking comm's integration.")
        if self.mqttClient:
            if self.mqttClient.isClientConnected():
                if resource == ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE:
                    topic = resource
                elif resource == ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE:
                    topic = resource
                else:
                    logging.warning(
                        "Unknown resource type for upstream transmission: %s. Ignoring.", resource
                    )
                    return

                logging.debug("Published incoming data to resource (MQTT): %s", resource)
                self.mqttClient.publishMessage(resource=topic, msg=msg, qos=ConfigConst.DEFAULT_QOS)
            else:
                logging.warning("MQTT client is not connected. Cannot publish message.")
