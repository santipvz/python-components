import logging
import time
import json
from datetime import datetime
from pathlib import Path
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager
from programmingtheiot.common import ConfigConst

class SystemTest:
    def __init__(self):
        # Configure logging
        logging.basicConfig(
            format='%(asctime)s:%(levelname)s:%(message)s',
            level=logging.INFO,
            filename='system_test.log'
        )
        
        # Initialize counters
        self.system_perf_samples = 0
        self.sensor_samples = 0
        self.actuator_events = 0
        
        # Initialize managers
        self.sensorManager = SensorAdapterManager()
        self.actuatorManager = ActuatorAdapterManager()
        self.systemPerfManager = SystemPerformanceManager()
        
        # Connect managers
        self.sensorManager.setActuatorManager(self.actuatorManager)
        
        # Create data directory if it doesn't exist
        self.data_dir = Path('test_data')
        self.data_dir.mkdir(exist_ok=True)
        
    def log_metrics(self):
        """Log current metrics to file"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system_perf_samples': self.system_perf_samples,
            'sensor_samples': self.sensor_samples,
            'actuator_events': self.actuator_events
        }
        
        with open(self.data_dir / 'metrics.json', 'a', encoding='utf-8') as f:
            json.dump(metrics, f)
            f.write('\n')
            
    def run_test(self, duration_hours=1):
        try:
            # Start the system
            logging.info("Starting system test...")
            self.sensorManager.startManager()
            self.systemPerfManager.startManager()
            
            # Run for specified duration
            end_time = time.time() + (duration_hours * 3600)
            logging.info("System will run for %d hour(s). Press Ctrl+C to stop early.", duration_hours)
            
            while time.time() < end_time:
                # Log metrics every minute
                self.log_metrics()
                time.sleep(60)
                
        except KeyboardInterrupt:
            logging.info("Test stopped by user.")
        finally:
            # Stop the system
            logging.info("Stopping system...")
            self.sensorManager.stopManager()
            self.systemPerfManager.stopManager()
            
            # Final metrics log
            self.log_metrics()
            logging.info("System test completed.")
            logging.info("Final metrics - System perf samples: %d, Sensor samples: %d, Actuator events: %d",
                        self.system_perf_samples, self.sensor_samples, self.actuator_events)

def main():
    test = SystemTest()
    test.run_test()

if __name__ == "__main__":
    main() 