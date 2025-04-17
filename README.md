# Defense Radar and Motion Detection System

## Abstract
This project develops a defense-oriented motion detection and threat alert system using an Arduino Uno, combining a Passive Infrared (PIR) sensor with a rotating ultrasonic sensor to detect objects in the sky. The PIR sensor detects motion by sensing changes in infrared radiation, identifying potential threats or intrusions in the area. In addition, the ultrasonic sensor, mounted on a rotating platform, scans the sky by emitting and receiving sound waves, measuring the distance of detected objects.

The Arduino Uno coordinates the operation of both sensors, along with the rotation mechanism of the ultrasonic sensor, enabling the system to cover a wide area for potential airborne threats. Upon detection of motion or an object, the system activates an LED indicator and a buzzer to alert the operator. 

Moreover, the system is integrated with a Alerting Bot System, which sends real-time alerts to registered users whenever an obstruction is detected by the ultrasonic sensor. This bot ensures that notifications reach users directly on their mobile devices, enhancing situational awareness and responsiveness. Users are automatically registered when they interact with the bot, and the system sends automated threat alerts based on sensor data.

This integrated system offers both real-time detection and alerting, making it suitable for various applications in defense, surveillance, and security. By combining sensor-based motion detection, automated scanning, and remote alerting, this project presents a cost-effective solution for enhancing threat monitoring and situational awareness.

## Circuit Diagram
![image](https://github.com/user-attachments/assets/810b1bde-a98f-444a-baea-ed1dd7c43c8c)


## To Run
```sh
# Upload arduinoCode.ino into UNO board
# Run the server
python3 server_script.py
# Run the processingCode.pde
```
