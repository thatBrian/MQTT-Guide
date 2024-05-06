import paho.mqtt.client as mqtt
import time
import os

HOST = "127.0.0.1"
PORT = 8883

def on_connect(client, userdata, flags, rc, properties):
    client.subscribe('#', qos=1)
    client.subscribe('$SYS/#')
    print("Connected")

def on_message(client, userdata, message):
    print('Topic: %s | QOS: %s  | Message: %s' % (message.topic, message.qos, message.payload))

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.tls_set(
        './sampleCerts/ca-root-cert.crt',
        './sampleCerts/server.crt',
        './sampleCerts/server.key'
    )
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT)
    client.loop_start()
    time.sleep(10)

if __name__ == "__main__":
    print("Starting...")
    main()