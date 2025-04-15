import serial
import requests
import time
import socket
import math
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Serial port settings
SERIAL_PORT = "/dev/ttyUSB0"  # Update if needed
BAUD_RATE = 9600

# Access variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# TCP Socket Setup (for Processing)
HOST = "127.0.0.1"
PORT = 65432

# Alert cooldown settings
ALERT_COOLDOWN = 5  # seconds
last_alert_time = 0

def send_alert(message):
    try:
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(TELEGRAM_URL, data=payload, timeout=2)
        if response.status_code == 200:
            print("🚀 Alert Sent!")
        else:
            print("❌ Failed to send alert:", response.text)
    except Exception as e:
        print("❌ Telegram error:", e)

def polar_to_cartesian(angle_deg, distance_cm):
    angle_rad = math.radians(angle_deg)
    x = distance_cm * math.cos(angle_rad)
    y = distance_cm * math.sin(angle_rad)
    return round(x, 2), round(y, 2)

def main():
    global last_alert_time

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(2)  # Wait for Arduino connection
    except Exception as e:
        print("💥 Serial connection failed:", e)
        return

    # Start TCP socket server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    print(f"📡 Socket server listening on {HOST}:{PORT}")

    conn, addr = sock.accept()
    print(f"🟢 Processing connected: {addr}")

    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()

                    if not line:
                        continue

                    if "," in line and line.endswith("."):
                        data = line[:-1].split(",")

                        if len(data) == 4:
                            angle = int(data[0])
                            distance = int(data[1])
                            pir1 = int(data[2])
                            pir2 = int(data[3])

                            # Send to Processing
                            try:
                                conn.sendall(f"{angle},{distance},{pir1},{pir2}\n".encode())
                            except Exception as e:
                                print("❌ Socket send failed:", e)

                            print(f"📤 Sent to Processing: {angle},{distance},{pir1},{pir2}")

                            # Trigger alert
                            if distance < 50 or pir1 == 1 or pir2 == 1:
                                now = time.time()
                                if now - last_alert_time > ALERT_COOLDOWN:
                                    x, y = polar_to_cartesian(angle, distance)
                                    alert_msg = (
                                        f"⚠️ Obstruction Detected!\n"
                                        f"Angle: {angle}°\n"
                                        f"Distance: {distance}cm\n"
                                        f"Coordinates: ({x}, {y})\n"
                                        f"PIR1: {pir1}, PIR2: {pir2}"
                                    )
                                    send_alert(alert_msg)
                                    last_alert_time = now

                    elif "DANGER!" in line:
                        print("⚠️ DANGER string detected in line:", line)

            except Exception as e:
                print("💥 Loop Error:", e)

    except KeyboardInterrupt:
        print("🛑 Interrupted by user.")
    finally:
        conn.close()
        ser.close()
        sock.close()
        print("🔴 Closed all connections.")

if __name__ == "__main__":
    main()