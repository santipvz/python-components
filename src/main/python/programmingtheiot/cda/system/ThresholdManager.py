import logging

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.ActuatorData import ActuatorData

class ThresholdManager:
    """
    Manages sensor data thresholds and triggers local actuation when thresholds are crossed.
    """
    
    def __init__(self):
        self.configUtil = ConfigUtil()
        
        # Load threshold configurations
        self.tempThreshold = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.TEMP_THRESHOLD_KEY,
            defaultVal=25.0
        )
        
        self.humidityThreshold = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.HUMIDITY_THRESHOLD_KEY,
            defaultVal=45.0
        )
        
        self.pressureThreshold = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.PRESSURE_THRESHOLD_KEY,
            defaultVal=1010.0
        )
        
        self.actuatorManager = None
        
    def setActuatorManager(self, actuatorManager):
        """Set the actuator manager reference"""
        self.actuatorManager = actuatorManager
        
    def checkThresholds(self, sensorData: SensorData) -> bool:
        """
        Check if sensor data crosses configured thresholds and trigger appropriate actuation.
        Returns True if actuation was triggered, False otherwise.
        """
        if not sensorData or not self.actuatorManager:
            return False
            
        sensorType = sensorData.getTypeID()
        sensorValue = sensorData.getValue()
        actuationTriggered = False
        
        if sensorType == ConfigConst.TEMP_SENSOR_TYPE:
            if sensorValue > self.tempThreshold:
                logging.info(f"Temperature threshold crossed: {sensorValue} > {self.tempThreshold}")
                # Trigger HVAC cooling
                actuatorData = ActuatorData(typeID=ConfigConst.HVAC_ACTUATOR_TYPE)
                actuatorData.setCommand(ConfigConst.COMMAND_ON)
                actuatorData.setValue(ConfigConst.DEFAULT_VAL)
                self.actuatorManager.sendActuatorCommand(actuatorData)
                actuationTriggered = True
                
        elif sensorType == ConfigConst.HUMIDITY_SENSOR_TYPE:
            if sensorValue > self.humidityThreshold:
                logging.info(f"Humidity threshold crossed: {sensorValue} > {self.humidityThreshold}")
                # Trigger dehumidifier
                actuatorData = ActuatorData(typeID=ConfigConst.HUMIDIFIER_ACTUATOR_TYPE)
                actuatorData.setCommand(ConfigConst.COMMAND_ON)
                actuatorData.setValue(ConfigConst.DEFAULT_VAL)
                self.actuatorManager.sendActuatorCommand(actuatorData)
                actuationTriggered = True
                
        elif sensorType == ConfigConst.PRESSURE_SENSOR_TYPE:
            if sensorValue > self.pressureThreshold:
                logging.info(f"Pressure threshold crossed: {sensorValue} > {self.pressureThreshold}")
                # Trigger LED display warning
                actuatorData = ActuatorData(typeID=ConfigConst.LED_DISPLAY_ACTUATOR_TYPE)
                actuatorData.setCommand(ConfigConst.COMMAND_ON)
                actuatorData.setValue(ConfigConst.DEFAULT_VAL)
                self.actuatorManager.sendActuatorCommand(actuatorData)
                actuationTriggered = True
                
        return actuationTriggered 