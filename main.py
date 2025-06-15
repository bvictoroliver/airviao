import pygame
import random
import sys
import os

# Inicialização do Pygame
pygame.init()

# Configurações da tela
LARGURA = 800
ALTURA = 600
TITULO = "Avião de Guerra"

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)

# Configuração da tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption(TITULO)
relogio = pygame.time.Clock()

# Carregar imagem de fundo
caminho_fundo = os.path.join('assets', 'fundo.png')
if os.path.exists(caminho_fundo):
    fundo = pygame.image.load(caminho_fundo).convert()
    fundo = pygame.transform.scale(fundo, (LARGURA, ALTURA))
else:
    fundo = None

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        caminho_img = os.path.join('assets', 'player.png')
        if os.path.exists(caminho_img):
            self.image = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        else:
            self.image = pygame.Surface((60, 60))
            self.image.fill(BRANCO)
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGURA // 2
        self.rect.bottom = ALTURA - 10
        self.velocidade = 5

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT] and self.rect.right < LARGURA:
            self.rect.x += self.velocidade

class Inimigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        imagens_inimigos = [os.path.join('assets', f'en{i}.png') for i in range(1, 6)]
        imagem_escolhida = random.choice(imagens_inimigos)
        if os.path.exists(imagem_escolhida):
            self.image = pygame.image.load(imagem_escolhida).convert_alpha()
            self.image = pygame.transform.scale(self.image, (36, 36))
        else:
            self.image = pygame.Surface((36, 36))
            self.image.fill(VERMELHO)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, LARGURA - 36)
        self.rect.y = random.randint(-100, -40)
        self.velocidade = random.randint(1, 3)

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA:
            self.rect.x = random.randint(0, LARGURA - 36)
            self.rect.y = random.randint(-100, -40)

class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        caminho_img = os.path.join('assets', 'gun.png')
        if os.path.exists(caminho_img):
            self.image = pygame.image.load(caminho_img).convert_alpha()
            self.image = pygame.transform.scale(self.image, (10, 20))
        else:
            self.image = pygame.Surface((10, 20))
            self.image.fill(BRANCO)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.velocidade = -10

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.bottom < 0:
            self.kill()

# Grupos de sprites
todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()

# Criação do jogador
jogador = Jogador()
todos_sprites.add(jogador)

# Criação dos inimigos
for i in range(8):
    inimigo = Inimigo()
    todos_sprites.add(inimigo)
    inimigos.add(inimigo)

# Variáveis do jogo
pontos = 0
rodando = True
game_over = False

# Função para carregar o recorde salvo
def carregar_recorde():
    try:
        with open('recorde.txt', 'r') as f:
            return int(f.read())
    except:
        return 0

# Função para salvar o recorde
def salvar_recorde(novo_recorde):
    with open('recorde.txt', 'w') as f:
        f.write(str(novo_recorde))

# Carregar recorde
recorde = carregar_recorde()

# Fonte para o texto
fonte = pygame.font.Font(None, 36)

# Controle de tiro automático
intervalo_tiro = 250  # milissegundos
ultimo_tiro = pygame.time.get_ticks()

while rodando:
    # Controle de FPS
    relogio.tick(60)

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r and game_over:
                # Reiniciar o jogo
                todos_sprites.empty()
                inimigos.empty()
                tiros.empty()
                jogador = Jogador()
                todos_sprites.add(jogador)
                for i in range(8):
                    inimigo = Inimigo()
                    todos_sprites.add(inimigo)
                    inimigos.add(inimigo)
                game_over = False
                pontos = 0

    if not game_over:
        # Tiro automático
        agora = pygame.time.get_ticks()
        if agora - ultimo_tiro > intervalo_tiro:
            tiro = Tiro(jogador.rect.centerx, jogador.rect.top)
            todos_sprites.add(tiro)
            tiros.add(tiro)
            ultimo_tiro = agora

        # Atualização
        todos_sprites.update()

        # Colisões
        colisoes = pygame.sprite.groupcollide(inimigos, tiros, True, True)
        for colisao in colisoes:
            pontos += 10  # Adiciona 10 pontos por inimigo destruído
            inimigo = Inimigo()
            todos_sprites.add(inimigo)
            inimigos.add(inimigo)

        # Verificar colisão entre jogador e inimigos
        if pygame.sprite.spritecollide(jogador, inimigos, False):
            game_over = True

    # Renderização
    if fundo:
        tela.blit(fundo, (0, 0))
    else:
        tela.fill(PRETO)
    todos_sprites.draw(tela)
    
    # Mostrar pontuação
    texto_pontos = fonte.render(f'Pontos: {pontos}', True, BRANCO)
    tela.blit(texto_pontos, (10, 10))
    texto_recorde = fonte.render(f'Recorde: {recorde}', True, BRANCO)
    tela.blit(texto_recorde, (10, 40))
    
    # Mostrar mensagem de Game Over
    if game_over:
        if pontos > recorde:
            recorde = pontos
            salvar_recorde(recorde)
        fonte_grande = pygame.font.Font(None, 74)
        texto = fonte_grande.render('GAME OVER', True, VERMELHO)
        texto_rect = texto.get_rect(center=(LARGURA/2, ALTURA/2))
        tela.blit(texto, texto_rect)
        
        texto_pontuacao = fonte.render(f'Pontuação Final: {pontos}', True, BRANCO)
        texto_pontuacao_rect = texto_pontuacao.get_rect(center=(LARGURA/2, ALTURA/2 + 40))
        tela.blit(texto_pontuacao, texto_pontuacao_rect)
        
        texto_reiniciar = fonte.render('Pressione R para reiniciar', True, BRANCO)
        texto_reiniciar_rect = texto_reiniciar.get_rect(center=(LARGURA/2, ALTURA/2 + 80))
        tela.blit(texto_reiniciar, texto_reiniciar_rect)
    
    pygame.display.flip()

pygame.quit()
sys.exit() 