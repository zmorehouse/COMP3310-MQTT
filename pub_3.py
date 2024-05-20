'''
COMP3310 - A3 - MQTT Analysis Assignment
Zac Morehouse | u7637337 

Publisher Script (Number 3) for MQTT Testing Suite

This script is designed to simulate an MQTT publisher as part of a testing suite 
to evaluate the performance of an MQTT broker. The script listens for configuration 
requests to set QoS levels, message delay, and instance count. It then publishes 
messages at specified intervals for a set duration and logs the results to a CSV file.

Libraries Used:
- common: Locally defined module for shared variables
- time: To keep track of time delays
- os and csv: To write to a csv file
- paho : MQTT library for Python for publishing and subscribing to a broker
'''

import common
import time
import os
import csv
import paho.mqtt.client as mqtt

# Define publisher number
pub_number = 3

# Initialize global variables
qos = 0
delay = 0
instance_count = 1
tracker = 0
analyser_qos = -1 # Begin at -1 so that, when the program sees 1/0/0, it will increment to 0
comparison = 0

# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, reason_code, properties):
    global pub_number, comparison
    # Subscribe to necessary request topics
    client.subscribe("request/qos")
    client.subscribe("request/delay")
    client.subscribe("request/instancecount")
    print(f"Pub_{pub_number} connected to the server with reason code : {reason_code}")

# Callback function for when a message is received
def on_message(client, userdata, message):
    global tracker, qos, delay, instance_count, pub_number, analyser_qos
    
    # Update variables based on the topic of the message
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
    
    # Once all parameters are received, start publishing
    if tracker == 3:
        if qos == 0 and delay == 0 and instance_count == 1:
            analyser_qos += 1
        if pub_number <= comparison:
            publish_counter(client, comparison, analyser_qos)
            tracker = 0
        else:
            tracker = 0

# Function to publish counter messages to the broker
def publish_counter(client, comparison, analyser_qos):
    global qos, delay, instance_count, tracker, pub_number
    topic = f"counter/{pub_number}/{qos}/{delay}"
    print('Publishing to topic', topic)
    start_time = time.time()
    counter = 0

    # Publish messages at specified intervals for the test duration
    while time.time() < start_time + common.duration:
        counter += 1
        client.publish(topic, str(counter), qos=qos)
        time.sleep(delay / 1000) # Delay in milliseconds

    # Log the results if the current instance is the latest one
    if pub_number == comparison:
        logger(counter, topic, analyser_qos)

# Function to log the results to a CSV file
def logger(counter, topic, analyser_qos):
    # Define the log entry
    log_entry = {
        'Counter': counter,
        'Topic': topic,
        'Analyser QoS': analyser_qos
    }

    # Check if the CSV file exists and if it's empty
    file_exists = os.path.exists('publisher_log.csv')
    file_is_empty = os.stat('publisher_log.csv').st_size == 0 if file_exists else True

    # Write to the log file
    with open('publisher_log.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Counter", "Topic", "Analyser QoS"])
        
        # Write the header only if the file is new or empty
        if file_is_empty:
            writer.writeheader()
        
        # Write the log entry
        writer.writerow(log_entry)

# Main script execution
if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(common.host, common.port, 60)
    client.loop_forever()
