import paho.mqtt.publish as publish
import time

host = "localhost"
port = 1883
analyser_qos = 0

# Predefined lists for instance count, delay, and qos
instance_counts = [1, 2, 3, 4, 5]
delays = [0, 1, 2, 4]
qos_levels = [0, 1, 2]

# Function to publish a message to the specified topic
def publish_message(topic, message):
    publish.single(topic, payload=message, hostname=host, port=port)
    print(f"Published: {message} to topic: {topic}")

# Function to publish values with a delay of 60 seconds between each iteration
def analyser():
    global analyser_qos
    while analyser_qos < 3:
        publish_values()
        analyser_qos += 1
    print('All values published successfully.')

def publish_values():
    global analyser_qos
    for instance_count in instance_counts:
            for delay in delays:
                for qos in qos_levels:
                    publish_message("request/qos", str(qos))
                    publish_message("request/delay", str(delay))
                    publish_message("request/instancecount", str(instance_count))
                    print("Values published successfully.")
                    time.sleep(2) 
    print(f'All values published at qos: {analyser_qos}')
    


analyser()
