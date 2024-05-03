import paho.mqtt.client as mqtt
import time

host = "localhost"
port = 1883

instance = 1
qos = 1
delay = 4  
topic = f"counter/{instance}/{qos}/{delay}"

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

def publish_sequence(client, topic):
    counter = 0
    while counter < 10:
        message = str(counter)
        client.publish(topic, message, qos=2)
        counter += 1
        time.sleep(delay / 1000) 

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect

mqttc.connect(host, port, 60)
print("Connected to broker.")

publish_sequence(mqttc, topic)
print("Finished publishing message sequence.")

mqttc.loop_forever()
