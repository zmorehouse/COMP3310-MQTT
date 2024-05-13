import os
import time
import threading
import paho.mqtt.client as mqtt
import pandas as pd

host = "localhost"
port = 1883

qos = 0
delay = 0
instance_count = 1
tracker = 0

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("request/qos")
    client.subscribe("request/delay")
    client.subscribe("request/instancecount")

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
        tracker += 1
    if tracker == 3:
        publish_counter(client)
        tracker = 0

def publish_counter(client):
    global qos, delay
    topic = f"counter/{instance_count}/{qos}/{delay}"

    start_time = time.time()
    duration = 10

    counter = 0
    while time.time() < start_time + duration:
        counter += 1
        client.publish(topic, str(counter), qos=qos)
        time.sleep(delay / 1000)  # Delay in milliseconds
    logger(counter, topic)
    
def logger(counter, topic):
    if not os.path.exists('publisher_log.csv'):
        open('publisher_log.csv', 'w').close() 
        
    log_entry = pd.DataFrame({'Counter': [counter], 'Topic': [topic]})
    log_entry.to_csv('publisher_log.csv', mode='a', header=False, index=False)

def publish_sequence(publisher_number):
    global thread_publisher_number
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect(host, port, 60)
    mqttc.loop_forever()

    # Set the publisher number for this thread
    thread_publisher_number = publisher_number

# Create and start 5 threads with unique publisher numbers
threads = []
for i in range(5):
    publisher_number = i + 1  # Publisher numbers start from 1
    t = threading.Thread(target=publish_sequence, args=(publisher_number,))
    threads.append(t)
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()