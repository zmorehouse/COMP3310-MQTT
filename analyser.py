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

messageTotal = 0

combination_number = 0

def publish_message(topic, message):
    global analyser_qos, maximum_brokers, received_messages, dropped_messages
    publish.single(topic, payload=message, hostname=common.host, port=common.port, qos=2)


def on_message(client, userdata, message):
    global messageTotal

    if message.topic.startswith("counter/"): # We know its not a system message
        messageTotal += 1
    else: # It must be a system message
        if message.topic == "$SYS/broker/clients/maximum":
            maximum_brokers = message.payload.decode()
        elif message.topic == "$SYS/broker/publish/messages/received":
            received_messages = message.payload.decode()
        elif message.topic == "$SYS/broker/publish/messages/dropped":
            dropped_messages = message.payload.decode()


def publish_values():
    global combination_number, analyser_qos
    for instance_count in instance_counts:
        for delay in delays:
            for qos in qos_levels:
                # Publish Changes
                publish_message("request/qos", str(qos))
                publish_message("request/delay", str(delay))
                publish_message("request/instancecount", str(instance_count))
                print("Values published successfully.")
                combination_number += 1 
                for i in range(1, instance_count+1):
                    mqttc.subscribe(f"counter/{i}/{qos}/{delay}", qos=analyser_qos)
                    print(f"Subscribed to counter/{i}/{qos}/{delay}.") 
                
                # Wait for 15 seconds
                time.sleep(15)  
                print(f'Number of messages {messageTotal}')
                
                mqttc.subscribe(f"$SYS/broker/clients/maximum", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/received", qos=analyser_qos)
                mqttc.subscribe(f"$SYS/broker/publish/messages/dropped", qos=analyser_qos)
                time.sleep(5)
                system_info()

                calculate_statistics()

    print(f'All values published at qos: {analyser_qos}')


def system_info():
    global combination_number, maximum_brokers, received_messages, dropped_messages
    if not os.path.exists('sys_log.csv') or os.stat('sys_log.csv').st_size == 0:
        with open('sys_log.csv', 'w') as file:
            file.write("No,MaxBrokers,RecievedMessages,DroppedMessages\n")
        log_entry = pd.DataFrame({'No':[combination_number], 'MaxBrokers': [maximum_brokers], 'RecievedMessages': [received_messages], 'DroppedMessages': [dropped_messages]})
        log_entry.to_csv('sys_log.csv', mode='a', header=False, index=False)
    else:
        log_entry = pd.DataFrame({'No':[combination_number], 'MaxBrokers': [maximum_brokers], 'RecievedMessages': [received_messages], 'DroppedMessages': [dropped_messages]})
        log_entry.to_csv('sys_log.csv', mode='a', header=False, index=False)

def calculate_statistics():
    global combination_number
    msgsaSecond = messageTotal / 10
    print(f'Average Rate of Number of messages: {msgsaSecond}')

    if not os.path.exists('analyser_log.csv') or os.stat('analyser_log.csv').st_size == 0:
        with open('analyser_log.csv', 'w') as file:
            file.write("No,Messages\n")
        log_entry = pd.DataFrame({'No':[combination_number], 'Messages': [messageTotal]})
        log_entry.to_csv('analyser_log.csv', mode='a', header=False, index=False)
    else:
        log_entry = pd.DataFrame({'No':[combination_number], 'Messages': [messageTotal]})
        log_entry.to_csv('analyser_log.csv', mode='a', header=False, index=False)


if __name__ =='__main__':
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(common.host, common.port, 60)
    mqttc.on_message = on_message
    mqttc.loop_forever()

    analyser_qos = 0
    while analyser_qos < 3:
        publish_values()
        analyser_qos += 1
    print('All values published successfully.')