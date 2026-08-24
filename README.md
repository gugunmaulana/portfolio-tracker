# Core-Satellite Portfolio & Financial Freedom Tracker

Aplikasi dashboard finansial cerdas dengan integrasi data pasar real-time langsung dari **Yahoo Finance, IDX (Bursa Efek Indonesia), NYSE/NASDAQ, dan Crypto Exchanges**.

---

## 📡 Sumber Data Kredibel Terintegrasi

Sistem ini mengambil data harga real-time, ATH historis, P/E ratio, dan multi-timeframe return langsung dari:
1. **US Stocks & ETF (NYSE/NASDAQ)**: `VOO`, `QQQ`, `SMH`, `NVDA`, `AAPL`, `MSFT`, `AMZN`, `GOOGL`, dll.
2. **Indonesia Stocks (Bursa Efek Indonesia / IDX)**: `BBCA.JK`, `BBRI.JK`, `UNTR.JK`, `BREN.JK`, dll.
3. **Crypto Market**: `BTC-USD`, `ETH-USD`, `MSTR`.
4. **Forex Interbank Rate**: `USDIDR=X` (USD/IDR), `CNYIDR=X` (CNY/IDR).
5. **Commodities**: `GC=F` (Gold / Emas Dunia).

---

## 🚀 Cara Menjalankan Secara Lokal

```bash
# 1. Jalankan script runner
python run.py

# Atau klik ganda file run.bat pada Windows
```
Buka di browser: `http://localhost:8000`

---

## 🌐 Cara Menjadikan Website ONLINE di Internet (Gratis 24/7)

Anda bisa meng-online-kan website ini ke internet secara **gratis** dengan langkah berikut:

### Opsi 1: Render.com (Paling Direkomendasikan & Gratis)
1. Buat akun di [Render.com](https://render.com).
2. Upload folder proyek ini ke repository GitHub Anda (bisa mode Private).
3. Di dashboard Render, klik **New + Web Service**, lalu pilih repository GitHub Anda.
4. Render akan otomatis membaca file `Procfile` dan `requirements.txt`.
5. Klik **Create Web Service** — dalam 2 menit website Anda sudah **ONLINE 24/7** dengan domain HTTPS publik (misal: `https://portofolio-anda.onrender.com`) dan bisa diakses dari HP / Laptop mana saja!

### Opsi 2: Railway.app
1. Buat akun di [Railway.app](https://railway.app).
2. Pilih **Deploy from GitHub repo**.
3. Website akan langsung online secara otomatis.
