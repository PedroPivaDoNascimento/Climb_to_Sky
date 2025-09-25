import pgzrun
import math
from pygame.rect import Rect

# --- Configurações da Janela e do Mundo ---
WIDTH = 800
HEIGHT = 600
level_width = 800
level_height = 4000

# --- Constantes do Jogo ---
GRAVITY = 0.5
PLAYER_SPEED = 5
JUMP_SPEED = -16
ENEMY_SPEED = 2
ANIMATION_SPEED = 40

# --- Variáveis do Jogo ---
game_over = False
win_game = False
camera_y = 0
game_state = 'MENU'
start_button = Rect(WIDTH/2 - 120, HEIGHT/2 - 50, 240, 60)
tutorial_button = Rect(WIDTH/2 - 120, HEIGHT/2 + 15, 240, 60)
music_button = Rect(WIDTH/2 - 120, HEIGHT/2 + 80, 240, 60)
exit_button = Rect(WIDTH/2 - 120, HEIGHT/2 + 145, 240, 60)
close_button = Rect(WIDTH/2 - 80, HEIGHT/2 + 200, 160, 50)
mouse_pos = (0, 0)
music_is_playing = True
victory_music_played = False
lose_music_played = False

# A imagem de fundo que se repete é o céu
bg_tile = images.sky_bg
bg_tile_width = bg_tile.get_width()
bg_tile_height = bg_tile.get_height()

# --- Classes de Atores ---
class Player(Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.is_alive = True

        # Lista de imagens para cada animação do jogador
        self.idle_images = ['character/pose_idle1_segundaversao', 'character/pose_idle2_segundaversao',
                            'character/pose_idle3_segundaversao', 'character/pose_idle4_segundaversao',
                            'character/pose_idle5_segundaversao']
        self.walking_images = ['character/pose_walking1', 'character/pose_walking2',
                               'character/pose_walking3']
        self.jumping_images = ['character/pose_jumping1', 'character/pose_jumping2',
                               'character/pose_jumping3', 'character/pose_jumping4']

        self.current_animation = self.idle_images
        self.animation_frame = 0
        self.animation_timer = 0
        self.image = self.idle_images[0]

    def update(self):
        if not self.is_alive:
            return

        # Movimento horizontal
        if keyboard.left:
            self.velocity_x = -PLAYER_SPEED
        elif keyboard.right:
            self.velocity_x = PLAYER_SPEED
        else:
            self.velocity_x = 0

        # Pulo
        if keyboard.up and self.on_ground:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False
            if music_is_playing:
                sounds.jump_sound.play()

        # Lógica de animação
        previous_animation = self.current_animation

        if not self.on_ground and abs(self.velocity_y) > 0.1:
            # Animação de pulo
            self.current_animation = self.jumping_images
        elif self.velocity_x != 0:
            # Animação de caminhada
            self.current_animation = self.walking_images
        else:
            # Animação idle (parado)
            self.current_animation = self.idle_images

        # Reseta o frame se a animação mudou
        if self.current_animation != previous_animation:
            self.animation_frame = 0

        # Atualiza o frame da animação atual
        self.animation_timer += 1
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.current_animation)

        self.image = self.current_animation[self.animation_frame]

        self.x += self.velocity_x

        if not self.on_ground:
            self.velocity_y += GRAVITY
        self.y += self.velocity_y

        if self.x < 0:
            self.x = 0
        if self.right > level_width:
            self.right = level_width

    def draw(self):
        screen.blit(self.image, (self.x, self.y - camera_y))

class Enemy(Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.velocity_x = -ENEMY_SPEED
        self.is_alive = True

        # Animação de troca de cor
        self.enemy_images = ['enemy/enemy_green', 'enemy/enemy_red']
        self.animation_frame = 0
        self.animation_timer = 0
        self.image = self.enemy_images[0]

    def update(self):
        if not self.is_alive:
            return

        # Atualiza a animação de troca de cor
        self.animation_timer += 1
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.enemy_images)
        self.image = self.enemy_images[self.animation_frame]

        # Movimento horizontal
        self.x += self.velocity_x
        if self.left < 0 or self.right > level_width:
            self.velocity_x *= -1

    def draw(self):
        if self.is_alive:
            screen.blit(self.image, (self.x, self.y - camera_y))

class Block(Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60)
        self.image = 'blocks/ground_block'

    def draw(self):
        screen.blit(self.image, (self.x, self.y - camera_y))

# --- Funções de Gerenciamento do Jogo ---
def reset_game():
    global game_over, win_game, camera_y, player, enemies, platforms, final_platforms, game_state, music_is_playing, victory_music_played, lose_music_played
    game_over = False
    win_game = False
    camera_y = 0
    game_state = 'PLAYING'
    victory_music_played = False
    lose_music_played = False

    music.stop()
    if music_is_playing:
        music.play('back_ground_music')

    player = Player(WIDTH / 2, level_height - 100)

    initial_ground = []

    ground_width = 60
    num_blocks = math.ceil(WIDTH / ground_width)
    for i in range(num_blocks):
        initial_ground.append(Block(i * ground_width, level_height - 40))

    final_platforms = []
    for i in range(5):
        final_platforms.append(Block(250 + i * 60, 100))

    platforms = initial_ground + [
        Block(300, level_height - 150),
        Block(500, level_height - 250),
        Block(100, level_height - 350),
        Block(600, level_height - 450),
        Block(250, level_height - 550),
        Block(450, level_height - 650),
        Block(50, level_height - 750),
        Block(700, level_height - 850),
        Block(300, level_height - 950),
        Block(500, level_height - 1050),
        Block(150, level_height - 1150),
        Block(650, level_height - 1250),
        Block(200, level_height - 1350),
        Block(550, level_height - 1450),
        Block(50, level_height - 1550),
        Block(400, level_height - 1650),
        Block(700, level_height - 1750),
        Block(300, level_height - 1850),
        Block(500, level_height - 1950),
        Block(100, level_height - 2050),
        Block(600, level_height - 2150),
        Block(350, level_height - 2250),
        Block(50, level_height - 2350),
        Block(400, level_height - 2450),
        Block(150, level_height - 2550),
        Block(650, level_height - 2650),
        Block(200, level_height - 2750),
        Block(550, level_height - 2850),
        Block(50, level_height - 2950),
        Block(400, level_height - 3050),
        Block(700, level_height - 3150),
        Block(300, level_height - 3250),
        Block(500, level_height - 3350),
        Block(100, level_height - 3450),
        Block(600, level_height - 3550),
        Block(350, level_height - 3650),
        Block(250, level_height - 3750),
        Block(450, level_height - 3850),
    ] + final_platforms

    enemies = [
        Enemy(500, level_height - 500),
        Enemy(150, level_height - 900),
        Enemy(600, level_height - 1300),
        Enemy(350, level_height - 1800),
        Enemy(100, level_height - 2200),
        Enemy(500, level_height - 2700),
        Enemy(300, level_height - 3100),
        Enemy(500, level_height - 3700)
    ]

def start_game():
    global game_state
    game_state = 'PLAYING'
    reset_game()

def start_tutorial():
    global game_state
    game_state = 'TUTORIAL'

def on_mouse_down(pos):
    global game_state, music_is_playing
    if game_state == 'MENU':
        if start_button.collidepoint(pos):
            start_game()
        elif tutorial_button.collidepoint(pos):
            start_tutorial()
        elif music_button.collidepoint(pos):
            if music_is_playing:
                music.pause()
                music_is_playing = False
            else:
                music.play('back_ground_music')
                music_is_playing = True
        elif exit_button.collidepoint(pos):
            quit()
    elif game_state == 'TUTORIAL':
        if close_button.collidepoint(pos):
            game_state = 'MENU'
    elif (game_over or win_game) and start_button.collidepoint(pos):
        start_game()

def on_key_down(key):
    global game_over, win_game, game_state

    if key == keys.M and game_state == 'PLAYING':
        music.stop()
        if music_is_playing:
            music.play('back_ground_music')
        game_state = 'MENU'

    if (game_over or win_game) and key == keys.SPACE:
        start_game()

def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos

def update():
    global game_over, win_game, camera_y, game_state, victory_music_played, lose_music_played

    if game_state == 'TUTORIAL':
        return

    if game_state != 'PLAYING':
        return

    if win_game:
        if music_is_playing and not victory_music_played:
            music.stop()
            music.play('victory_music')
            victory_music_played = True
        return

    if game_over:
        if music_is_playing and not lose_music_played:
            music.stop()
            music.play('lose_music')
            lose_music_played = True
        return

    player.update()

    player.on_ground = False

    for p in platforms:
        if player.colliderect(p):
            if player.velocity_y >= 0 and player.bottom <= p.top + player.velocity_y + 5:
                if p in final_platforms:
                    win_game = True

                player.bottom = p.top
                player.velocity_y = 0
                player.on_ground = True

            elif player.velocity_y < 0 and player.top >= p.bottom - 5:
                player.top = p.bottom
                player.velocity_y = 0

    for enemy in enemies:
        enemy.update()
        if enemy.is_alive and player.colliderect(enemy):
            game_over = True
            player.is_alive = False

    camera_y = player.y - HEIGHT / 2
    if camera_y < 0:
        camera_y = 0
    if camera_y > level_height - HEIGHT:
        camera_y = level_height - HEIGHT

    if player.y - camera_y > HEIGHT:
        game_over = True
        player.is_alive = False

def draw():
    # Desenha o fundo em todas as telas
    screen.clear()
    y_start_pos = -camera_y % bg_tile_height
    num_tiles_vertical = math.ceil(HEIGHT / bg_tile_height) + 1
    num_tiles_horizontal = math.ceil(WIDTH / bg_tile_width) + 1

    for i in range(-num_tiles_vertical, num_tiles_vertical):
        for j in range(num_tiles_horizontal):
            x_pos = j * bg_tile_width
            y_pos = y_start_pos + i * bg_tile_height
            screen.blit(bg_tile, (x_pos, y_pos))

    if game_state == 'MENU':
        screen.draw.text("Climbing to Sky", center=(WIDTH/2, HEIGHT/2 - 100), fontsize=60, fontname="8bitoperatorplus8-regular.ttf", color='black')

        # Desenha os botões
        start_button_color = (255, 255, 255)
        if start_button.collidepoint(mouse_pos):
            start_button_color = (200, 200, 200)
        screen.draw.filled_rect(start_button, start_button_color)
        screen.draw.text("COMEÇAR", center=start_button.center, fontsize=40, fontname="8bitoperatorplus8-regular.ttf", color='black')

        tutorial_button_color = (255, 255, 255)
        if tutorial_button.collidepoint(mouse_pos):
            tutorial_button_color = (200, 200, 200)
        screen.draw.filled_rect(tutorial_button, tutorial_button_color)
        screen.draw.text("TUTORIAL", center=tutorial_button.center, fontsize=40, fontname="8bitoperatorplus8-regular.ttf", color='black')

        music_button_color = (255, 255, 255)
        if music_button.collidepoint(mouse_pos):
            music_button_color = (200, 200, 200)
        screen.draw.filled_rect(music_button, music_button_color)
        music_text = "SOM: ON" if music_is_playing else "SOM: OFF"
        screen.draw.text(music_text, center=music_button.center, fontsize=40, fontname="8bitoperatorplus8-regular.ttf", color='black')

        exit_button_color = (255, 255, 255)
        if exit_button.collidepoint(mouse_pos):
            exit_button_color = (200, 200, 200)
        screen.draw.filled_rect(exit_button, exit_button_color)
        screen.draw.text("SAIR", center=exit_button.center, fontsize=40, fontname="8bitoperatorplus8-regular.ttf", color='black')

    elif game_state == 'TUTORIAL':
        screen.draw.text("Mova-se com as setas. Pressione M para abrir o menu.", center=(WIDTH/2, HEIGHT/2), fontsize=25, fontname="8bitoperatorplus8-regular.ttf", color='white')

        close_button_color = (255, 255, 255)
        if close_button.collidepoint(mouse_pos):
            close_button_color = (200, 200, 200)
        screen.draw.filled_rect(close_button, close_button_color)
        screen.draw.text("FECHAR", center=close_button.center, fontsize=25, fontname="8bitoperatorplus8-regular.ttf", color='black')

    elif game_over:
        screen.draw.text("FIM DE JOGO", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=60, fontname="8bitoperatorplus8-regular.ttf", color='red')
        screen.draw.text("Pressione ESPAÇO para Jogar Novamente", center=(WIDTH/2, HEIGHT/2), fontsize=30, fontname="8bitoperatorplus8-regular.ttf", color='black')

    elif win_game:
        screen.draw.text("VOCÊ VENCEU!", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=60, fontname="8bitoperatorplus8-regular.ttf", color='green')
        screen.draw.text("Pressione ESPAÇO para Jogar Novamente", center=(WIDTH/2, HEIGHT/2), fontsize=30, fontname="8bitoperatorplus8-regular.ttf", color='black')

    elif game_state == 'PLAYING':
        player.draw()
        for p in platforms:
            p.draw()
        for enemy in enemies:
            enemy.draw()

# --- Inicialização ---
enemies = []
platforms = []
final_platforms = []
player = None

# A música toca a partir do início do script
music.play('back_ground_music')

pgzrun.go()