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
tutorial_timer = 0

# A imagem de fundo que se repete é o céu
bg_tile = images.sky_bg
bg_tile_width = bg_tile.get_width()
bg_tile_height = bg_tile.get_height()

# --- Classes de Atores ---
class Jogador(Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60)
        self.velocidade_x = 0
        self.velocidade_y = 0
        self.no_chao = False
        self.vivo = True

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
        if not self.vivo:
            return

        # Movimento horizontal
        if keyboard.left:
            self.velocidade_x = -PLAYER_SPEED
        elif keyboard.right:
            self.velocidade_x = PLAYER_SPEED
        else:
            self.velocidade_x = 0

        # Pulo
        if keyboard.up and self.no_chao:
            self.velocidade_y = JUMP_SPEED
            self.no_chao = False
            if music_is_playing:
                sounds.jump_sound.play()

        # Lógica de animação
        previous_animation = self.current_animation

        if not self.no_chao and abs(self.velocidade_y) > 0.1:
            # Animação de pulo
            self.current_animation = self.jumping_images
        elif self.velocidade_x != 0:
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

        self.x += self.velocidade_x

        if not self.no_chao:
            self.velocidade_y += GRAVITY
        self.y += self.velocidade_y

        if self.x < 0:
            self.x = 0
        if self.right > level_width:
            self.right = level_width

    def draw(self):
        screen.blit(self.image, (self.x, self.y - camera_y))

class Inimigo(Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.velocidade_x = -ENEMY_SPEED
        self.vivo = True

        # Animação de troca de cor
        self.enemy_images = ['enemy/enemy_green', 'enemy/enemy_red']
        self.animation_frame = 0
        self.animation_timer = 0
        self.image = self.enemy_images[0]

    def update(self, plataformas):
        if not self.vivo:
            return

        # Atualiza a animação de troca de cor
        self.animation_timer += 1
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.enemy_images)
        self.image = self.enemy_images[self.animation_frame]

        # Movimento horizontal
        self.x += self.velocidade_x
        if self.left < 0 or self.right > level_width:
            self.velocidade_x *= -1

    def draw(self):
        if self.vivo:
            screen.blit(self.image, (self.x, self.y - camera_y))

class Bloco(Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60)
        self.image = 'blocks/ground_block'

    def draw(self):
        screen.blit(self.image, (self.x, self.y - camera_y))

# --- Funções de Gerenciamento do Jogo ---
def reset_game():
    global game_over, win_game, camera_y, jogador, inimigos, plataformas, plataformas_finais, game_state, music_is_playing, victory_music_played, lose_music_played
    game_over = False
    win_game = False
    camera_y = 0
    game_state = 'PLAYING'
    victory_music_played = False
    lose_music_played = False

    music.stop()
    if music_is_playing:
        music.play('back_ground_music')

    jogador = Jogador(WIDTH / 2, level_height - 100)

    chao_inicial = []

    largura_terreno = 60
    num_blocos = math.ceil(WIDTH / largura_terreno)
    for i in range(num_blocos):
        chao_inicial.append(Bloco(i * largura_terreno, level_height - 40))

    plataformas_finais = []
    for i in range(5):
        plataformas_finais.append(Bloco(250 + i * 60, 100))

    plataformas = chao_inicial + [
        Bloco(300, level_height - 150),
        Bloco(500, level_height - 250),
        Bloco(100, level_height - 350),
        Bloco(600, level_height - 450),
        Bloco(250, level_height - 550),
        Bloco(450, level_height - 650),
        Bloco(50, level_height - 750),
        Bloco(700, level_height - 850),
        Bloco(300, level_height - 950),
        Bloco(500, level_height - 1050),
        Bloco(150, level_height - 1150),
        Bloco(650, level_height - 1250),
        Bloco(200, level_height - 1350),
        Bloco(550, level_height - 1450),
        Bloco(50, level_height - 1550),
        Bloco(400, level_height - 1650),
        Bloco(700, level_height - 1750),
        Bloco(300, level_height - 1850),
        Bloco(500, level_height - 1950),
        Bloco(100, level_height - 2050),
        Bloco(600, level_height - 2150),
        Bloco(350, level_height - 2250),
        Bloco(50, level_height - 2350),
        Bloco(400, level_height - 2450),
        Bloco(150, level_height - 2550),
        Bloco(650, level_height - 2650),
        Bloco(200, level_height - 2750),
        Bloco(550, level_height - 2850),
        Bloco(50, level_height - 2950),
        Bloco(400, level_height - 3050),
        Bloco(700, level_height - 3150),
        Bloco(300, level_height - 3250),
        Bloco(500, level_height - 3350),
        Bloco(100, level_height - 3450),
        Bloco(600, level_height - 3550),
        Bloco(350, level_height - 3650),
        Bloco(250, level_height - 3750),
        Bloco(450, level_height - 3850),
    ] + plataformas_finais

    inimigos = [
        Inimigo(500, level_height - 500),
        Inimigo(150, level_height - 900),
        Inimigo(600, level_height - 1300),
        Inimigo(350, level_height - 1800),
        Inimigo(100, level_height - 2200),
        Inimigo(500, level_height - 2700),
        Inimigo(300, level_height - 3100),
        Inimigo(500, level_height - 3700)
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

    jogador.update()

    jogador.no_chao = False

    for p in plataformas:
        if jogador.colliderect(p):
            if jogador.velocidade_y >= 0 and jogador.bottom <= p.top + jogador.velocidade_y + 5:
                if p in plataformas_finais:
                    win_game = True

                jogador.bottom = p.top
                jogador.velocidade_y = 0
                jogador.no_chao = True

            elif jogador.velocidade_y < 0 and jogador.top >= p.bottom - 5:
                jogador.top = p.bottom
                jogador.velocidade_y = 0

    for inimigo in inimigos:
        inimigo.update(plataformas)
        if inimigo.vivo and jogador.colliderect(inimigo):
            game_over = True
            jogador.vivo = False

    camera_y = jogador.y - HEIGHT / 2
    if camera_y < 0:
        camera_y = 0
    if camera_y > level_height - HEIGHT:
        camera_y = level_height - HEIGHT

    if jogador.y - camera_y > HEIGHT:
        game_over = True
        jogador.vivo = False

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
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=60, fontname="8bitoperatorplus8-regular.ttf", color='red')
        screen.draw.text("Pressione ESPAÇO para Jogar Novamente", center=(WIDTH/2, HEIGHT/2), fontsize=30, fontname="8bitoperatorplus8-regular.ttf", color='black')

    elif win_game:
        screen.draw.text("VOCÊ VENCEU!", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=60, fontname="8bitoperatorplus8-regular.ttf", color='green')
        screen.draw.text("Pressione ESPAÇO para Jogar Novamente", center=(WIDTH/2, HEIGHT/2), fontsize=30, fontname="8bitoperatorplus8-regular.ttf", color='black')

    elif game_state == 'PLAYING':
        jogador.draw()
        for p in plataformas:
            p.draw()
        for inimigo in inimigos:
            inimigo.draw()


# --- Inicialização ---
inimigos = []
plataformas = []
plataformas_finais = []
jogador = None

# A música toca a partir do início do script
music.play('back_ground_music')

pgzrun.go()