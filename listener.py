import paho.mqtt.client as mqtt
import time

host = "localhost"
port = 1883
numberOfMessage = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}.")
    client.subscribe("counter/1/1/1")

def on_message(client, userdata, message):
    global numberOfMessage
    print(f"Received message: {message.payload.decode()} on topic: {message.topic}")
    numberOfMessage += 1
    print(numberOfMessage)

def publish_sequence():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(host, port, 60)
    mqttc.loop_forever()

publish_sequence()