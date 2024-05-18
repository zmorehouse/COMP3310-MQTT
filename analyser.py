import common
import time
import os
import pandas as pd
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

# Predefined values for instance count, delay, and qos
instance_counts = [1,2,3,4,5]
delays = [0, 1, 2, 4]
qos_levels = [0, 1, 2]

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

combination_number = 0

def publish_message(topic, message):
    global analyser_qos, received_messages, dropped_messages
    publish.single(topic, payload=message, hostname=common.host, port=common.port, qos=2)


def on_message(client, userdata, message):
    global messageTotal, numberOfMessages, outoforderMessages, lastMessageCount, lastMessageTime, timeTracker, received_messages, dropped_messages, total_received_messages, total_dropped_messages, startValues

    if message.topic.startswith("counter/"): # We know its not a system message
        messageTotal += 1

        currentMessageCount = int(message.payload)
        currentTime = time.time()
        
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

    
    elif startValues == False:
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

def publish_values():
    global combination_number, analyser_qos, messageTotal, numberOfMessages, outoforderMessages, lastMessageCount, lastMessageTime, timeTracker, received_messages, dropped_messages
    for instance_count in instance_counts:
        for delay in delays:
            for qos in qos_levels:
                # Publish Changes
                publish_message("request/qos", str(qos))
                publish_message("request/delay", str(delay))
                publish_message("request/instancecount", str(instance_count))
                print("Values published successfully.")
                combination_number += 1 
                mqttc.subscribe(f"counter/{instance_count}/{qos}/{delay}", qos=analyser_qos)
                current_topic = f"counter/{instance_count}/{qos}/{delay}"

                time.sleep(common.duration + 5)  
                calculate_statistics(current_topic)
                time.sleep(5)

                mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)
                time.sleep(5)
                system_info(current_topic, instance_count)

                mqttc.unsubscribe(f"counter/{instance_count}/{qos}/{delay}")
                mqttc.unsubscribe(f"$SYS/broker/publish/messages/received")
                mqttc.unsubscribe(f"$SYS/broker/publish/messages/dropped")

                messageTotal = 0
                numberOfMessages = 0
                outoforderMessages = 0
                timeTracker = []
                lastMessageTime = None
                lastMessageCount = 0

    print(f'All values published at qos: {analyser_qos}')


def system_info(current_topic, instance_count):
    global received_messages, dropped_messages, numberOfMessages, outoforderMessages, timeTracker, analyser_qos 
    sys_msgs_a_second = round(((received_messages / instance_count) / common.duration), 2)
    sys_dropped_msgs = round((dropped_messages / received_messages) * 100, 2)
        



    if not os.path.exists('sys_log.csv') or os.stat('sys_log.csv').st_size == 0:
        with open('sys_log.csv', 'w') as file:  # Create an empty file
            file.write("Topic,Messages Received,Messages Dropped\n")
        log_entry = pd.DataFrame({'Topic': [current_topic], 'Messages Received / sec': [sys_msgs_a_second], 'Messages Dropped %': [sys_dropped_msgs]})
        log_entry.to_csv('sys_log.csv', mode='a', header=False, index=False)
    else:
        log_entry = pd.DataFrame({'Topic': [current_topic], 'Messages Received / sec': [sys_msgs_a_second], 'Messages Dropped %': [sys_dropped_msgs]})
        log_entry.to_csv('sys_log.csv', mode='a', header=False, index=False)


def calculate_statistics(current_topic):
    global numberOfMessages, outoforderMessages, timeTracker, analyser_qos
    if outoforderMessages != 0 or numberOfMessages != 0:
        outoforderMessagespercentage = round(outoforderMessages / numberOfMessages * 100, 3)
    else:
        outoforderMessagespercentage = 0

    if numberOfMessages != 0:
        msgsaSecond = round(numberOfMessages / common.duration, 3)
    else:
        msgsaSecond = 0

    if len(timeTracker) != 0:
        median_intermessage_gap = round(sum(timeTracker) / len(timeTracker), 3)
    else:
        median_intermessage_gap = 0

    if not os.path.exists('analyser_log.csv') or os.stat('analyser_log.csv').st_size == 0:
        with open('analyser_log.csv', 'w') as file:  # Create an empty file
            file.write("Messages Received,Out of Order Messages,Messages per Second,Median Intermessage Gap, Topic, Analyser QoS\n")
        log_entry = pd.DataFrame({'Messages Received': [numberOfMessages], 'Out of Order Messages': [outoforderMessagespercentage], 'Messages per Second': [msgsaSecond], 'Median Intermessage Gap': [median_intermessage_gap], 'Topic' : [current_topic], 'Analyser QoS': [analyser_qos]})
        log_entry.to_csv('analyser_log.csv', mode='a', header=False, index=False)
    else:
        log_entry = pd.DataFrame({'Messages Received': [numberOfMessages], 'Out of Order Messages': [outoforderMessagespercentage], 'Messages per Second': [msgsaSecond], 'Median Intermessage Gap': [median_intermessage_gap], 'Topic' : [current_topic], 'Analyser QoS': [analyser_qos]})
        log_entry.to_csv('analyser_log.csv', mode='a', header=False, index=False)

def get_system_stats():
    global total_received_messages, total_dropped_messages, startValues
    mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
    mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)
    time.sleep(10)
    print(f'Initial number of messages received (previous runs): {total_received_messages}')
    print(f'Initial number of messages dropped (previous runs): {total_dropped_messages}')
    startValues = True


if __name__ =='__main__':
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(common.host, common.port, 60)
    mqttc.on_message = on_message
    mqttc.loop_start()

    get_system_stats()
    
    analyser_qos = 0
    while analyser_qos < 3:
        publish_values()
        analyser_qos += 1
    print('All values published successfully.')