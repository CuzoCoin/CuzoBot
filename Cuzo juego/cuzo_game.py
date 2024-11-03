import pygame
import sys
import sqlite3
import webbrowser
import time
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla (tamaño de un teléfono)
WIDTH, HEIGHT = 375, 667
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cuzo - Tap to Earn")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
RED = (200, 0, 0)
LIGHT_RED = (255, 100, 100)
GREEN = (0, 200, 0)
LIGHT_GREEN = (100, 255, 100)

# Fuentes
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)  # Fuente más pequeña para el ID

# Estado del juego
game_state = "inicio"
background_image = None
wallet_connected = False
wallet_address = ""  # Dirección de la wallet
score = 0  # Inicializar puntuación
touches = 0  # Contador de toques
last_touch_time = 0  # Tiempo del último toque
hour_limit = 50  # Límite de toques por hora
time_window = 3600  # 3600 segundos = 1 hora
last_reward_time = 0  # Tiempo del último premio
show_confetti = False  # Bandera para mostrar confeti

# Estado de misiones
missions_completed = {
    "follow_x": False,
    "join_community": False,
    "join_telegram": False,
}

# Generar un ID único de 8 dígitos
def generate_unique_id():
    return ''.join(random.sample('0123456789', 8))  # Generar un ID de 8 dígitos

unique_id = generate_unique_id()  # Generar el ID al iniciar el juego

# Evento de confeti
CONFETTI_EVENT = pygame.USEREVENT + 1  # Crear un nuevo tipo de evento para el confeti

# Clases para botones y entradas de texto
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        draw_text(self.text, font, WHITE, screen, self.rect.centerx, self.rect.centery)

    def check_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            if self.action:
                self.action()

class TextInput:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = ""
        self.active = False

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        draw_text(self.text, font, WHITE, screen, self.rect.centerx, self.rect.centery)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activa o desactiva el campo de entrada
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            # Entrada de texto para la dirección de wallet
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

# Funciones para cambiar de pantalla
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def set_state_inicio():
    global game_state
    game_state = "inicio"

def set_state_misiones():
    global game_state
    game_state = "misiones"

def set_state_wallet():
    global game_state
    game_state = "wallet"

def open_link(url, mission_key):
    global score, missions_completed
    if not missions_completed[mission_key]:
        score += 1000  # Aumentar la puntuación en 1000 puntos
        missions_completed[mission_key] = True  # Marcar la misión como completada
    webbrowser.open(url)

def connect_wallet():
    global wallet_connected, wallet_address, score
    wallet_address = wallet_input.text  # Guardar la dirección de la wallet
    if wallet_address and not wallet_connected:
        wallet_connected = True  # Conectar la billetera si la dirección está ingresada
        score += 2000  # Agregar 2000 puntos al puntaje
        missions_completed["connect_wallet"] = True  # Marcar la misión de conexión de wallet como completada

def complete_mission(mission_key):
    global score, missions_completed
    if not missions_completed[mission_key]:
        score += 10  # Incrementar la puntuación en 10 al completar una misión
        missions_completed[mission_key] = True  # Marcar la misión como completada

def increase_score_with_touch():
    global score, touches, last_touch_time
    current_time = time.time()
    
    # Si ha pasado más de una hora desde el último toque, restablecer el contador
    if current_time - last_touch_time > time_window:
        touches = 0
    
    # Solo aumentar la puntuación si no se ha alcanzado el límite de toques
    if touches < hour_limit:
        score += 1
        touches += 1
        last_touch_time = current_time  # Actualizar el tiempo del último toque

def reward_daily_points():
    global score, last_reward_time, show_confetti
    current_time = time.time()

    # Verificar si han pasado 24 horas (86400 segundos) desde el último premio
    if current_time - last_reward_time >= 86400:
        score += 200  # Otorgar 200 puntos
        last_reward_time = current_time  # Actualizar el tiempo del último premio
        show_confetti = True  # Activar la animación de confeti
        pygame.time.set_timer(CONFETTI_EVENT, 2000)  # Configurar un temporizador de 2 segundos

def draw_confetti():
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(-20, HEIGHT)
        pygame.draw.circle(screen, (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)), (x, y), random.randint(2, 5))

def inicio():
    draw_background()
    draw_text("CUZO", big_font, WHITE, screen, WIDTH // 2, HEIGHT // 4)
    draw_text(f"Puntos: {score}", font, WHITE, screen, WIDTH // 2, HEIGHT // 4 + 50)  # Mostrar puntuación

    # Dibujar círculo transparente con solo contorno
    circle_x, circle_y = WIDTH // 2, HEIGHT // 2 + 50
    pygame.draw.circle(screen, WHITE, (circle_x, circle_y), 80, 2)  # Contorno transparente

    # Reorganizar botones en pantalla de inicio
    button_width, button_height = 250, 50
    button_y_start = HEIGHT // 2 + 120

    buttons = [
        Button("Missions", WIDTH // 2 - button_width // 2, button_y_start, button_width, button_height, GRAY, LIGHT_GRAY, set_state_misiones),
        Button("Wallet", WIDTH // 2 - button_width // 2, button_y_start + 60, button_width, button_height, GRAY, LIGHT_GRAY, set_state_wallet),
        Button("Quit", WIDTH // 2 - button_width // 2, button_y_start + 120, button_width, button_height, RED, LIGHT_RED, sys.exit)
    ]

    for button in buttons:
        button.draw()
        button.check_click()

    # Cargar y dibujar la imagen dentro del círculo (opcional)
    try:
        image_inside_circle = pygame.image.load('Imagenes/imagen_dentro_circulo.png').convert_alpha()
        image_resized = pygame.transform.scale(image_inside_circle, (160, 160))  # Ajustar tamaño de la imagen
        screen.blit(image_resized, (circle_x - 80, circle_y - 80))  # Centrar imagen dentro del círculo
    except Exception as e:
        print(f"No se pudo cargar la imagen: {e}")

    # Dibujar el ID único en la parte inferior derecha
    draw_text(f"ID: {unique_id}", small_font, WHITE, screen, WIDTH - 50, HEIGHT - 30)

def misiones():
    draw_background()
    draw_text("Misiones", big_font, WHITE, screen, WIDTH // 2, HEIGHT // 4)

    mission_buttons = [
        Button("Seguir a Cuzo", WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 50, GRAY, LIGHT_GRAY, lambda: open_link("https://twitter.com/cuzocoin", "follow_x")),
        Button("Unirse a la comunidad", WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 50, GRAY, LIGHT_GRAY, lambda: open_link("https://discord.gg/dxcVtC9d", "join_community")),
        Button("Subscribe to YouTube", WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 50, GRAY, LIGHT_GRAY, lambda: open_link("https://www.youtube.com/@CuzoCoin", "join_telegram"))
    ]

    for button in mission_buttons:
        button.draw()
        button.check_click()
        # Verificar si la misión está completada y dibujar un check
        if missions_completed["follow_x"] and button.text == "Seguir a Cuzo":
            draw_text("✓", font, GREEN, screen, button.rect.centerx + 80, button.rect.centery)  # Marcar con un check
        elif missions_completed["join_community"] and button.text == "Unirse a la comunidad":
            draw_text("✓", font, GREEN, screen, button.rect.centerx + 80, button.rect.centery)
        elif missions_completed["join_telegram"] and button.text == "Subscribe to YouTube":
            draw_text("✓", font, GREEN, screen, button.rect.centerx + 80, button.rect.centery)

    # Cargar y dibujar la flecha para regresar
    try:
        back_arrow = pygame.image.load('Imagenes/flecha_atras.png').convert_alpha()  # Asegúrate de tener esta imagen
        back_arrow = pygame.transform.scale(back_arrow, (50, 50))  # Ajustar tamaño de la flecha
        screen.blit(back_arrow, (10, 10))  # Dibujar la flecha en la esquina superior izquierda
    except Exception as e:
        print(f"No se pudo cargar la imagen de la flecha: {e}")

    # Dibujar el ID único en la parte inferior derecha
    draw_text(f"ID: {unique_id}", small_font, WHITE, screen, WIDTH - 50, HEIGHT - 30)

def wallet():
    draw_background()
    draw_text("Conectar Wallet", big_font, WHITE, screen, WIDTH // 2, HEIGHT // 4)

    # Cuadro de entrada para la dirección de wallet
    wallet_input.draw()
    
    # Botón de conectar
    connect_button = Button("Conectar Wallet", WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, GRAY, LIGHT_GRAY, connect_wallet)
    connect_button.draw()
    connect_button.check_click()

    # Verificar si la wallet está conectada
    if wallet_connected:
        draw_text("Conectada", font, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 150)
        draw_text("✓", font, GREEN, screen, WIDTH // 2 + 30, HEIGHT // 2 + 150)  # Marcar como completada
    else:
        draw_text("Desconectada", font, RED, screen, WIDTH // 2, HEIGHT // 2 + 150)

    # Cargar y dibujar la flecha para regresar
    try:
        back_arrow = pygame.image.load('Imagenes/flecha_atras.png').convert_alpha()  # Asegúrate de tener esta imagen
        back_arrow = pygame.transform.scale(back_arrow, (50, 50))  # Ajustar tamaño de la flecha
        screen.blit(back_arrow, (10, 10))  # Dibujar la flecha en la esquina superior izquierda
    except Exception as e:
        print(f"No se pudo cargar la imagen de la flecha: {e}")

    # Dibujar el ID único en la parte inferior derecha
    draw_text(f"ID: {unique_id}", small_font, WHITE, screen, WIDTH - 50, HEIGHT - 30)

# Lógica para regresar al inicio al hacer clic en la flecha
def check_arrow_click():
    mouse_pos = pygame.mouse.get_pos()
    if 10 <= mouse_pos[0] <= 60 and 10 <= mouse_pos[1] <= 60:  # Ajustar según el tamaño de la flecha
        set_state_inicio()

def draw_background():
    if background_image:
        # Redimensionar la imagen de fondo al tamaño de la pantalla
        resized_background = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        screen.blit(resized_background, (0, 0))
    else:
        screen.fill(BLACK)

def load_background(image_path):
    global background_image
    try:
        background_image = pygame.image.load(image_path).convert()
    except Exception as e:
        print(f"No se pudo cargar la imagen de fondo: {e}")

# Cargar fondo predeterminado al iniciar
load_background('Imagenes/wallet_background.png')  # Cambia esta línea para establecer un fondo predeterminado

# Cuadro de entrada de wallet
wallet_input = TextInput(WIDTH // 2 - 125, HEIGHT // 2 - 25, 250, 50, LIGHT_GRAY)

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == CONFETTI_EVENT:
            show_confetti = False  # Desactivar el confeti después de 2 segundos
            pygame.time.set_timer(CONFETTI_EVENT, 0)  # Desactivar el temporizador
        elif event.type == pygame.KEYDOWN:
            # Cambia el fondo en cada pantalla con la tecla '1'
            if event.key == pygame.K_1:
                if game_state == "inicio":
                    load_background('Imagenes/wallet_background.png')
                elif game_state == "misiones":
                    load_background('Imagenes/wallet_background.png')
                elif game_state == "wallet":
                    load_background('Imagenes/wallet_background.png')

        wallet_input.handle_event(event)

        # Incrementar la puntuación al tocar el círculo
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            circle_x, circle_y = WIDTH // 2, HEIGHT // 2 + 50
            if (circle_x - 80 <= mouse_pos[0] <= circle_x + 80) and (circle_y - 80 <= mouse_pos[1] <= circle_y + 80):
                increase_score_with_touch()
            
            # Comprobar clic en la flecha para regresar al inicio
            check_arrow_click()

    # Otorgar puntos diariamente
    reward_daily_points()

    # Dibujar la pantalla según el estado del juego
    if game_state == "inicio":
        inicio()
        if show_confetti:
            draw_confetti()
    
    elif game_state == "misiones":
        misiones()
    elif game_state == "wallet":
        wallet()

    pygame.display.flip()

pygame.quit()
