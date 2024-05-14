import common

import time
import os
import pandas as pd
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

# Predefined values for instance count, delay, and qos
instance_counts = [1, 2, 3, 4, 5]
delays = [0, 1, 2, 4]
qos_levels = [0, 1, 2]

analyser_qos = 0

messageTotal = 0
numberOfMessages = 0
outoforderMessages = 0
lastMessageCount = 0
lastMessageTime = None
timeTracker = []


currentTopic = ''
maximum_brokers = ''
received_messages = ''
dropped_messages = ''

startValues = False

combination_number = 0

def publish_message(topic, message):
    global analyser_qos, maximum_brokers, received_messages, dropped_messages
    publish.single(topic, payload=message, hostname=common.host, port=common.port, qos=2)


def on_message(client, userdata, message):
    global messageTotal, numberOfMessages, outoforderMessages, lastMessageCount, lastMessageTime, timeTracker, maximum_brokers, received_messages, dropped_messages

    if message.topic.startswith("counter/"): # We know its not a system message
        messageTotal += 1

        currentMessageCount = int(message.payload)
        currentTime = time.time()
        
        if currentMessageCount != lastMessageCount + 1:
            outoforderMessages += 1
        lastMessageCount = currentMessageCount

        if lastMessageTime is not None:
            # Calculate the time difference in milliseconds
            timeDiff_ms = (currentTime - lastMessageTime) * 1000
            timeTracker.append(timeDiff_ms)
        lastMessageTime = currentTime
    
        numberOfMessages += 1
    elif startValues == False:
        if message.topic == "$SYS/broker/clients/maximum":
            maximum_brokers = 0
        elif message.topic == "$SYS/broker/publish/messages/received":
            received_messages = message.payload.decode()
        elif message.topic == "$SYS/broker/publish/messages/dropped":
            dropped_messages = message.payload.decode()
    
    else: 
        if message.topic == "$SYS/broker/clients/maximum":
            maximum_brokers = message.payload.decode()
        elif message.topic == "$SYS/broker/publish/messages/received":
            received_messages = message.payload.decode()
        elif message.topic == "$SYS/broker/publish/messages/dropped":
            dropped_messages = message.payload.decode()

def publish_values():
    global combination_number, analyser_qos, messageTotal, numberOfMessages, outoforderMessages, lastMessageCount, lastMessageTime, timeTracker, maximum_brokers, received_messages, dropped_messages
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
                print(f"Subscribed to counter/{instance_count}/{qos}/{delay}.") 
                
                # Wait for 15 seconds
                time.sleep(common.duration + 5)  
                print(f'Number of messages {messageTotal}')
                
                mqttc.subscribe(f"$SYS/broker/clients/maximum", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)
                time.sleep(5)
                system_info()

                calculate_statistics()

                #Reset All
                mqttc.unsubscribe(f"counter/{instance_count}/{qos}/{delay}")
                mqttc.unsubscribe(f"$SYS/broker/clients/maximum")
                mqttc.unsubscribe(f"$SYS/broker/publish/messages/received")
                mqttc.unsubscribe(f"$SYS/broker/publish/messages/dropped")

                messageTotal = 0
                numberOfMessages = 0
                outoforderMessages = 0
                timeTracker = []
                lastMessageTime = None
                lastMessageCount = 0

    print(f'All values published at qos: {analyser_qos}')


def system_info():
    print('System Statistics')

def calculate_statistics():
    global currentTopic, numberOfMessages, outoforderMessages, timeTracker, analyser_qos

    if outoforderMessages != 0 or numberOfMessages != 0:
        outoforderMessagespercentage = outoforderMessages / numberOfMessages * 100
    else:
        outoforderMessagespercentage = 0
    if numberOfMessages != 0:
        msgsaSecond = numberOfMessages / 10
    else:
        msgsaSecond = 0
    if len(timeTracker) != 0:
        median_intermessage_gap = sum(timeTracker) / len(timeTracker)
    else:
        median_intermessage_gap = 0

    print(f'Out of order message%: {outoforderMessagespercentage}%')
    print(f'Messages per second: {msgsaSecond}')
    print(f'Median intermessage gap: {median_intermessage_gap}ms')

    if not os.path.exists('analyser_log.csv'):
        open('analyser_log.csv', 'w').close()  # Create an empty file
    log_entry = pd.DataFrame({'Mesages Recieved': [numberOfMessages], 'Out of Order Messages': [outoforderMessages], 'Messages per Second': [msgsaSecond], 'Median Intermessage Gap': [median_intermessage_gap], 'Topic' : [currentTopic], 'Analyser QoS': [analyser_qos]})
    log_entry.to_csv('analyser_log.csv', mode='a', header=False, index=False)

def get_system_stats():
    global maximum_brokers, received_messages, dropped_messages
    mqttc.subscribe(f"$SYS/broker/clients/maximum", qos=analyser_qos)
    mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
    mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)
    time.sleep(10)
    print(f'Maximum number of brokers: {maximum_brokers}')
    print(f'Number of messages received: {received_messages}')
    print(f'Number of messages dropped: {dropped_messages}')


if __name__ =='__main__':
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(common.host, common.port, 60)
    mqttc.on_message = on_message
    mqttc.loop_start()

    get_system_stats()
    startValues = True
    analyser_qos = 0
    while analyser_qos < 3:
        publish_values()
        analyser_qos += 1
    print('All values published successfully.')