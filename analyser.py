import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time

host = "localhost"
port = 1883
analyser_qos = 0
numberOfMessage = 0

# Predefined lists for instance count, delay, and qos
instance_counts = [1, 2, 3, 4, 5]
delays = [0, 1, 2, 4]
qos_levels = [0, 1, 2]

# Function to publish a message to the specified topic
def publish_message(topic, message):
    global analyser_qos
    publish.single(topic, payload=message, hostname=host, port=port, qos=analyser_qos)
    print(f"Published: {message} to topic: {topic} at qos: {analyser_qos}")

# Function to handle incoming messages
def on_message(client, userdata, message):
    global numberOfMessage
    numberOfMessage += 1

# Function to publish values with a delay of 60 seconds between each iteration
def analyser():
    global analyser_qos
    while analyser_qos < 3:
        publish_values()
        analyser_qos += 1
    print('All values published successfully.')

def publish_values():
    global analyser_qos
    global numberOfMessage
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(host, port, 60)
    mqttc.on_message = on_message
    mqttc.loop_start()

    for instance_count in instance_counts:
        for delay in delays:
            for qos in qos_levels:
                publish_message("request/qos", str(qos))
                publish_message("request/delay", str(delay))
                publish_message("request/instancecount", str(instance_count))
                print("Values published successfully.")

                mqttc.subscribe(f"counter/{instance_count}/{qos}/{delay}", qos=analyser_qos)
                print(f"Subscribed to counter/{instance_count}/{qos}/{delay}.") 

                time.sleep(16.25)  # Adjust this delay according to your requirements
                print(f'Number of messages {numberOfMessage}')
                numberOfMessage = 0

    print(f'All values published at qos: {analyser_qos}')

analyser()
