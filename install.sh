#!/bin/bash

echo "======================================"
echo "   INSTALANDO RETROCONSOLA"
echo "======================================"

# Actualizar sistema
echo "[1/5] Actualizando sistema..."
apt update -y

# Instalar dependencias
echo "[2/5] Instalando dependencias..."
apt install -y \
    mednafen \
    python3-pygame \
    python3-pil \
    vlc \
    cvlc \
    fbi \
    alsa-utils \
    git

pip3 install pygame pillow --break-system-packages

# Crear estructura de carpetas
echo "[3/5] Creando estructura de carpetas..."
mkdir -p /home/pi/retroconsola/roms/nes
mkdir -p /home/pi/retroconsola/roms/snes
mkdir -p /home/pi/retroconsola/roms/gba
mkdir -p /home/pi/retroconsola/usb
mkdir -p /home/pi/retroconsola/logs

# Copiar archivos del repo al proyecto
echo "[4/5] Copiando archivos..."
REPO_DIR="$(dirname "$0")"
cp -r "$REPO_DIR/src" /home/pi/retroconsola/
cp -r "$REPO_DIR/assets" /home/pi/retroconsola/
cp -r "$REPO_DIR/roms" /home/pi/retroconsola/
cp "$REPO_DIR/start.sh" /home/pi/retroconsola/
chmod +x /home/pi/retroconsola/start.sh

# Configurar arranque automático
echo "[5/5] Configurando arranque automático..."
cat > /etc/systemd/system/retroconsola.service << 'SERVICE'
[Unit]
Description=RetroConsola
After=multi-user.target

[Service]
Type=simple
User=root
ExecStart=/bin/bash /home/pi/retroconsola/start.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable retroconsola.service

echo "======================================"
echo "   INSTALACION COMPLETA"
echo "   Reinicia con: sudo reboot"
echo "======================================"
