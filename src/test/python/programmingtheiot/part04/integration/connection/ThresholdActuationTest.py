import logging
import time
import unittest

from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.data.SensorData import SensorData
import programmingtheiot.common.ConfigConst as ConfigConst

class ThresholdActuationTest(unittest.TestCase):
    """
    Integration test for threshold-based actuation.
    """
    
    def setUp(self):
        logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
        self.sensorManager = SensorAdapterManager()
        self.actuatorManager = ActuatorAdapterManager()
        
        # Connect sensor manager to actuator manager
        self.sensorManager.setActuatorManager(self.actuatorManager)
        
    def testTemperatureThreshold(self):
        """Test temperature threshold-based actuation"""
        # Create test sensor data above threshold
        sensorData = SensorData(typeID=ConfigConst.TEMP_SENSOR_TYPE)
        sensorData.setValue(30.0)  # Above default threshold of 25.0
        
        # Check if actuation is triggered
        actuationTriggered = self.sensorManager.thresholdManager.checkThresholds(sensorData)
        self.assertTrue(actuationTriggered, "Temperature threshold actuation should be triggered")
        
    def testHumidityThreshold(self):
        """Test humidity threshold-based actuation"""
        # Create test sensor data above threshold
        sensorData = SensorData(typeID=ConfigConst.HUMIDITY_SENSOR_TYPE)
        sensorData.setValue(50.0)  # Above default threshold of 45.0
        
        # Check if actuation is triggered
        actuationTriggered = self.sensorManager.thresholdManager.checkThresholds(sensorData)
        self.assertTrue(actuationTriggered, "Humidity threshold actuation should be triggered")
        
    def testPressureThreshold(self):
        """Test pressure threshold-based actuation"""
        # Create test sensor data above threshold
        sensorData = SensorData(typeID=ConfigConst.PRESSURE_SENSOR_TYPE)
        sensorData.setValue(1020.0)  # Above default threshold of 1010.0
        
        # Check if actuation is triggered
        actuationTriggered = self.sensorManager.thresholdManager.checkThresholds(sensorData)
        self.assertTrue(actuationTriggered, "Pressure threshold actuation should be triggered")
        
    def testBelowThreshold(self):
        """Test that actuation is not triggered below thresholds"""
        # Create test sensor data below thresholds
        tempData = SensorData(typeID=ConfigConst.TEMP_SENSOR_TYPE)
        tempData.setValue(20.0)  # Below threshold
        
        humidityData = SensorData(typeID=ConfigConst.HUMIDITY_SENSOR_TYPE)
        humidityData.setValue(40.0)  # Below threshold
        
        pressureData = SensorData(typeID=ConfigConst.PRESSURE_SENSOR_TYPE)
        pressureData.setValue(1000.0)  # Below threshold
        
        # Check that no actuation is triggered
        self.assertFalse(self.sensorManager.thresholdManager.checkThresholds(tempData))
        self.assertFalse(self.sensorManager.thresholdManager.checkThresholds(humidityData))
        self.assertFalse(self.sensorManager.thresholdManager.checkThresholds(pressureData))
        
    def testLongRunning(self):
        """Test long-running operation with multiple sensor readings"""
        # Start the managers
        self.sensorManager.startManager()
        
        # Let it run for a few seconds
        time.sleep(5)
        
        # Stop the managers
        self.sensorManager.stopManager()
        
if __name__ == '__main__':
    unittest.main() 