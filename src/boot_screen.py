import subprocess
import time
from PIL import Image

def show_image():
    img = Image.open("/home/pi/retroconsola/assets/LOGO.png")
    img = img.resize((1024, 600))
    img = img.convert("RGB")
    pixels = list(img.getdata())

    rgb565 = bytearray()
    for r, g, b in pixels:
        color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        rgb565 += color.to_bytes(2, 'little')

    with open("/dev/fb0", "wb") as fb:
        fb.write(rgb565)

def main():
    show_image()

    audio_proc = subprocess.Popen(
        ["sudo", "-u", "pi", "cvlc", "--aout=alsa", "--no-video", "--play-and-exit",
         "/home/pi/retroconsola/assets/FNAF8BIT.ogg"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    audio_proc.wait()

    # Limpia framebuffer
    with open("/dev/fb0", "wb") as fb:
        fb.write(b'\x00' * (1024 * 600 * 2))

if __name__ == "__main__":
    main()
