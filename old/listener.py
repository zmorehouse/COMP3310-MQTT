import paho.mqtt.client as mqtt
import time

host = "broker.emqx.io"
port = 1883
numberOfMessage = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}.")
    client.publish("/zac/comp3310", 'Testing QoS', qos=2)



def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic: {message.topic}")
    print(numberOfMessage)

def publish_sequence():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(host, port, 60)
    mqttc.loop_forever()

publish_sequence()