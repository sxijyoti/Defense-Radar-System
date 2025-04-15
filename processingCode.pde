import java.net.*;
import java.io.*;

final int MAX_DISTANCE_CM = 70; // New max radar range

String noObject;
int angle = 0;
int distance = 0;
int pir1 = 0;
int pir2 = 0;

Socket socket;
BufferedReader input;

void setup() {
  size(1200, 700);
  smooth();

  try {
    socket = new Socket("127.0.0.1", 65432); // Match Python bot host/port
    input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
    println("Connected to Python socket");
  } catch (Exception e) {
    println("Socket connection failed: " + e);
  }
}

void draw() {
  fill(0, 80);
  noStroke();
  rect(0, 0, width, height);

  readData();   // Read TCP data each frame
  drawRadar();
  drawSweep();
  drawLine();
  drawObject();
  drawPIR();    // Visualize PIR zones
  drawText();
}

void readData() {
  try {
    if (input.ready()) {
      String data = input.readLine();
      String[] items = split(data, ',');
      if (items.length == 4) {
        angle = int(items[0]);
        distance = int(items[1]);
        pir1 = int(items[2]);
        pir2 = int(items[3]);
        println("Received: " + data);
      }
    }
  } catch (Exception e) {
    println("Read error: " + e);
  }
}

void drawRadar() {
  pushMatrix();
  strokeWeight(2);
  stroke(0, 255, 0);
  noFill();

  float maxRadius = height * 0.6;

  for (int r = 1; r <= 4; r++) {
    float radius = map(r, 1, 4, maxRadius * 0.25, maxRadius);
    arc(width / 2, height, radius * 2, radius * 2, PI, TWO_PI);
  }

  for (int a = 30; a <= 150; a += 30) {
    float x = cos(radians(a)) * maxRadius;
    float y = sin(radians(a)) * maxRadius;
    line(width / 2, height, width / 2 - x, height - y);
  }

  fill(0, 255, 0);
  textSize(16);
  textAlign(CENTER);
  for (int a = 30; a <= 150; a += 30) {
    float x = cos(radians(a)) * (maxRadius + 20);
    float y = sin(radians(a)) * (maxRadius + 20);
    text(a + "°", width / 2 - x, height - y);
  }

  textAlign(LEFT);
  for (int r = 1; r <= 4; r++) {
    float radius = map(r, 1, 4, maxRadius * 0.25, maxRadius);
    int label = int(map(radius, 0, maxRadius, 0, MAX_DISTANCE_CM));
    text(label + "cm", width / 2 + radius, height - 10);
  }

  popMatrix();
}

void drawLine() {
  pushMatrix();
  translate(width / 2, height);
  stroke(0, 255, 0);
  strokeWeight(2);
  float r = height - height * 0.12;
  line(0, 0, r * cos(radians(angle)), -r * sin(radians(angle)));
  popMatrix();
}

void drawSweep() {
  pushMatrix();
  translate(width / 2, height);

  noStroke();
  if (pir1 == 1 || pir2 == 1) {
    fill(255, 0, 0, 80); // Red if motion detected
  } else {
    fill(0, 255, 0, 50); // Green otherwise
  }

  float radius = height - height * 0.12;
  float startAngle = radians(angle - 10);
  float endAngle = radians(angle + 10);
  arc(0, 0, radius * 2, radius * 2, startAngle, endAngle, PIE);
  popMatrix();
}

void drawObject() {
  if (distance <= MAX_DISTANCE_CM) {
    pushMatrix();
    translate(width/2, height);

    float maxRadius = height * 0.6;
    float scale = maxRadius / MAX_DISTANCE_CM;

    float x = distance * scale * cos(radians(angle));
    float y = -distance * scale * sin(radians(angle));

    fill(255, 0, 0);
    noStroke();
    ellipse(x, y, 10, 10);
    popMatrix();
  }
}

void drawPIR() {
  pushMatrix();
  translate(width / 2, height);
  float radius = height - height * 0.12;
  noStroke();

  // PIR1 triggers left sector (30–90°)
  if (pir1 == 1) {
    fill(255, 255, 0, 80); // Yellow
    arc(0, 0, radius * 2, radius * 2, radians(30), radians(90), PIE);
  }

  // PIR2 triggers right sector (90–150°)
  if (pir2 == 1) {
    fill(255, 165, 0, 80); // Orange
    arc(0, 0, radius * 2, radius * 2, radians(90), radians(150), PIE);
  }

  popMatrix();
}

void drawText() {
  pushMatrix();
  fill(0);
  noStroke();
  rect(0, height - height * 0.0648, width, height);
  fill(0, 255, 0);
  textSize(25);

  if (distance > MAX_DISTANCE_CM) {
    noObject = "Out of Range";
  } else {
    noObject = "In Range";
  }

  text("MPCA", 50, height - 10);
  text("Angle: " + angle + "°", width / 2 - 50, height - 10);
  text("Distance: " + distance + "cm", width - 250, height - 10);
  text("PIR1: " + pir1 + "  PIR2: " + pir2, 50, height - 40);
  popMatrix();
}
