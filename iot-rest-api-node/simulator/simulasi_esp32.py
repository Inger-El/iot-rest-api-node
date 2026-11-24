"""
==============================================================================
 Simulator ESP32 - Tugas Praktek 9: REST API Node
 Mata Kuliah: Pemrograman Internet of Things (TIF1504)
 
 Simulasi perangkat ESP32 yang:
   1. Publish data sensor (suhu & kelembaban) ke topik MQTT 'iot/sensor'
   2. Subscribe ke topik 'iot/kontrol' untuk menerima perintah aktuator
   3. Subscribe ke topik 'iot/alert' untuk menerima notifikasi threshold
==============================================================================
"""

import json
import random
import time
from datetime import datetime, timezone, timedelta

import paho.mqtt.client as mqtt

# ==============================================================================
# KONFIGURASI
# ==============================================================================
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
CLIENT_ID = "ESP32-Simulator"

TOPIC_SENSOR = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"
TOPIC_ALERT = "iot/alert"

PUBLISH_INTERVAL = 3  # detik

# Rentang sensor
SUHU_MIN = 25.0
SUHU_MAX = 35.0
KELEMBABAN_MIN = 55.0
KELEMBABAN_MAX = 80.0

# Timezone WIB (UTC+8)
WIB = timezone(timedelta(hours=8))


# ==============================================================================
# STATUS PERANGKAT
# ==============================================================================
lamp_status = "off"


# ==============================================================================
# CALLBACK FUNCTIONS (paho-mqtt v2.x compatible)
# ==============================================================================
def on_connect(client, userdata, flags, reason_code, properties):
    """Callback saat berhasil terhubung ke MQTT Broker."""
    if reason_code == 0:
        print("=" * 60)
        print("  ESP32 Simulator - Terhubung ke MQTT Broker")
        print(f"  Broker : {MQTT_BROKER}:{MQTT_PORT}")
        print(f"  Client : {CLIENT_ID}")
        print("=" * 60)
        print(f"  [PUB]  Publish sensor   -> {TOPIC_SENSOR} (setiap {PUBLISH_INTERVAL}s)")
        print(f"  [SUB]  Kontrol aktuator <- {TOPIC_KONTROL}")
        print(f"  [SUB]  Alert threshold  <- {TOPIC_ALERT}")
        print("=" * 60)
        print()

        # Subscribe ke topik kontrol dan alert
        client.subscribe(TOPIC_KONTROL)
        client.subscribe(TOPIC_ALERT)
    else:
        print(f"[ERROR] Gagal terhubung, kode: {reason_code}")


def on_disconnect(client, userdata, flags, reason_code, properties):
    """Callback saat koneksi terputus."""
    print(f"\n[WARN] Koneksi terputus (kode: {reason_code}). Mencoba reconnect...")


def on_message(client, userdata, msg):
    """Callback saat menerima pesan dari topik yang di-subscribe."""
    global lamp_status

    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        payload = msg.payload.decode("utf-8", errors="replace")

    timestamp = datetime.now(WIB).strftime("%H:%M:%S")

    if topic == TOPIC_KONTROL:
        # Perintah aktuator dari Node-RED
        device = payload.get("device", "unknown") if isinstance(payload, dict) else "unknown"
        action = payload.get("action", "unknown") if isinstance(payload, dict) else "unknown"

        if device == "lamp":
            lamp_status = action
            icon = "💡" if action == "on" else "⚫"
            print(f"  [{timestamp}] {icon} KONTROL DITERIMA: Lampu -> {action.upper()}")
        else:
            print(f"  [{timestamp}] ⚙️  KONTROL DITERIMA: {device} -> {action}")

    elif topic == TOPIC_ALERT:
        # Notifikasi alert dari Node-RED
        message = payload.get("message", str(payload)) if isinstance(payload, dict) else str(payload)
        suhu = payload.get("suhu", "?") if isinstance(payload, dict) else "?"
        threshold = payload.get("threshold", "?") if isinstance(payload, dict) else "?"
        print()
        print("  " + "!" * 56)
        print(f"  [{timestamp}] 🚨 ALERT THRESHOLD!")
        print(f"               Suhu saat ini : {suhu}°C")
        print(f"               Batas maksimal: {threshold}°C")
        print(f"               Pesan         : {message}")
        print("  " + "!" * 56)
        print()


# ==============================================================================
# FUNGSI GENERATE DATA SENSOR
# ==============================================================================
def generate_sensor_data():
    """
    Generate data sensor simulasi.
    Sesekali menghasilkan suhu di atas 30°C agar fitur threshold terlihat.
    """
    # 40% kemungkinan suhu di atas 30°C agar threshold sering terpicu
    if random.random() < 0.4:
        suhu = round(random.uniform(30.1, SUHU_MAX), 1)
    else:
        suhu = round(random.uniform(SUHU_MIN, 30.0), 1)

    kelembaban = round(random.uniform(KELEMBABAN_MIN, KELEMBABAN_MAX), 1)
    timestamp = datetime.now(WIB).isoformat()

    return {
        "suhu": suhu,
        "kelembaban": kelembaban,
        "timestamp": timestamp
    }


# ==============================================================================
# MAIN
# ==============================================================================
def main():
    # Inisialisasi client MQTT dengan API v2
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)

    # Set callback
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Koneksi ke broker
    print(f"Menghubungkan ke MQTT Broker ({MQTT_BROKER}:{MQTT_PORT})...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except ConnectionRefusedError:
        print("[ERROR] Tidak dapat terhubung ke MQTT Broker!")
        print("        Pastikan Mosquitto sudah berjalan di localhost:1883")
        return
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    # Jalankan loop network di background thread
    client.loop_start()

    # Tunggu koneksi
    time.sleep(1)

    counter = 0
    try:
        while True:
            counter += 1
            data = generate_sensor_data()

            # Publish ke topik sensor
            payload = json.dumps(data)
            result = client.publish(TOPIC_SENSOR, payload, qos=1)

            timestamp = datetime.now(WIB).strftime("%H:%M:%S")
            lamp_icon = "💡" if lamp_status == "on" else "⚫"

            print(
                f"  [{timestamp}] #{counter:04d} 📡 Publish -> "
                f"Suhu: {data['suhu']:>5.1f}°C | "
                f"Kelembaban: {data['kelembaban']:>5.1f}% | "
                f"Lampu: {lamp_icon} {lamp_status.upper()}"
            )

            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n[INFO] Simulator dihentikan oleh pengguna (Ctrl+C)")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[INFO] Koneksi MQTT ditutup. Selesai.")


if __name__ == "__main__":
    main()
