#include <Servo.h>

// Servo + Ultrasonic
Servo myServo;
int trigPin = 9;
int echoPin = 10;
long duration;
int distance;
const int distanceThreshold = 50; // cm

// PIR + LED
const int ledPin = 2;
const int pirPin1 = 3;
const int pirPin2 = 5;
int state = LOW;
unsigned long lastMotionTime = 0;
const int motionTimeout = 2000; // 2 seconds

// Buzzer
const int buzzerPin = 12;  // Connected to digital pin 12
const int buzzerDuration = 3000; // Buzzer sounds for 3 seconds
unsigned long buzzerStartTime = 0;
bool buzzerActive = false;

void setup() {
  // Servo and Ultrasonic
  myServo.attach(11);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  // PIR and LED
  pinMode(ledPin, OUTPUT);
  pinMode(pirPin1, INPUT);
  pinMode(pirPin2, INPUT);
  
  // Buzzer
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW);
  
  // Serial Communication
  Serial.begin(9600);
  delay(30000); // Allow PIR sensors to stabilize
  Serial.println("System Ready...");
}

void loop() {
  // First check PIR sensors immediately
  int val1 = digitalRead(pirPin1);
  int val2 = digitalRead(pirPin2);
  
  if (val1 == HIGH || val2 == HIGH) {
    triggerDetection();
  }
  
  // Sweep Servo: 0 to 180
  for (int angle = 0; angle <= 180; angle++) {
    myServo.write(angle);
    delay(30);
    
    // Check ultrasonic
    measureDistance();
    
    // Check if object detected
    if (distance > 0 && distance < distanceThreshold) {
      triggerDetection();
    }
    
    // Send data
    sendData(angle);
    
    // Check if buzzer should be turned off
    checkBuzzer();
  }
  
  // Sweep Servo: 180 to 0
  for (int angle = 180; angle >= 0; angle--) {
    myServo.write(angle);
    delay(30);
    
    // Check ultrasonic
    measureDistance();
    
    // Check if object detected
    if (distance > 0 && distance < distanceThreshold) {
      triggerDetection();
    }
    
    // Send data
    sendData(angle);
    
    // Check if buzzer should be turned off
    checkBuzzer();
  }
  
  // Check if LED should be turned off
  if (state == HIGH && millis() - lastMotionTime > motionTimeout) {
    digitalWrite(ledPin, LOW);
    Serial.println("No motion or object detected");
    state = LOW;
  }
}

void triggerDetection() {
  // Turn on LED
  digitalWrite(ledPin, HIGH);
  
  // Activate buzzer immediately if not already active
  if (!buzzerActive) {
    digitalWrite(buzzerPin, HIGH);
    buzzerActive = true;
    buzzerStartTime = millis();
    Serial.println("Buzzer activated");
  }
  
  lastMotionTime = millis();
  
  if (state == LOW) {
    Serial.println("Motion or object detected");
    state = HIGH;
  }
}

void checkBuzzer() {
  // Turn off buzzer after duration
  if (buzzerActive && (millis() - buzzerStartTime > buzzerDuration)) {
    digitalWrite(buzzerPin, LOW);
    buzzerActive = false;
    Serial.println("Buzzer deactivated");
  }
}

void measureDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;
}

void sendData(int angle) {
  // Format: angle,distance,pir1,pir2.
  Serial.print(angle);
  Serial.print(",");
  Serial.print(distance);
  Serial.print(",");
  Serial.print(digitalRead(pirPin1));
  Serial.print(",");
  Serial.print(digitalRead(pirPin2));
  Serial.println(".");
}
