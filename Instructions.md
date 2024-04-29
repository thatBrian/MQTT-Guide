Pentest Info: https://book.hacktricks.xyz/network-services-pentesting/1883-pentesting-mqtt-mosquitto#pentesting-mqtt
Python Mqtt Paho package Documentation:https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html

This this demonstration we'll go over the lack of security in MQTT by default, the weakness in it's built-in security setup and how to properly secure MQTT

### Setup MQTT Client and Server

We'll first demonstate how to setup MQTT locally and review it's lack of security by default.

1. Download and install Mosquitto

-   We'll use the below links to download Moqsuitto. Mosquitto is an open source message broker that implements the MQTT protocol.
    -   https://mosquitto.org/download/
-   For this demonstration I'll be testing on a Debian based Linux system. We will follow the below guide:
    -   https://mosquitto.org/blog/2013/01/mosquitto-debian-repository/

2. Run the Moquitto Server

-   Next step is to startup the Mosquitto server/broker. Follow the below documentation:
    -   https://mosquitto.org/man/mosquitto-8.html
-   For our Linux system, the Mosquitto server/broker should already begin running after installation.
    -   You can verify the status with the following command: `service mosquitto status`
    -   You should see something like the below:
        ```
        ● mosquitto.service - Mosquitto MQTT v3.1/v3.1.1 Broker
           Loaded: loaded (/lib/systemd/system/mosquitto.service; enabled; vendor preset: enabl>
           Active: active (running) since Tue 2024-04-23 22:12:52 EDT; 5 days ago
             Docs: man:mosquitto.conf(5)
                   man:mosquitto(8)
        ...
        ```
    -   Verify that the "Active" section states `active (running)`
    -   If it does not show this, then you may attempt to restart the service wit the following command: `systemctl restart mosquitto.service`

3. Check configuration

-   You can make any configurational changes to the following file: `/etc/mosquitto/mosquitto.conf`
-   You can review the possible configuational changes here: https://mosquitto.org/man/mosquitto-conf-5.html

At this point we should be done setting up Mosquitto. We can test this with the sample python script included in this guide. The script file is named: `client_no_password.py`.

You may run the file using the following command: `python3 client_no_password.py`

If the script runs successfully we should see the below output:

```
❯ python3 client_with_password.py
Starting...
Connected
Topic: $SYS/broker/version | QOS: 0  | Message: b'mosquitto version 1.6.9'
Topic: $SYS/broker/uptime | QOS: 0  | Message: b'433048 seconds'
Topic: $SYS/broker/uptime | QOS: 0  | Message: b'433059 seconds'
Topic: $SYS/broker/clients/total | QOS: 0  | Message: b'1'
Topic: $SYS/broker/clients/maximum | QOS: 0  | Message: b'1'
Topic: $SYS/broker/clients/active | QOS: 0  | Message: b'1'
Topic: $SYS/broker/clients/connected | QOS: 0  | Message: b'1'
```

The script we ran above attempts to first connect to the MQTT broker found at localhost (127.0.0.1) on port 1883 (default MQTT port). After a connection is established the script subscribes to the `#` and `$SYS/#` topics. `#` is a wild card topic that represents any subdirectories within a topic hierarchy. For example, a subscription to `cars/#` subscribes to any topic within cars like `cars/tires` or `cars/engine/oil` etc. In this case the `#` subscription is for everything. The `$SYS/#` is a subscription to a special topic that contians information about the MQTT broker. (We will touch base on this later in detail on information leakage of unsecured brokers.)

Now that we have successfully ran the broker and client we can pull up Wireshark and review some of the details of the connection.

After startup Wireshark and capturing the local traffic, we can set up a filter to capture the MQTT specific traffic. The filter is straight forward, just type `mqtt` into the filters bar.

We should be left with a couple of different types of packets.
The first packet would be the `Connect Command` packet, this represents the request sent from the client in an attempt to initiate a connection with the broker. The next packet following this is the `Connect Ack` which represents the response from the broker to the client's request. For now, since there isn't any type of authentication process, any client should be freely able to connect to the broker. To properly protect our system we'll need to setup an authentication process. We'll dive into this a bit more in the following msection.

For users that were not able to setup the client/broker connection or capture the packets in Wireshark, we've attached a sample capture file. The file is named `client_no_password.pcapng`.

### Setup MQTT username & password authentication

We've setup the client/broker connection successfully in the previous section. Now we will configure the broker to require a username and password during the connection process.

1. Configure Mosquitto.

-   We'll first begin by updating the broker's configuration file.

-   Add following lines to `/etc/mosquitto/mosquitto.conf`.

```
password_file /etc/mosquitto/password
allow_anonymous false
```

-   The `password_file` option will require Mosquitto to use a username and password during the connection process. The second part of the command specifies the file we'll use to verify the credentials with.

-   The `allow_anonymous` option allows the clients to connect to the broker without providing credentials. We set this to false so the client must provide credentials.

-   Details of these options can be found here: https://mosquitto.org/man/mosquitto-conf-5.html

2. Create password file.

-   In this step we will create an empty password file that will be used to store the credential used to verify a connection.

```
touch /etc/mosquitto/password && chmod 600 /etc/mosquitto/password
```

3. Create user accounts

-   Next step is the create the accounts that will be used by the client.
-   The below command uses Mosquitto's password file management tool to setup a user account. More details can be found here: https://mosquitto.org/man/mosquitto_passwd-1.html

```
mosquitto_passwd /etc/mosquitto/password user1
```

-   The above command will create an account with the username `user1` and a password of your choosing.

4. Restart mosquitto

-   Now to make sure our changes are being used by the broker, we'll restart the server.

```
sudo systemctl restart mosquitto.service
```

After completing the above steps we can now verify that our changes are working correctly.

Lets try to run the previous script we used in the previous section.

```
python3 client_no_password.py
```

The above script should provide us witht he following output:

```❯ python3 client_no_password.py
Starting...
Connected
Connected
Connected
Connected
```

After about 4 tries the client gives up on connecting, because every request sent is being rejected by the broker.

Next, we can try to attempt to connect with the account we created in the this section. Open up the following file with a text editor: `client_with_password.py`. Update the following line with the username and password you created the account with:

```
...
client.username_pw_set(username="user1", password="test")
...
```

Then, run the script: `python3 client_with_password.py`.

You should see a similar output to when we ran the script agains the broker without authentication.

If we open Wireshark we'll be able to the same `Connect Command` and `Connect Ack` commands, but this time we'll see a rejection in the `Connect Ack` response when running the `client_no_password.py` script. This is expected as we did not provide the required credentials when trying to connect.

When running Wireshark with durng the `client_with_password.py` script we should see a Connection Accepted return code similar to what we saw in the previous section without authentication. If we took a look into the `Connect Command` packet, we should notice something different from before. Under the `MQ Telemetry Transport Protocol` section there should be two new sections named 'User Name' and 'Password'. This is the username and password provided by the client during the connection process.

Though we now have basic authentication setup with MQTT, it is evident that the authentication process itself is not secure. In the next section we'll learn about how MQTT solves this using TLS.

### Setup MQTT with SSL/TLS

1. Reset MQTT configuration

-   The first step us to undo the changes we've made to MQTT and add changes to use the certificate option.

Remove the two lines below:

```
password_file /etc/mosquitto/password
allow_anonymous false #TODO: DOUBLE CHECK THIS
```

Then add the following lines:

```
require_certificate true
use_identity_as_username true
```

In the above lines we've removed the requirment for passwords and allowed anonymous connections. We've also made certificates required. This option `use_identity_as_username` causes the Common Name (CN) form the client certificate to be used instead of the MQTT username.

2. Generate Certificates

-   The next step is to generate the Certificates necessary for the broker and client to use SSL encrypted network connections and authentications. A more detailed guide can be found here: https://mosquitto.org/man/mosquitto-tls-7.html
-   We'll first generate a certificate authority certificate and key

When using certificate base approach, the password is not longer necessary because it is assumed that only authenticated clients have valid certificates.

1. Generate CA Certificates

```
openssl genrsa -out ca.key 2048
openssl req -new -x509 -key ca.key -out ca.crt -subj "/C=US/ST=NY/L=NY/O=MobileSecurityClass/CN=CAMqtt" -days 3650
```

2. Generate Server Certificate and Key

```
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=NY/L=NY/O=MobileSecurityClass/CN=localhost"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650
```

3. Configure Mosquitto Broker

-   Edit the `mosquitto.conf` file and add the following lines

```
listener 8883
port 8883

# Path to server certificate
certfile mqtt_certs/server.crt

# Path to server key
keyfile mqtt_certs/server.key

# Optional: Path to CA certificate (for client certificate verification)
# cafile mqtt_certs/ca.crt
```

4. Restart Mosquitto Broker

```
sudo systemctl restart mosquitto.service
```

listener 8883

certfile /etc/mosquitto/cert/server.crt

keyfile /etc/mosquitto/cert/server.key

cafile /etc/mosquitto/ca_certificates/ca.crt

If you'd like to learn more about this Authentication, Mosquitto actually provides a pretty nice introduction in the documentation here: https://mosquitto.org/man/mosquitto-conf-5.html
