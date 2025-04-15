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
  // Check and update buzzer state first
  updateBuzzer();
  
  bool newDetection = false;
  
  // Read PIR Sensors
  int val1 = digitalRead(pirPin1);
  int val2 = digitalRead(pirPin2);
  
  if (val1 == HIGH || val2 == HIGH) {
    newDetection = true;
  }
  
  // Sweep Servo: 0 to 180
  for (int angle = 0; angle <= 180; angle++) {
    // Check if anything is detected during the scan
    if (scanAndCheck(angle)) {
      newDetection = true;
    }
    
    // Check buzzer during scan to avoid delay
    updateBuzzer();
  }
  
  // Sweep Servo: 180 to 0
  for (int angle = 180; angle >= 0; angle--) {
    // Check if anything is detected during the scan
    if (scanAndCheck(angle)) {
      newDetection = true;
    }
    
    // Check buzzer during scan to avoid delay
    updateBuzzer();
  }
  
  // Control LED
  if (newDetection) {
    digitalWrite(ledPin, HIGH);
    // Activate buzzer immediately if it's not already active
    if (!buzzerActive) {
      activateBuzzer();
    }
    lastMotionTime = millis();
    
    if (state == LOW) {
      Serial.println("Motion or object detected");
      state = HIGH;
    }
  }
  
  // Turn off LED after timeout
  if (state == HIGH && millis() - lastMotionTime > motionTimeout) {
    digitalWrite(ledPin, LOW);
    Serial.println("No motion or object detected");
    state = LOW;
  }
}

void activateBuzzer() {
  digitalWrite(buzzerPin, HIGH);
  buzzerActive = true;
  buzzerStartTime = millis();
  Serial.println("Buzzer activated");
}

void updateBuzzer() {
  // Turn off buzzer after duration
  if (buzzerActive && (millis() - buzzerStartTime > buzzerDuration)) {
    digitalWrite(buzzerPin, LOW);
    buzzerActive = false;
    Serial.println("Buzzer deactivated");
  }
}

bool scanAndCheck(int angle) {
  myServo.write(angle);
  delay(30);
  
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;
  
  // Format: angle,distance,pir1,pir2.
  Serial.print(angle);
  Serial.print(",");
  Serial.print(distance);
  Serial.print(",");
  Serial.print(digitalRead(pirPin1));
  Serial.print(",");
  Serial.print(digitalRead(pirPin2));
  Serial.println(".");
  
  return (distance > 0 && distance < distanceThreshold);
}
