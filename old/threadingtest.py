import paho.mqtt.client as mqtt
import time
import threading
import os
import pandas as pd

class Publisher:
    shared_counter_lock = threading.Lock()
    iteration_counter = 0  
    
    def __init__(self, pub_number):
        self.host = "localhost"
        self.port = 1883
        self.pub_number = pub_number
        self.qos = 0
        self.delay = 0
        self.instance_count = 1
        self.tracker = 0

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect_to_broker(self):
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()


    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Publisher number {self.pub_number} connected with result code {reason_code}.")
        client.subscribe("request/qos")
        client.subscribe("request/delay")
        client.subscribe("request/instancecount")

    def on_message(self, client, userdata, message):
        if message.topic == "request/qos":
            self.qos = int(message.payload)
            self.tracker += 1
        elif message.topic == "request/delay":
            self.delay = int(message.payload)
            self.tracker += 1
        elif message.topic == "request/instancecount":
            self.instance_count = int(message.payload)
            comparison = int(message.payload)
            self.tracker += 1
        if self.tracker == 3:
            Publisher.iteration_counter += 1  
            if self.pub_number <= comparison:
                self.publish_counter()
                self.tracker = 0
            else:
                self.tracker = 0

    def publish_counter(self):
        topic = f"counter/{self.pub_number}/{self.qos}/{self.delay}"
        print(f"Publisher number {self.pub_number} is publishing to {topic} with qos: {self.qos} and delay: {self.delay} ms.")

        start_time = time.time()
        duration = 10

        counter = 0
        while time.time() < start_time + duration:
            counter += 1
            self.client.publish(topic, str(counter), qos=self.qos)
            time.sleep(self.delay / 1000)  # Delay in milliseconds
        logger(counter, topic)


def logger(counter, topic):
    if not os.path.exists('publisher_log.csv'):
        open('publisher_log.csv', 'w').close()  # Create an empty file

    log_entry = pd.DataFrame({'Iteration ':[Publisher.iteration_counter],'Counter': [counter], 'Topic': [topic]})
    log_entry.to_csv('publisher_log.csv', mode='a', header=False, index=False)

def main():
    instances = 5
    publishers = [Publisher(pub_number) for pub_number in range(1, instances+1)]
    threads = [threading.Thread(target=publisher.connect_to_broker) for publisher in publishers]

    try:
        for thread in threads:
            thread.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for publisher in publishers:
            publisher.client.loop_stop()
        for thread in threads:
            thread.join()


if __name__ == "__main__":
    main()
