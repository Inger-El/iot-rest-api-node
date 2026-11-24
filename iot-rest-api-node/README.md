# 🌐 Tugas Praktek 9: REST API Node — Pemrograman Internet of Things

> **Mata Kuliah:** Pemrograman Internet of Things (TIF1504)  
> **Tugas:** Praktek 9 — REST API & Antarmuka Web IoT  
> **Nama:** Elma Najaratun Nisa  
> **NPM:** 2410020155  
> **Program Studi:** Sistem Informasi  

---

## 📋 Deskripsi Proyek

Sistem IoT lengkap berbasis **Node-RED** yang mengintegrasikan sensor simulasi ESP32, MQTT Broker (Mosquitto), REST API, Database SQLite, WebSocket real-time, dan Custom Web Dashboard.

### Arsitektur Sistem

```
┌─────────────────┐    MQTT     ┌──────────────┐    HTTP/WS    ┌──────────────┐
│  Simulator      │◄──────────►│   Node-RED    │◄────────────►│  Dashboard   │
│  ESP32          │  iot/sensor │   Backend     │  REST API    │  (Browser)   │
│  (Python)       │  iot/kontrol│              │  WebSocket   │              │
│                 │  iot/alert  │   + SQLite    │              │  Chart.js    │
└────────┬────────┘            └──────┬───────┘              └──────────────┘
         │                            │
         ▼                            ▼
   Mosquitto MQTT              SQLite Database
   localhost:1883              iot_data.db
```

---

## ✅ Checklist 5 Fitur Tugas Pengembangan (Nilai Tambah)

| # | Fitur | Deskripsi | Status |
|---|-------|-----------|--------|
| 1 | **Threshold Alert** | Endpoint `PUT /api/threshold` untuk set batas suhu + notifikasi otomatis via MQTT `iot/alert` & WebSocket saat suhu melewati batas | ✅ |
| 2 | **Grafik Chart.js Real-Time** | Line chart dua dataset (Suhu °C & Kelembaban %) yang update real-time via WebSocket (20 data terakhir) | ✅ |
| 3 | **Autentikasi API Key** | Semua endpoint REST API dilindungi header `X-API-Key` (default: `uniska-iot-2026`), respons `401` jika tidak valid | ✅ |
| 4 | **WebSocket Real-Time** | Push data sensor, alert, kontrol, dan threshold ke dashboard via `ws://localhost:1880/ws/sensor` tanpa polling | ✅ |
| 5 | **Database SQLite** | Semua data sensor disimpan ke tabel `sensor_history` di SQLite (bukan flow context), tabel `settings` untuk threshold | ✅ |

---

## 📁 Struktur Proyek

```
iot-rest-api-node/
├── README.md                     # Dokumentasi ini
├── .gitignore                    # File yang dikecualikan dari Git
├── simulator/
│   ├── simulasi_esp32.py         # Simulator ESP32 (Python + paho-mqtt v2.x)
│   └── requirements.txt          # Dependency Python
├── node-red/
│   └── flows.json                # Flow Node-RED (siap import)
└── dashboard/
    └── index.html                # Custom Web Dashboard (HTML5 + CSS3 + JS + Chart.js)
```

---

## 🛠️ Prasyarat (Prerequisites)

Pastikan sudah terinstal dan berjalan di Windows:

| Komponen | Versi | Status |
|----------|-------|--------|
| **Node.js** | v18+ | Terinstal |
| **Node-RED** | Terbaru | Berjalan di `http://localhost:1880` |
| **Mosquitto MQTT** | Terbaru | Berjalan sebagai Windows Service di `localhost:1883` (`allow_anonymous true`) |
| **Python** | 3.8+ | Terinstal |

---

## 🚀 Langkah Instalasi & Menjalankan

### Langkah 1: Install Palette `node-red-node-sqlite`

Buka browser ke **http://localhost:1880**, lalu:

1. Klik menu **☰** (kanan atas) → **Manage palette**
2. Tab **Install** → Cari: `node-red-node-sqlite`
3. Klik **Install** pada `node-red-node-sqlite`
4. Tunggu hingga selesai, lalu tutup dialog

> **Catatan:** Jika gagal install via UI, jalankan di CMD/PowerShell:
> ```cmd
> cd %USERPROFILE%\.node-red
> npm install node-red-node-sqlite
> ```
> Lalu restart Node-RED.

### Langkah 2: Import Flow Node-RED

1. Buka **http://localhost:1880**
2. Klik menu **☰** → **Import**
3. Pilih tab **Clipboard**
4. Klik **select a file to import** → Pilih file `node-red/flows.json`
5. Pilih **new flow** (tab baru)
6. Klik **Import**
7. Klik tombol **Deploy** (kanan atas, tombol merah)

> ✅ Setelah deploy, database SQLite akan otomatis diinisialisasi (tabel `sensor_history` dan `settings` dengan threshold default 30.0°C).

### Langkah 3: Install Dependency Python & Jalankan Simulator

Buka **CMD** atau **PowerShell** baru:

```cmd
cd path\ke\iot-rest-api-node\simulator
pip install -r requirements.txt
python simulasi_esp32.py
```

> Simulator akan mulai mengirim data sensor setiap 3 detik ke MQTT topic `iot/sensor`.

### Langkah 4: Buka Dashboard

Buka file `dashboard/index.html` di browser (double-click atau drag ke browser).

> Dashboard akan otomatis terhubung via WebSocket dan menampilkan data real-time.

---

## 📡 REST API Endpoints

Semua endpoint memerlukan header `X-API-Key: uniska-iot-2026`.

### GET `/api/suhu` — Data Sensor Terbaru

```cmd
curl -H "X-API-Key: uniska-iot-2026" http://localhost:1880/api/suhu
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "suhu": 31.2,
    "kelembaban": 65.4,
    "timestamp": "2026-11-24T20:00:00+08:00",
    "threshold": 30.0,
    "alert": true
  }
}
```

### GET `/api/history` — 50 Data Terakhir

```cmd
curl -H "X-API-Key: uniska-iot-2026" http://localhost:1880/api/history
```

**Response (200 OK):**
```json
{
  "status": "success",
  "count": 50,
  "data": [
    {"id": 100, "suhu": 28.5, "kelembaban": 62.3, "timestamp": "...", "received": "..."},
    ...
  ]
}
```

### POST `/api/kontrol` — Kontrol Aktuator (Lampu)

```cmd
curl -X POST -H "Content-Type: application/json" -H "X-API-Key: uniska-iot-2026" -d "{\"device\":\"lamp\",\"action\":\"on\"}" http://localhost:1880/api/kontrol
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Perintah dikirim ke lamp",
  "data": {"device": "lamp", "action": "on"}
}
```

### PUT `/api/threshold` — Ubah Batas Suhu (Fitur #1)

```cmd
curl -X PUT -H "Content-Type: application/json" -H "X-API-Key: uniska-iot-2026" -d "{\"threshold\":31.5}" http://localhost:1880/api/threshold
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Threshold berhasil diperbarui",
  "data": {"threshold": 31.5}
}
```

### Test API Key Invalid (401)

```cmd
curl -H "X-API-Key: salah123" http://localhost:1880/api/suhu
```

**Response (401 Unauthorized):**
```json
{
  "status": "error",
  "message": "Invalid or missing X-API-Key"
}
```

---

## 🧪 Checklist Pengujian

### Pengujian Dasar
- [ ] Node-RED berjalan di `http://localhost:1880`
- [ ] Mosquitto berjalan di `localhost:1883`
- [ ] Flow berhasil di-import dan di-deploy tanpa error
- [ ] Simulator Python berjalan dan mengirim data
- [ ] Dashboard terbuka dan menampilkan data

### Pengujian 5 Fitur Pengembangan
- [ ] **#1 Threshold:** Ubah threshold via dashboard/curl → alert muncul saat suhu melebihi batas baru
- [ ] **#2 Chart.js:** Grafik garis suhu & kelembaban bergerak real-time di dashboard
- [ ] **#3 API Key:** Request tanpa/salah API Key → response `401 Unauthorized`
- [ ] **#4 WebSocket:** Data muncul otomatis di dashboard tanpa refresh (cek Log Aktivitas)
- [ ] **#5 SQLite:** Data tersimpan di database → `GET /api/history` mengembalikan data dari DB

### Pengujian Alur Lengkap
1. Jalankan simulator → data muncul di terminal & dashboard
2. Klik "Nyalakan Lampu" → status berubah di dashboard & terminal simulator
3. Ubah threshold menjadi 28°C → alert sering muncul
4. Coba hapus API Key di dashboard → tombol kontrol error 401
5. Cek `GET /api/history` → data sensor tersimpan di SQLite

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `node-red-node-sqlite` gagal install | Pastikan `node-gyp` dan build tools terinstal: `npm install -g windows-build-tools` |
| Simulator error `ConnectionRefused` | Pastikan Mosquitto berjalan: `net start mosquitto` atau cek Services |
| Dashboard "Disconnected" | Pastikan Node-RED sudah deploy flow, cek URL `ws://localhost:1880/ws/sensor` |
| Error `no such table` | Re-deploy flow Node-RED (tabel dibuat otomatis saat startup via inject node) |
| `paho-mqtt` error inisialisasi | Pastikan pakai v2.x: `pip install paho-mqtt>=2.0.0` |

---

## 📝 Teknologi yang Digunakan

- **Backend:** Node-RED (Node.js)
- **Database:** SQLite (`node-red-node-sqlite`)
- **Message Broker:** Mosquitto MQTT
- **Simulator:** Python 3 + paho-mqtt v2.x
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript
- **Visualisasi:** Chart.js (CDN)
- **Komunikasi Real-Time:** WebSocket (`ws://localhost:1880/ws/sensor`)
- **Autentikasi:** API Key via header `X-API-Key`

---

**© 2026 — Elma Najaratun Nisa (2410020155) — Tugas Praktek Pemrograman Internet of Things**
