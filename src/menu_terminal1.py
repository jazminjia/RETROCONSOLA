import os
import subprocess
import curses
import pygame
import time

BASE_DIR = "/home/pi/retroconsola/roms"
USB_MOUNT = "/home/pi/retroconsola/usb"

FOLDERS = {
    "NES": f"{BASE_DIR}/nes",
    "SNES": f"{BASE_DIR}/snes",
    "GBA": f"{BASE_DIR}/gba",
}

EXTS = (".nes", ".sfc", ".smc", ".gba", ".gb", ".gbc")


def get_games():
    games = []

    for system, folder in FOLDERS.items():
        os.makedirs(folder, exist_ok=True)

        for name in sorted(os.listdir(folder)):
            if name.lower().endswith(EXTS):
                games.append((system, name, os.path.join(folder, name)))

    return games


def mount_usb():
    os.makedirs(USB_MOUNT, exist_ok=True)

    already_mounted = subprocess.run(
        ["mountpoint", "-q", USB_MOUNT]
    )

    if already_mounted.returncode == 0:
        return True

    # Busca el disco USB y agrega el 1 de la partición
    result = subprocess.run(
        "lsblk -rpno NAME,TRAN | awk '$2==\"usb\" {print $1\"1\"}'| head -n 1",
        shell=True,
        capture_output=True,
        text=True
    )

    usb_dev = result.stdout.strip()

    if not usb_dev:
        return False

    mount = subprocess.run(
        ["mount", usb_dev, USB_MOUNT],
        capture_output=True,
        text=True
    )

    return mount.returncode == 0

def umount_usb():
    already_mounted = subprocess.run(
        ["mountpoint", "-q", USB_MOUNT]
    )

    if already_mounted.returncode != 0:
        return  # Ya está desmontada, no hacer nada

    # Verifica si el disco USB sigue conectado
    result = subprocess.run(
        "lsblk -rpno NAME,TRAN | awk '$2==\"usb\"'",
        shell=True,
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        # USB desconectada, desmonta
        subprocess.run(["umount", USB_MOUNT], capture_output=True)

def scan_usb_and_copy():
    if not mount_usb():
        return 0

    copied = 0

    for root, dirs, files in os.walk(USB_MOUNT):
        for file in files:
            lower = file.lower()
            src = os.path.join(root, file)

            if lower.endswith(".nes"):
                dst_folder = FOLDERS["NES"]
            elif lower.endswith(".sfc") or lower.endswith(".smc"):
                dst_folder = FOLDERS["SNES"]
            elif lower.endswith(".gba"):
                dst_folder = FOLDERS["GBA"]
            else:
                continue

            os.makedirs(dst_folder, exist_ok=True)
            dst = os.path.join(dst_folder, file)

            # Evita duplicados por nombre
            if not os.path.exists(dst):
                result = subprocess.run(
                    ["cp", src, dst],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    copied += 1

    return copied


def launch_game(path):
    curses.endwin()
    subprocess.run(["sudo", "python3", "/home/pi/retroconsola/salir_juego.py", path])


def draw_menu(stdscr, games, selected, status_msg):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    title = "RETRO CONSOLA"
    subtitle = "D-PAD: mover | A: jugar | B: salir"
    line = "-" * min(w - 4, 60)

    stdscr.addstr(1, max(0, (w - len(title)) // 2), title, curses.A_BOLD)
    stdscr.addstr(2, max(0, (w - len(line)) // 2), line)
    stdscr.addstr(3, max(0, (w - len(subtitle)) // 2), subtitle)

    if status_msg:
        stdscr.addstr(5, 4, status_msg[:w - 8], curses.A_BOLD)

    if not games:
        stdscr.addstr(7, 4, "No hay ROMS disponibles.")
        stdscr.addstr(9, 4, "Conecta una USB con archivos .nes, .sfc, .smc o .gba.")
        stdscr.refresh()
        return

    count_text = f"Juegos disponibles: {len(games)}"
    stdscr.addstr(5, max(0, w - len(count_text) - 4), count_text)

    start_y = 7
    visible = max(1, h - 10)
    offset = max(0, selected - visible // 2)

    for i, game in enumerate(games[offset:offset + visible]):
        real_i = offset + i
        system, name, path = game
        text = f"[{system}] {name}"

        if len(text) > w - 10:
            text = text[:w - 13] + "..."

        if real_i == selected:
            stdscr.addstr(start_y + i, 4, "> " + text, curses.A_REVERSE)
        else:
            stdscr.addstr(start_y + i, 4, "  " + text)

    footer = "USB: conecta memoria y espera unos segundos para copiar ROMS nuevas"
    stdscr.addstr(h - 2, max(0, (w - len(footer)) // 2), footer[:w - 1])

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    games = get_games()
    selected = 0
    status_msg = "Sistema listo. Inserta una USB para agregar juegos."
    last_usb_scan = 0

    while True:
        now = time.time()

        # Revisa USB cada 3 segundos
        if now - last_usb_scan > 3:
            umount_usb()
            copied = scan_usb_and_copy()
            last_usb_scan = now

            if copied > 0:
                games = get_games()
                status_msg = f"Se copiaron {copied} ROMS nuevas desde USB."

                if selected >= len(games):
                    selected = max(0, len(games) - 1)
            else:
                status_msg = "Sistema listo. Inserta una USB para agregar juegos."

        draw_menu(stdscr, games, selected, status_msg)

        key = stdscr.getch()

        if games:
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(games)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(games)
            elif key in (10, 13):
                launch_game(games[selected][2])

        if key in (ord("q"), ord("Q")):
            break

        pygame.event.pump()

        for event in pygame.event.get():
            if event.type == pygame.JOYHATMOTION and games:
                x, y = event.value

                if y == 1:
                    selected = (selected - 1) % len(games)
                elif y == -1:
                    selected = (selected + 1) % len(games)

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    if games:
                        launch_game(games[selected][2])

                elif event.button == 1:
                    return

        curses.napms(80)


if __name__ == "__main__":
    curses.wrapper(main)
