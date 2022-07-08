# mqtt-bed config

BED_ADDRESS = "DC:BB:48:42:D9:3E"

MQTT_USERNAME = "mqttbed"
MQTT_PASSWORD = "mqtt-bed"
MQTT_SERVER = "10.0.0.3"
MQTT_SERVER_PORT = 1883
MQTT_TOPIC = "bed"

# Bed controller type, supported values are "serta", "jiecang", "lucid", and "dewertokin"
BED_TYPE = "lucid"

# Don't worry about these unless you want to
MQTT_CHECKIN_TOPIC = "checkIn/bed"
MQTT_CHECKIN_PAYLOAD = "OK"
MQTT_ONLINE_PAYLOAD = "online"
MQTT_QOS = 0

# Extra debug messages
DEBUG = 1
