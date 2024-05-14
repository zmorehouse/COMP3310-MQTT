import common

import time
import os
import pandas as pd
import paho.mqtt.client as mqtt

pub_number = 4

qos = 0
delay = 0
instance_count = 1
tracker = 0
combination_number = 0

comparison = 0
def on_connect(client, userdata, flags, reason_code, properties):
    global pub_number, comparison
    client.subscribe("request/qos")
    client.subscribe("request/delay")
    client.subscribe("request/instancecount")
    print(f"Pub_{pub_number} connected to the server.")

def on_message(client, userdata, message):
    global tracker, qos, delay, instance_count, pub_number, combination_number
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
        combination_number += 1
        if pub_number <= comparison:
            publish_counter(client, comparison)
            tracker = 0
        else:
            tracker = 0

def publish_counter(client, comparison):
    global qos, delay, instance_count, tracker, pub_number, combination_number
    topic = f"counter/{pub_number}/{qos}/{delay}"
    print('Publishing to topic', topic)
    start_time = time.time()

    counter = 0

    while time.time() < start_time + common.duration:
        counter += 1
        client.publish(topic, str(counter), qos=qos)
        time.sleep(delay / 1000) 

    if pub_number == comparison:
        logger(combination_number, counter, topic)

def logger(combination_number, counter, topic):
    if not os.path.exists('publisher_log.csv') or os.stat('publisher_log.csv').st_size == 0:
        with open('publisher_log.csv', 'w') as file:
            file.write("No,Counter,Topic\n")
        log_entry = pd.DataFrame({'No':[combination_number], 'Counter': [counter], 'Topic': [topic]})
        log_entry.to_csv('publisher_log.csv', mode='a', header=False, index=False)
    else:
        log_entry = pd.DataFrame({'No':[combination_number], 'Counter': [counter], 'Topic': [topic]})
        log_entry.to_csv('publisher_log.csv', mode='a', header=False, index=False)


if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(common.host, common.port, 60)
    client.loop_forever()