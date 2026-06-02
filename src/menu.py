import os
import subprocess
import pygame
import sys

BASE_DIR = "/home/pi/retroconsola/roms"

ROM_FOLDERS = {
    "NES": os.path.join(BASE_DIR, "nes"),
    "SNES": os.path.join(BASE_DIR, "snes"),
    "GBA": os.path.join(BASE_DIR, "gba"),
}

VALID_EXTENSIONS = (".nes", ".sfc", ".smc", ".gba", ".gb", ".gbc")

# Colores pastel
BG = (255, 230, 242)
PANEL = (255, 245, 250)
TEXT = (120, 60, 90)
SELECTED = (255, 170, 210)
BORDER = (230, 120, 180)
WHITE = (255, 255, 255)

pygame.init()
pygame.joystick.init()

screen = pygame.display.set_mode((800, 480))
pygame.display.set_caption("RetroConsola")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("dejavusans", 48, bold=True)
font_menu = pygame.font.SysFont("dejavusans", 30)
font_small = pygame.font.SysFont("dejavusans", 22)

selected = 0


def load_games():
    games = []

    for system, folder in ROM_FOLDERS.items():
        if not os.path.exists(folder):
            continue

        for file in sorted(os.listdir(folder)):
            if file.lower().endswith(VALID_EXTENSIONS):
                games.append({
                    "name": file,
                    "system": system,
                    "path": os.path.join(folder, file)
                })

    return games


games = load_games()


def draw_menu():
    screen.fill(BG)

    title = font_title.render("♡ RetroConsola ♡", True, TEXT)
    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 60)))

    subtitle = font_small.render("Usa el D-pad para moverte | A para jugar | B para salir", True, TEXT)
    screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, 110)))

    if not games:
        msg = font_menu.render("No hay ROMS disponibles", True, TEXT)
        screen.blit(msg, msg.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))
        pygame.display.flip()
        return

    start_y = 160
    item_h = 48
    visible_items = 10

    offset = max(0, selected - visible_items // 2)

    for i, game in enumerate(games[offset:offset + visible_items]):
        real_index = offset + i
        y = start_y + i * item_h

        rect = pygame.Rect(90, y, screen.get_width() - 180, item_h - 8)

        if real_index == selected:
            pygame.draw.rect(screen, SELECTED, rect, border_radius=18)
            pygame.draw.rect(screen, BORDER, rect, 3, border_radius=18)
        else:
            pygame.draw.rect(screen, PANEL, rect, border_radius=18)

        text = f"[{game['system']}] {game['name']}"
        label = font_menu.render(text, True, TEXT)
        screen.blit(label, (rect.x + 20, rect.y + 8))

    pygame.display.flip()


def launch_game(path):
    pygame.display.quit()
    pygame.quit()

    subprocess.run(["mednafen", path])

    os.execv(sys.executable, [sys.executable] + sys.argv)


def main():
    global selected

    while True:
        draw_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(games)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(games)
                elif event.key == pygame.K_RETURN:
                    launch_game(games[selected]["path"])
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.JOYHATMOTION:
                x, y = event.value

                if y == 1:
                    selected = (selected - 1) % len(games)
                elif y == -1:
                    selected = (selected + 1) % len(games)

            if event.type == pygame.JOYBUTTONDOWN:
                # Xbox: A normalmente es botón 0
                if event.button == 0:
                    launch_game(games[selected]["path"])

                # Xbox: B normalmente es botón 1
                elif event.button == 1:
                    pygame.quit()
                    sys.exit()

        clock.tick(30)


if __name__ == "__main__":
    if pygame.joystick.get_count() > 0:
        pygame.joystick.Joystick(0).init()

    main()
