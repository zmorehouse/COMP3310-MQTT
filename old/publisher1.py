import paho.mqtt.client as mqtt
import time

host = "localhost"
port = 1883

pub_number = 1

qos = 0
delay = 0
instance_count = 1
tracker = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Publisher number {pub_number} connected with result code {reason_code}.")
    client.subscribe("request/qos")
    client.subscribe("request/delay")
    client.subscribe("request/instancecount")
    print("Subscribed to request topics.")

def on_message(client, userdata, message):
    global qos, delay, instance_count, tracker
    print(f"Received message: {message.payload.decode()} on topic: {message.topic}")

    if message.topic == "request/qos":
        qos = int(message.payload)
        tracker += 1
    elif message.topic == "request/delay":
        delay = int(message.payload)
        tracker += 1
    elif message.topic == "request/instancecount":
        instance_count = int(message.payload)
        comparison = int(message.payload)
        tracker += 1
    if tracker == 3:
        if pub_number <= comparison:

            publish_counter(client)
            tracker = 0
        else:
            print('Instance count is not high enough, ignoring.')
            tracker = 0
    

def publish_counter(client):
    global qos, delay, instance_count, tracker, pub_number
    topic = f"counter/{pub_number}/{qos}/{delay}"
    print(f"Publishing to counter/{pub_number}/{qos}/{delay}")

    start_time = time.time()
    duration = 5

    counter = 0
    while time.time() < start_time + duration:
        counter += 1
        client.publish(topic, str(counter), qos=qos)
        print(f"Published: {counter} to topic: {topic}")
        time.sleep(delay / 1000)  # Delay in milliseconds

    tracker = 0

def publish_sequence():
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(host, port, 60)
    mqttc.loop_forever()

publish_sequence()
