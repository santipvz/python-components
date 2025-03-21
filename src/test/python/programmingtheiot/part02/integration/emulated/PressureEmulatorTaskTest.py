#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging
import unittest

from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.emulated.PressureSensorEmulatorTask import PressureSensorEmulatorTask

class PressureEmulatorTaskTest(unittest.TestCase):
	"""
	This test case class contains very basic unit tests for
	PressureEmulatorTaskTest. It should not be considered complete,
	but serve as a starting point for the student implementing
	additional functionality within their Programming the IoT
	environment.
	
	NOTE: This test requires the sense_emu_gui to be running
	and must have access to the underlying libraries that
	support the pisense module. On Windows, one way to do
	this is by installing pisense and sense-emu within the
	Bash on Ubuntu on Windows environment and then execute this
	test case from the command line, as it will likely fail
	if run within an IDE in native Windows.
	
	"""
	
	@classmethod
	def setUpClass(self):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("Testing PressureEmulatorTaskTest class [using SenseHAT emulator]...")
		self.pEmuTask = PressureSensorEmulatorTask()
		
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testReadEmulator(self):
		sd1 = self.pEmuTask.generateTelemetry()
		
		if sd1:
			self.assertEqual(sd1.getTypeID(), ConfigConst.PRESSURE_SENSOR_TYPE)
			logging.info("SensorData: %f - %s", sd1.getValue(), str(sd1))
			
			# wait 5 seconds
			sleep(5)
		else:
			logging.warning("FAIL: SensorData is None.")
			
		sd2 = self.pEmuTask.generateTelemetry()
		
		if sd2:
			self.assertEqual(sd2.getTypeID(), ConfigConst.PRESSURE_SENSOR_TYPE)
			logging.info("SensorData: %f - %s", sd2.getValue(), str(sd2))
			
			# wait 5 seconds
			sleep(5)
		else:
			logging.warning("FAIL: SensorData is None.")
			
if __name__ == "__main__":
	unittest.main()
	