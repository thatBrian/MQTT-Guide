Pentest Info: https://book.hacktricks.xyz/network-services-pentesting/1883-pentesting-mqtt-mosquitto#pentesting-mqtt
Python Mqtt Paho package Documentation:https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html

1. Download and install Mosquitto

-   https://mosquitto.org/download/
-   https://mosquitto.org/blog/2013/01/mosquitto-debian-repository/

2. Run the Moquitto Server

-   https://mosquitto.org/man/mosquitto-8.html

3. Check if Mosquitto is already running

```
sudo service mosquitto status
```

4. Check configuration

```
cat /etc/mosquitto/mosquitto.conf
```

5. Create accounts for mosquitto

-   Add following line to `/etc/mosquitto/mosquitto.conf`

```
password_file /etc/mosquitto/password
```

-   Create password file

```
touch /etc/mosquitto/password && chmod 600 /etc/mosquitto/password
```

-   Add users, run the following command

```
mosquitto_passwd /etc/mosquitto/password user1
```

6. Enforce use of account
   Add following line to `etc/mosquitto/mosquitto.conf`

```
allow_anonymous false
```

7. Restart mosquitto

```
sudo systemctl restart mosquitto.service
```

7. Run wireshark and listen to loopback.

8. Set filter to `mqtt`
