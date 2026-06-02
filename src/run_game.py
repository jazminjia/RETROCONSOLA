import sys
import subprocess
import os
import pygame
import time

if len(sys.argv) < 2:
    sys.exit(1)

rom_path = sys.argv[1]

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()


def usb_devices():
    result = subprocess.run(
        "lsblk -rpno NAME,TRAN,TYPE | awk '$2==\"usb\" && $3==\"disk\" {print $1\"1\"}'",
        shell=True, capture_output=True, text=True
    )
    return set(result.stdout.strip().splitlines())


initial_usb = usb_devices()

mednafen_env = os.environ.copy()
mednafen_env.pop("SDL_VIDEODRIVER", None)
mednafen_env.pop("PYGAME_HIDE_SUPPORT_PROMPT", None)

process = subprocess.Popen(
    ["/usr/games/mednafen", rom_path],
    env=mednafen_env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

view_pressed = False
menu_pressed = False
last_usb_check = 0

while process.poll() is None:
    now = time.time()
    pygame.event.pump()

    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 6:
                view_pressed = True
            elif event.button == 7:
                menu_pressed = True
        elif event.type == pygame.JOYBUTTONUP:
            if event.button == 6:
                view_pressed = False
            elif event.button == 7:
                menu_pressed = False

    if view_pressed and menu_pressed:
        process.terminate()
        time.sleep(0.5)
        if process.poll() is None:
            process.kill()
        pygame.quit()
        sys.exit(0)

    if now - last_usb_check > 1:
        current_usb = usb_devices()
        last_usb_check = now
        if current_usb - initial_usb:
            process.terminate()
            time.sleep(0.5)
            if process.poll() is None:
                process.kill()
            pygame.quit()
            sys.exit(20)

    time.sleep(0.05)

pygame.quit()
sys.exit(0)
