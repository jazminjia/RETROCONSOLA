# 🎮 RetroConsola - KawaiiBox 360 UWU

Consola de videojuegos retro implementada en una Raspberry Pi 3B+ usando el emulador Mednafen.

## 📋 Descripción

Sistema embebido que emula juegos de NES, SNES y Game Boy Advance con una interfaz gráfica personalizada en tonos rosa pastel. Incluye pantalla de arranque animada con logo y música, detección automática de USB para agregar ROMs y control completo mediante gamepad Xbox.

## 🛠️ Requisitos

- Raspberry Pi 3B+
- Raspberry Pi OS Lite
- Control Xbox One/Series conectado por USB
- Pantalla HDMI (resolución 1024x600)
- Memoria microSD de 16GB o más

## 📦 Instalación

    git clone https://github.com/jazminjia/retroconsola.git
    cd retroconsola
    sudo bash install.sh
    sudo reboot

## 🎯 Características

- Pantalla de arranque con logo personalizado y música
- Interfaz gráfica sin escritorio en tonos rosa pastel
- Emulación de NES, SNES y Game Boy Advance con Mednafen
- 16 ROMs precargadas
- Detección automática de USB para agregar nuevas ROMs
- Las ROMs nuevas se marcan con ★ NEW en el menú
- Salida del juego con VIEW + MENU simultáneos
- Sonidos al navegar el menú
- Arranque automático al encender la Raspberry

## 🕹️ Controles

| Botón | Función |
|-------|---------|
| D-PAD | Navegar menú |
| A | Seleccionar juego |
| B | Salir del menú |
| VIEW + MENU | Salir del juego |

## 📁 Estructura del proyecto

    retroconsola/
    ├── src/
    │   ├── boot_screen.py      # Pantalla de arranque
    │   ├── menu_terminal.py    # Menú principal
    │   └── run_game.py         # Lanzador de juegos
    ├── assets/
    │   ├── LOGO.png            # Logo de arranque
    │   ├── FNAF8BIT.ogg        # Música de arranque
    │   ├── DPADSOUND.wav       # Sonido navegación
    │   ├── SELECCIONSOUND.wav  # Sonido selección
    │   ├── SALIDASOUND.wav     # Sonido salida
    │   └── USBSOUND.wav        # Sonido USB detectada
    ├── roms/
    │   ├── nes/                # ROMs de NES
    │   ├── snes/               # ROMs de SNES
    │   └── gba/                # ROMs de GBA
    ├── start.sh                # Script de arranque
    └── install.sh              # Script de instalación

## 👩‍💻 Autoras

| # | Nombre | Lista |
|---|--------|-------|
| 1 | María Jazmín Jiménez Aguirre | 15 |
| 2 | María Elena Soriano Barrera | 33 |

Desarrollado para la materia Fundamentos de Sistemas Embebidos.
