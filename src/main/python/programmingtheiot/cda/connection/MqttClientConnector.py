#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import ssl
import paho.mqtt.client as mqttClient
import json

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient

from programmingtheiot.data.DataUtil import DataUtil

class MqttClientConnector(IPubSubClient):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, clientID: str = None):
		self.config = ConfigUtil()
		self.dataMsgListener = None

		self.host = \
			self.config.getProperty( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)

		self.port = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_MQTT_PORT)

		self.keepAlive = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.KEEP_ALIVE_KEY, ConfigConst.DEFAULT_KEEP_ALIVE)

		self.defaultQos = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.DEFAULT_QOS_KEY, ConfigConst.DEFAULT_QOS)

		self.mqttClient = None

		# Initialize clientID first
		if not clientID:
			self.clientID = self.config.getProperty(
				ConfigConst.CONSTRAINED_DEVICE, ConfigConst.DEVICE_LOCATION_ID_KEY)
		else:
			self.clientID = clientID

		self.enableEncryption = \
			self.config.getBoolean( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.ENABLE_CRYPT_KEY)

		self.pemFileName = \
			self.config.getProperty( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.CERT_FILE_KEY)

		logging.info('\tMQTT Client ID:   %s', self.clientID)
		logging.info('\tMQTT Broker Host: %s', self.host)
		logging.info('\tMQTT Broker Port: %s', str(self.port))
		logging.info('\tMQTT Keep Alive:  %s', str(self.keepAlive))

	def connectClient(self) -> bool:
		if not self.mqttClient:
			# TODO: make clean_session configurable
			self.mqttClient = mqttClient.Client(client_id = self.clientID, clean_session = True)

			try:
				# Get Ubidots token from credentials
				credConfig = ConfigUtil()
				credentials = credConfig.getCredentials(ConfigConst.MQTT_GATEWAY_SERVICE)
				
				if not credentials or "authToken" not in credentials:
					logging.error("No Ubidots token found in credentials")
					return False
				
				self.ubidotsToken = credentials["authToken"]
				
				# Set username and password for Ubidots
				self.mqttClient.username_pw_set(self.ubidotsToken, password="")
				
				# Always use secure port for Ubidots
				self.port = 8883
				
				# Enable TLS
				self.mqttClient.tls_set(tls_version = ssl.PROTOCOL_TLS_CLIENT)
				self.mqttClient.tls_insecure_set(True)  # Required for Ubidots
				
				# Set reconnection parameters
				self.mqttClient.reconnect_delay_set(min_delay=1, max_delay=60)
				self.keepAlive = 120  # Increase keep-alive to 2 minutes
				
				# Set connection flags
				self.mqttClient.max_inflight_messages_set(20)  # Allow up to 20 messages in flight
				self.mqttClient.max_queued_messages_set(100)   # Queue up to 100 messages
				
			except Exception as e:
				logging.error("Failed to setup MQTT client: %s", str(e))
				return False

			self.mqttClient.on_connect = self.onConnect
			self.mqttClient.on_disconnect = self.onDisconnect
			self.mqttClient.on_message = self.onMessage
			self.mqttClient.on_publish = self.onPublish
			self.mqttClient.on_subscribe = self.onSubscribe

		if not self.mqttClient.is_connected():
			logging.info('MQTT client connecting to broker at host: %s:%d', self.host, self.port)
			try:
				# Start the network loop before connecting
				self.mqttClient.loop_start()
				
				# Connect with a timeout
				rc = self.mqttClient.connect(self.host, self.port, self.keepAlive)
				if rc != mqttClient.MQTT_ERR_SUCCESS:
					logging.error("Failed to connect to MQTT broker with error code: %d", rc)
					self.mqttClient.loop_stop() # Stop the loop on connection failure
					return False
					
				return True
			except Exception as e:
				logging.error("Failed to connect to MQTT broker: %s", str(e))
				return False
		else:
			logging.warning('MQTT client is already connected. Ignoring connect request.')
			return False
		
	def disconnectClient(self) -> bool:
		if self.mqttClient:
			logging.info('Disconnecting MQTT client from broker: %s', self.host)
			self.mqttClient.loop_stop()
			self.mqttClient.disconnect()
			return True
		logging.warning('MQTT client not initialized. Ignoring disconnect request.')
		return False
		
	def onConnect(self, client, userdata, flags, rc):
		if rc == mqttClient.CONNACK_ACCEPTED:
			logging.info('MQTT client connected to broker: %s', self.host)
			
			# Subscribe to actuator commands
			self.mqttClient.subscribe(
				topic = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value,
				qos = self.defaultQos
			)
			
			self.mqttClient.message_callback_add(
				sub = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value,
				callback = self.onActuatorCommandMessage
			)
		else:
			logging.error('Failed to connect to MQTT broker with return code: %d', rc)
			
	def onDisconnect(self, client, userdata, rc):
		if rc != 0:
			logging.warning('MQTT client disconnected from broker: %s with return code: %d', self.host, rc)
			# Attempt to reconnect
			try:
				self.mqttClient.reconnect()
			except Exception as e:
				logging.error("Failed to reconnect to MQTT broker: %s", str(e))
		else:
			logging.info('MQTT client disconnected from broker: %s', self.host)
		
	def onMessage(self, client, userdata, msg):
		logging.info('Received message on topic: %s', msg.topic)
		if self.dataMsgListener:
			self.dataMsgListener.handleIncomingMessage(ResourceNameEnum(msg.topic), msg.payload.decode())
	
	def onPublish(self, client, userdata, mid):
		logging.info('Message published successfully')
	
	def onSubscribe(self, client, userdata, mid, granted_qos):
		logging.info('MQTT client subscribed to broker: %s', self.host)
	
	def onActuatorCommandMessage(self, client, userdata, msg):
		logging.info('[Callback] Actuator command message received. Topic: %s.', msg.topic)

		if self.dataMsgListener:
			try:
				# assumes all data is encoded using UTF-8 (between GDA and CDA)
				actuatorData = DataUtil().jsonToActuatorData(msg.payload.decode('utf-8'))

				self.dataMsgListener.handleActuatorCommandMessage(actuatorData)
			except:
				logging.exception("Failed to convert incoming actuation command payload to ActuatorData: ")

	def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot publish message.')
			return False

		# check validity of message
		if not msg:
			logging.warning('No message specified. Cannot publish message to topic: %s', resource.value)
			return False

		# check validity of QoS - set to default if necessary
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		# Format message and determine topic for Ubidots
		if resource == ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE:
			try:
				# Parse the sensor data
				sensorData = DataUtil().jsonToSensorData(msg)
				
				# Create Ubidots format
				ubidotsMsg = {
					sensorData.getName().lower(): {
						"value": sensorData.getValue()
					}
				}
				
				# Convert to JSON
				payload = json.dumps(ubidotsMsg)
				
				# Set topic to Ubidots format
				topic = f"/v1.6/devices/{self.clientID}"
				logging.info("Publishing sensor data to Ubidots topic: %s", topic)
			except Exception as e:
				logging.error("Failed to format sensor message for Ubidots: %s", str(e))
				# Fallback to original topic and message if formatting fails
				topic = resource.value
				payload = msg
		elif resource == ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE:
			# For system performance, the JSON is already in a suitable format
			payload = msg
			# Set topic to Ubidots format
			topic = f"/v1.6/devices/{self.clientID}"
			logging.info("Publishing system performance data to Ubidots topic: %s", topic)
		elif resource == ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE:
			try:
				# Parse the actuator data
				actuatorData = DataUtil().jsonToActuatorData(msg)
				
				# Create Ubidots format using actuator name and command
				variable_name = f"{actuatorData.getName().lower()}-{actuatorData.getCommand().lower()}"
				ubidotsMsg = {
					variable_name: {
						"value": actuatorData.getValue()
					}
				}
				
				# Convert to JSON
				payload = json.dumps(ubidotsMsg)
				
				# Set topic to Ubidots format
				topic = f"/v1.6/devices/{self.clientID}"
				logging.info("Publishing actuator response data to Ubidots topic: %s", topic)
			except Exception as e:
				logging.error("Failed to format actuator response message for Ubidots: %s", str(e))
				# Fallback to original topic and message if formatting fails
				topic = resource.value
				payload = msg
		else:
			# For other resource types, use the original topic and message
			topic = resource.value
			payload = msg
			logging.info("Publishing other message to topic: %s", topic)

		# publish message
		try:
			self.mqttClient.publish(topic = topic, payload = payload, qos = qos)
		except Exception as e:
			logging.error("Failed to publish message to topic %s: %s", topic, str(e))
			return False

		return True

	def subscribeToTopic(self, resource: ResourceNameEnum = None, callback = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot subscribe.')
			return False

		# check validity of QoS - set to default if necessary
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		# subscribe to topic
		logging.info('Subscribing to topic %s', resource.value)
		self.mqttClient.subscribe(resource.value, qos)

		return True
	
	def unsubscribeFromTopic(self, resource: ResourceNameEnum = None):
		# check validity of resource (topic)
		if not resource:
			logging.warning('No topic specified. Cannot unsubscribe.')
			return False

		logging.info('Unsubscribing to topic %s', resource.value)
		self.mqttClient.unsubscribe(resource.value)

		return True

	def setDataMessageListener(self, listener: IDataMessageListener = None):
		if listener:
			self.dataMsgListener = listener

	def isClientConnected(self) -> bool:
		"""
		Checks if the MQTT client is currently connected.
		
		@return True if connected, False otherwise.
		"""
		if self.mqttClient:
			return self.mqttClient.is_connected()
		return False
