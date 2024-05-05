import paho.mqtt.client as mqtt
import time

host = "localhost"
port = 1883

qos = 1
delay = 4
instance_count = 5

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("request/qos")
    client.subscribe("request/delay")
    client.subscribe("request/instancecount")
    print("Subscribed to request topics.")

def on_message(client, userdata, message):
    global qos, delay, instance_count
    print(f"Received message: {message.payload.decode()} on topic: {message.topic}")
    if message.topic == "request/qos":
        qos = int(message.payload)
        print(f"QoS set to {qos}")
    elif message.topic == "request/delay":
        delay = int(message.payload)
        print(f"Delay set to {delay}ms")
    elif message.topic == "request/instancecount":
        instance_count = int(message.payload)
        print(f"Instance count set to {instance_count}")

def publish_sequence():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(host, port, 60)
    mqttc.loop_forever()

publish_sequence()
