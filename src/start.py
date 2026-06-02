import subprocess
import time

# Cambia a tty2 y limpia pantalla
subprocess.run(["chvt", "2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["clear"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

# Muestra logo y música
subprocess.run(
    ["python3", "/home/pi/retroconsola/src/boot_screen.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Limpia pantalla antes del menú
subprocess.run(["clear"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.3)

# Arranca menú
subprocess.run(
    ["python3", "/home/pi/retroconsola/src/menu_terminal.py"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
