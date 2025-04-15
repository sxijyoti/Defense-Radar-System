import serial
import requests
import time
import socket
import math
import os
from dotenv import load_dotenv, set_key

# Load .env variables
load_dotenv()

# Telegram bot setup
ENV_PATH = ".env"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# Load multiple chat IDs
def get_saved_chat_ids():
    raw = os.getenv("TELEGRAM_CHAT_IDS", "")
    return [cid.strip() for cid in raw.split(",") if cid.strip()]

# Save chat IDs back to .env
def save_chat_ids_to_env(chat_ids):
    ids_str = ",".join(chat_ids)
    set_key(ENV_PATH, "TELEGRAM_CHAT_IDS", ids_str)

# Automatically get chat IDs via Telegram
def get_chat_ids_from_telegram():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url, timeout=5)
        updates = res.json()
        ids = set()
        for item in updates.get("result", []):
            try:
                cid = str(item["message"]["chat"]["id"])
                ids.add(cid)
            except KeyError:
                continue
        return list(ids)
    except Exception as e:
        print("❌ Failed to fetch chat IDs:", e)
        return []

# Merge and update chat ID list
discovered_ids = get_chat_ids_from_telegram()
saved_ids = get_saved_chat_ids()
all_chat_ids = list(set(discovered_ids + saved_ids))

if all_chat_ids != saved_ids:
    print("🔁 New chat IDs discovered, updating .env")
    save_chat_ids_to_env(all_chat_ids)

# Use the full list for sending alerts
TELEGRAM_CHAT_IDS = all_chat_ids

# Serial port settings
SERIAL_PORT = "/dev/ttyUSB0"  # Update if needed
BAUD_RATE = 9600

# TCP Socket Setup (for Processing)
HOST = "127.0.0.1"
PORT = 65432

# Alert cooldown settings
ALERT_COOLDOWN = 5  # seconds
last_alert_time = 0

def send_alert(message):
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            payload = {"chat_id": chat_id, "text": message}
            response = requests.post(TELEGRAM_URL, data=payload, timeout=2)
            if response.status_code == 200:
                print(f"🚀 Alert Sent to {chat_id}!")
            else:
                print(f"❌ Failed to send to {chat_id}:", response.text)
        except Exception as e:
            print(f"❌ Telegram error for {chat_id}:", e)

def polar_to_cartesian(angle_deg, distance_cm):
    angle_rad = math.radians(angle_deg)
    x = distance_cm * math.cos(angle_rad)
    y = distance_cm * math.sin(angle_rad)
    return round(x, 2), round(y, 2)

def main():
    global last_alert_time

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(2)
    except Exception as e:
        print("💥 Serial connection failed:", e)
        return

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

                            try:
                                conn.sendall(f"{angle},{distance},{pir1},{pir2}\n".encode())
                            except Exception as e:
                                print("❌ Socket send failed:", e)

                            print(f"📤 Sent to Processing: {angle},{distance},{pir1},{pir2}")

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
