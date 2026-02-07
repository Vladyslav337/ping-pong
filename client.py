from pygame import *
import socket
import json
from threading import Thread

# --- ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")

# --- ЗОБРАЖЕННЯ ---
background = image.load("background.png")
background = transform.scale(background, (WIDTH, HEIGHT))

# --- СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break


# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)

# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()

while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    # Відлік
    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.blit(background, (0, 0))
        countdown_text = font.Font(None, 72).render(
            str(game_state["countdown"]), True, (255, 255, 255)
        )
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue

    # Перемога
    if "winner" in game_state and game_state["winner"] is not None:
        screen.blit(background, (0, 0))

        if you_winner is None:
            you_winner = game_state["winner"] == my_id

        text = "Ти переміг!" if you_winner else "Пощастить наступним разом!"
        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        restart_text = font_win.render("К - рестарт", True, (255, 215, 0))
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(restart_text, restart_rect)

        display.update()
        continue

    # Гра
    if game_state:
        screen.blit(background, (0, 0))

        draw.rect(screen, (0, 255, 0),
                  (20, game_state['paddles']['0'], 20, 100))
        draw.rect(screen, (255, 0, 255),
                  (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        draw.circle(screen, (255, 255, 255),
                    (game_state['ball']['x'], game_state['ball']['y']), 10)

        score_text = font_main.render(
            f"{game_state['scores'][0]} : {game_state['scores'][1]}",
            True, (255, 255, 255)
        )
        screen.blit(score_text, (WIDTH // 2 - 25, 20))
    else:
        waiting_text = font_main.render(
            "Очікування гравців...", True, (255, 255, 255)
        )
        screen.blit(waiting_text, (WIDTH // 2 - 120, 20))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
