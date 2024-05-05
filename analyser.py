import paho.mqtt.publish as publish
import time

host = "localhost"
port = 1883

# Function to publish a message to the specified topic
def publish_message(topic, message):
    publish.single(topic, payload=message, hostname=host, port=port)
    print(f"Published: {message} to topic: {topic}")

# Function to repeatedly prompt the user for input and publish messages
def publish_values():
    while True:
        try:
            qos = int(input("Enter QoS level (0, 1, or 2): "))
            delay = int(input("Enter delay in milliseconds: "))
            instance_count = int(input("Enter instance count: "))

            publish_message("request/qos", str(qos))
            publish_message("request/delay", str(delay))
            publish_message("request/instancecount", str(instance_count))

            print("Values published successfully.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

        time.sleep(1)

# Start publishing values
publish_values()
