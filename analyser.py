''' 
Analyser Script for MQTT Testing Suite

This script is designed to simulate an MQTT analyser as part of a testing suite 
to evaluate the performance of an MQTT broker. It configures the publishers, 
listens for messages, and logs various statistics such as message order, 
inter-message gaps, and system performance metrics.

Libraries Used:
- common: Locally defined script for shared variables
- time: To keep track of time delays
- os and csv: To write to a csv file
- paho : MQTT library for Python for publishing and subscribing to a broker
'''

import common
import time
import os
import csv
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

# Predefined values for instance count, delay, and qos. These are our test criteria
instance_counts = [1, 2, 3, 4, 5]
delays = [0, 1, 2, 4]
qos_levels = [0, 1, 2]

# Initialize global variables
analyser_qos = 0
messageTotal = 0
numberOfMessages = 0
outoforderMessages = 0
lastMessageCount = 0
lastMessageTime = None
timeTracker = []
total_received_messages = 0
total_dropped_messages = 0
received_messages = 0
dropped_messages = 0
startValues = False

# Function to publish a message to a topic. This is used to send configuration values to the publishers
def publish_message(topic, message):
    global analyser_qos, received_messages, dropped_messages
    publish.single(topic, payload=message, hostname=common.host, port=common.port, qos=2)

# Callback for when a message is received
def on_message(client, userdata, message):
    global messageTotal, numberOfMessages, outoforderMessages, lastMessageCount, lastMessageTime, timeTracker, received_messages, dropped_messages, total_received_messages, total_dropped_messages, startValues

    # Check if the message is a counter message and process it
    if message.topic.startswith("counter/"):  
        messageTotal += 1
        currentMessageCount = int(message.payload)
        currentTime = time.time()
        
        # Check if the message is out of order. If it is, add it to the out of order messages count and do not calculate the median time difference
        if currentMessageCount != lastMessageCount + 1:
            outoforderMessages += 1
            lastMessageTime = currentTime
        else:
            if lastMessageTime is not None:
                timeDiff_ms = (currentTime - lastMessageTime) * 1000
                timeTracker.append(timeDiff_ms)
            lastMessageTime = currentTime
        lastMessageCount = currentMessageCount
    
        numberOfMessages += 1

    # If the initial system statistics exist already, calculate and update the variables. If not, assign. 
    elif not startValues:
        if message.topic == "$SYS/broker/publish/messages/received":
            total_received_messages = int(message.payload.decode())
        elif message.topic == "$SYS/broker/publish/messages/dropped":
            total_dropped_messages = int(message.payload.decode())
    
    else: 
        if message.topic == "$SYS/broker/publish/messages/received":
            received_messages = int(message.payload.decode()) - total_received_messages
            total_received_messages = int(message.payload.decode())
        elif message.topic == "$SYS/broker/publish/messages/dropped":
            dropped_messages = int(message.payload.decode()) - total_dropped_messages
            total_dropped_messages = int(message.payload.decode())

# Function to publish configuration values and run tests
def publish_values():
    global analyser_qos, messageTotal, numberOfMessages, outoforderMessages, lastMessageCount, lastMessageTime, timeTracker, received_messages, dropped_messages
    # Loop through all test combinations
    for instance_count in instance_counts:
        for delay in delays:
            for qos in qos_levels:
                # Publish New Values
                publish_message("request/qos", str(qos))
                publish_message("request/delay", str(delay))
                publish_message("request/instancecount", str(instance_count))
                print("Test values published successfully." + f" QoS: {qos}, Delay: {delay}, Instance Count: {instance_count}, Analyser QoS: {analyser_qos}")

                # Once published, subscribe to the topic and wait for the publisher messages to arrive
                mqttc.subscribe(f"counter/{instance_count}/{qos}/{delay}", qos=analyser_qos)
                current_topic = f"counter/{instance_count}/{qos}/{delay}"

                time.sleep(common.duration + 5) # Sleep for the duration of the sent messages (plus buffer room)
                calculate_statistics(current_topic) # Calculate and log statistics

                # Subscriber to system statistics, calculate and log their values
                mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)
                time.sleep(5) # Sleep for 5 seconds to allow the system statistics to be received
                system_info(current_topic, instance_count)

                # Unsubscribe from all topics
                mqttc.unsubscribe(f"counter/{instance_count}/{qos}/{delay}")
                mqttc.unsubscribe(f"$SYS/broker/publish/messages/received")
                mqttc.unsubscribe(f"$SYS/broker/publish/messages/dropped")

                # Reset variables for the next test
                messageTotal = 0
                numberOfMessages = 0
                outoforderMessages = 0
                timeTracker = []
                lastMessageTime = None
                lastMessageCount = 0

    print(f'All values published at qos: {analyser_qos}') # Print a message to indicate that all values have been published at a specific QoS

# Function to log system information to a CSV file
def system_info(current_topic, instance_count):
    global received_messages, dropped_messages, numberOfMessages, outoforderMessages, timeTracker, analyser_qos 

    sys_msgs_a_second = round(((received_messages / instance_count) / common.duration), 2) # Calculate messages received per second
    sys_dropped_msgs = round((dropped_messages / received_messages) * 100, 2) # Calculate percentage of dropped messages
        
    # Define the CSV log
    log_entry = {
        'Topic': current_topic,
        'Messages Received / sec': sys_msgs_a_second,
        'Messages Dropped %': sys_dropped_msgs
    }

    # Check if the CSV file exists and if it's empty
    file_exists = os.path.exists('sys_log.csv')
    file_is_empty = os.stat('sys_log.csv').st_size == 0 if file_exists else True

    # Write to the log file
    with open('sys_log.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Topic", "Messages Received / sec", "Messages Dropped %"])
    
        # Write the header only if the file is new or empty
        if file_is_empty:
            writer.writeheader()
        
        # Write the log entry
        writer.writerow(log_entry)

def calculate_statistics(current_topic):
    global numberOfMessages, outoforderMessages, timeTracker, analyser_qos

    # Calculate out of order message %
    if outoforderMessages != 0 or numberOfMessages != 0:
        outoforderMessagespercentage = round(outoforderMessages / numberOfMessages * 100, 3)
    else:
        outoforderMessagespercentage = 0

    # Calculate messages per second
    if numberOfMessages != 0:
        msgsaSecond = round(numberOfMessages / common.duration, 3)
    else:
        msgsaSecond = 0

    # Calculate median intermessage gap
    if len(timeTracker) != 0:
        median_intermessage_gap = round(sum(timeTracker) / len(timeTracker), 3)
    else:
        median_intermessage_gap = 0

    # Define the log entry
    log_entry = {
        'Messages Received': numberOfMessages,
        'Out of Order Messages': outoforderMessagespercentage,
        'Messages per Second': msgsaSecond,
        'Median Intermessage Gap': median_intermessage_gap,
        'Topic': current_topic,
        'Analyser QoS': analyser_qos
    }

    # Check if the CSV file exists and if it's empty
    file_exists = os.path.exists('analyser_log.csv')
    file_is_empty = os.stat('analyser_log.csv').st_size == 0 if file_exists else True

    # Write to the analyser log file
    with open('analyser_log.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "Messages Received", 
            "Out of Order Messages", 
            "Messages per Second", 
            "Median Intermessage Gap", 
            "Topic", 
            "Analyser QoS"
        ])
        
        # Write the header only if the file is new or empty
        if file_is_empty:
            writer.writeheader()
        
        # Write the log entry
        writer.writerow(log_entry)

# Function to get initial system statistics
def get_system_stats():
    global total_received_messages, total_dropped_messages, startValues
    mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
    mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)
    time.sleep(5) # Sleep for 10 seconds to allow the system statistics to be received
    startValues = True

# Main script execution
if __name__ == '__main__':
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(common.host, common.port, 60)
    mqttc.on_message = on_message
    mqttc.loop_start()
    get_system_stats() # Get initial system statistics
    analyser_qos = 0
    while analyser_qos < 3: # Loop through all QoS levels of analyer qos
        publish_values()
        analyser_qos += 1
    print('All tests published successfully.')
