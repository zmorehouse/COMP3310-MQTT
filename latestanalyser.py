import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import os
import pandas as pd

host = "localhost"
port = 1883
analyser_qos = 0
numberOfMessages = 0
outoforderMessages = 0
lastMessageCount = 0
duration = 15
lastMessageTime = None
timeTracker = []
currentTopic = ''
maximum_brokers = ''
received_messages = ''
dropped_messages = ''

# Predefined values for instance count, delay, and qos
instance_counts = [1, 2, 3, 4, 5]
delays = [0, 1, 2, 4]
qos_levels = [0, 1, 2]

# Function to publish a message to the specified topic
def publish_message(topic, message):
    global analyser_qos
    publish.single(topic, payload=message, hostname=host, port=port, qos=2)
    print(f"Published: {message} to topic: {topic} at qos: {analyser_qos}")

def on_message(client, userdata, message):
    global numberOfMessages, outoforderMessages, lastMessageCount,lastMessageTime, timeTracker, maximum_brokers, received_messages, dropped_messages

    if message.topic.startswith("counter"):
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
        # If previous message has a higher counter or not previous counter to this +1 to message loss
    '''
        else:
        if message.topic == "$SYS/broker/clients/maximum":
            maximum_brokers = message.payload.decode()
            print(f'SYS MAX BROKERS: {maximum_brokers}')
        elif message.topic == "$SYS/broker/publish/messages/received":
            received_messages = message.payload.decode()
            print(f'SYS RECEIVED MESSAGES: {received_messages}')
        elif message.topic == "$SYS/broker/publish/messages/dropped":
            dropped_messages = message.payload.decode()
            print(f'SYS DROPPED MESSAGES: {dropped_messages}')
    '''

                

def publish_values():
    global analyser_qos, numberOfMessages, outoforderMessages, lastMessageCount, lastMessageTime, timeTracker, currentTopic
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(host, port, 60)
    mqttc.on_message = on_message
    mqttc.loop_start()

    for instance_count in instance_counts:
        for delay in delays:
            for qos in qos_levels:
                # Publish Changes
                publish_message("request/qos", str(qos))
                publish_message("request/delay", str(delay))
                publish_message("request/instancecount", str(instance_count))
                print("Values published successfully.")
                currentTopic = f"counter/{instance_count}/{qos}/{delay}"
                # Subscribe to ALL counters to track
                for i in range(1, instance_count+1):
                    mqttc.subscribe(f"counter/{i}/{qos}/{delay}", qos=analyser_qos)
                    print(f"Subscribed to counter/{i}/{qos}/{delay}.") 
                
                time.sleep(duration)  # Wait
                print(f'Number of messages {numberOfMessages}') # Print total number of messages
                '''
                mqttc.subscribe(f"$SYS/broker/clients/maximum", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)

                '''
    '''
            if message.topic.startswith("counter/1"):
            pub1_Message = int(message.payload)

            # Out Of Order Increment
            if pub1_Message != pub1_LastMessage + 1:
                outoforderMessages += 1
            pub1_LastMessage = pub1_Message

            currentTime = time.time()
            # Average Time Calculation
            if lastMessageTime is not None:
                timeDiff_ms = (currentTime - lastMessageTime) * 1000
                timeTracker.append(timeDiff_ms)
            lastMessageTime = currentTime
    '''
            calculate_statistics()

            # Reset values
                # mqttc.unsubscribe('$SYS#')
                numberOfMessages = 0
                outoforderMessages = 0
                timeTracker = []
                lastMessageTime = None
                lastMessageCount = 0

    print(f'All values published at qos: {analyser_qos}')


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

if __name__ =='__main__':
    while analyser_qos < 3:
        publish_values()
        analyser_qos += 1
    print('All values published successfully.')