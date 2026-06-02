import os
import time
import subprocess

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1024
HEIGHT = 600

BASE_DIR = "/home/pi/retroconsola/roms"
USB_MOUNT = "/home/pi/retroconsola/usb"
ASSETS = "/home/pi/retroconsola/assets"
RUN_GAME = "/home/pi/retroconsola/src/run_game.py"

FOLDERS = {
    "NES": f"{BASE_DIR}/nes",
    "SNES": f"{BASE_DIR}/snes",
    "GBA": f"{BASE_DIR}/gba",
}

EXTS = (".nes", ".sfc", ".smc", ".gba", ".gb", ".gbc")


def font(size, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    return ImageFont.truetype(path, size)


FONT_TITLE = font(54, True)
FONT_SUB   = font(22)
FONT_ITEM  = font(24, True)
FONT_SMALL = font(18)


def write_fb(img):
    img = img.resize((WIDTH, HEIGHT)).convert("RGB")
    rgb565 = bytearray()
    for r, g, b in img.getdata():
        color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        rgb565 += color.to_bytes(2, "little")
    with open("/dev/fb0", "wb") as fb:
        fb.write(rgb565)


def play_sound(path):
    if os.path.exists(path):
        subprocess.Popen(
            ["aplay", "-q", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def get_games():
    games = []
    for system, folder in FOLDERS.items():
        os.makedirs(folder, exist_ok=True)
        for name in sorted(os.listdir(folder)):
            if name.lower().endswith(EXTS):
                games.append((system, name, os.path.join(folder, name)))
    return games


def get_usb_partition():
    result = subprocess.run(
        "lsblk -rpno NAME,TRAN,TYPE | awk '$2==\"usb\" && $3==\"disk\" {print $1\"1\"}' | head -n 1",
        shell=True, capture_output=True, text=True
    )
    usb_dev = result.stdout.strip()
    return usb_dev if usb_dev else None


def usb_connected():
    return get_usb_partition() is not None


def mount_usb():
    os.makedirs(USB_MOUNT, exist_ok=True)
    if subprocess.run(["mountpoint", "-q", USB_MOUNT]).returncode == 0:
        return True
    usb_dev = get_usb_partition()
    if not usb_dev:
        return False
    result = subprocess.run(
        ["mount", usb_dev, USB_MOUNT],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def umount_usb():
    if subprocess.run(["mountpoint", "-q", USB_MOUNT]).returncode != 0:
        return
    if not usb_connected():
        subprocess.run(["umount", USB_MOUNT],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def scan_usb_and_copy():
    if not mount_usb():
        return []
    copied = []
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
            if not os.path.exists(dst):
                result = subprocess.run(
                    ["cp", src, dst],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                if result.returncode == 0:
                    copied.append(dst)
    return copied


def launch_game(path):
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    write_fb(img)
    play_sound(f"{ASSETS}/SELECCIONSOUND.wav")
    time.sleep(0.4)
    result = subprocess.run(
        ["python3", RUN_GAME, path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    pygame.event.clear()
    time.sleep(0.5)
    return result.returncode


def clean_name(filename):
    name = os.path.splitext(filename)[0]
    return name


def draw_menu(games, selected, status, new_games):
    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 222, 238))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        r = 255
        g = 220 + int(20 * y / HEIGHT)
        b = min(255, 238 + int(12 * y / HEIGHT))
        draw.line((0, y, WIDTH, y), fill=(r, g, b))

    draw.rounded_rectangle((45, 35, 979, 565), radius=28,
                            fill=(255, 245, 250), outline=(219, 94, 154), width=5)

    title = "KAWAIIBOX 360 UWU"
    tw = draw.textlength(title, font=FONT_TITLE)
    draw.text(((WIDTH - tw) // 2, 55), title, font=FONT_TITLE, fill=(150, 45, 105))

    subtitle = "D-PAD: mover   A: jugar   B: salir   VIEW+MENU: salir del juego"
    sw = draw.textlength(subtitle, font=FONT_SUB)
    draw.text(((WIDTH - sw) // 2, 122), subtitle, font=FONT_SUB, fill=(130, 70, 110))

    draw.rounded_rectangle((90, 165, 934, 500), radius=22,
                            fill=(255, 232, 244), outline=(239, 151, 194), width=3)

    if not games:
        msg = "No hay ROMS disponibles"
        mw = draw.textlength(msg, font=FONT_ITEM)
        draw.text(((WIDTH - mw) // 2, 300), msg, font=FONT_ITEM, fill=(130, 70, 110))
    else:
        visible = 8
        offset = max(0, selected - visible // 2)
        for i, game in enumerate(games[offset:offset + visible]):
            real_i = offset + i
            system, name, path = game
            y = 185 + i * 38
            x = 120
            if real_i == selected:
                draw.rounded_rectangle((105, y - 4, 918, y + 32), radius=14,
                                       fill=(255, 167, 210), outline=(196, 68, 135), width=3)
                color = (95, 35, 80)
                prefix = "> "
            else:
                color = (135, 75, 115)
                prefix = "  "

            display_name = clean_name(name)
            if path in new_games:
                display_name += "  ★ NEW"
            if len(display_name) > 42:
                display_name = display_name[:39] + "..."

            text = f"{prefix}[{system}] {display_name}"
            draw.text((x, y), text, font=FONT_ITEM, fill=color)

    draw.rounded_rectangle((90, 515, 934, 545), radius=12, fill=(255, 214, 234))
    draw.text((110, 520), status[:70], font=FONT_SMALL, fill=(120, 50, 95))

    footer = "Inserta una USB para agregar ROMS automaticamente"
    fw = draw.textlength(footer, font=FONT_SMALL)
    draw.text(((WIDTH - fw) // 2, 560), footer, font=FONT_SMALL, fill=(120, 50, 95))

    write_fb(img)


def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()

    games = get_games()
    new_games = set()
    selected = 0
    status = f"Juegos disponibles: {len(games)}"
    last_usb_scan = 0
    last_move = 0
    running = True

    while running:
        now = time.time()

        if now - last_usb_scan > 2:
            umount_usb()
            copied = scan_usb_and_copy()
            last_usb_scan = now
            if copied:
                new_games.update(copied)
                games = get_games()
                status = f"Se agregaron {len(copied)} ROMs nuevas desde USB."
                play_sound(f"{ASSETS}/USBSOUND.wav")
                if selected >= len(games):
                    selected = max(0, len(games) - 1)
            else:
                status = f"Juegos disponibles: {len(games)}"

        draw_menu(games, selected, status, new_games)
        pygame.event.pump()

        for event in pygame.event.get():
            if event.type == pygame.JOYHATMOTION and games:
                x, y = event.value
                if time.time() - last_move > 0.04:
                    if y == 1:
                        selected = (selected - 1) % len(games)
                        last_move = time.time()
                        play_sound(f"{ASSETS}/DPADSOUND.wav")
                    elif y == -1:
                        selected = (selected + 1) % len(games)
                        last_move = time.time()
                        play_sound(f"{ASSETS}/DPADSOUND.wav")

            elif event.type == pygame.JOYAXISMOTION and games:
                if event.axis == 1 and time.time() - last_move > 0.06:
                    if event.value < -0.7:
                        selected = (selected - 1) % len(games)
                        last_move = time.time()
                        play_sound(f"{ASSETS}/DPADSOUND.wav")
                    elif event.value > 0.7:
                        selected = (selected + 1) % len(games)
                        last_move = time.time()
                        play_sound(f"{ASSETS}/DPADSOUND.wav")

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0 and games:
                    code = launch_game(games[selected][2])
                    # Si run_game salió por USB (código 20), copia ROMs
                    if code == 20:
                        copied = scan_usb_and_copy()
                        if copied:
                            new_games.update(copied)
                            games = get_games()
                            status = f"Se agregaron {len(copied)} ROMs nuevas desde USB."
                            play_sound(f"{ASSETS}/USBSOUND.wav")
                    else:
                        games = get_games()

                elif event.button == 1:
                    play_sound(f"{ASSETS}/SALIDASOUND.wav")
                    time.sleep(0.4)
                    running = False

        time.sleep(0.01)

    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    write_fb(img)
    pygame.quit()


if __name__ == "__main__":
    main()
