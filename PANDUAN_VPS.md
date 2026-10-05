# PANDUAN DEPLOYMENT KE VPS (Ubuntu/Debian)

Karena Bapak tidak memberikan password (yang mana ini adalah praktik keamanan yang SANGAT BAGUS!), Bapak bisa melakukan copy-paste perintah di bawah ini ke dalam terminal SSH VPS Bapak.

## Langkah 1: Update Server & Install Python
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx git -y
```

## Langkah 2: Download Kode dari GitHub
(Ganti URL di bawah dengan URL repositori GitHub Bapak)
```bash
cd /var/www
sudo git clone https://github.com/username-bapak/lapsentinel-dashboard.git
cd lapsentinel-dashboard
```

## Langkah 3: Setup Virtual Environment & Install Library
```bash
sudo python3 -m venv venv
source venv/bin/activate
sudo venv/bin/pip install -r requirements.txt
```

## Langkah 4: Jalankan Server Background (Gunicorn + Systemd)
Buat file service agar dashboard otomatis menyala walau server di-restart:
```bash
sudo nano /etc/systemd/system/lapsentinel.service
```
Lalu Paste kode ini di dalamnya:
```ini
[Unit]
Description=Gunicorn instance to serve LapSentinel Dashboard
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/lapsentinel-dashboard
Environment="PATH=/var/www/lapsentinel-dashboard/venv/bin"
ExecStart=/var/www/lapsentinel-dashboard/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```
Simpan (Ctrl+X, tekan Y, lalu Enter). Lalu nyalakan servicenya:
```bash
sudo systemctl start lapsentinel
sudo systemctl enable lapsentinel
```

## Langkah 5: Hubungkan ke Domain (Nginx)
```bash
sudo nano /etc/nginx/sites-available/lapsentinel
```
Paste kode ini:
```nginx
server {
    listen 80;
    server_name lap.yosefhomeserver.my.id;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Aktifkan dan restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/lapsentinel /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

SELESAI! Dashboard Bapak sekarang sudah online di http://lap.yosefhomeserver.my.id
