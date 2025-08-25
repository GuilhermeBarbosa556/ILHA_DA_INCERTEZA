# main.py - Ilha da Incerteza (Cenários Separados)
import pygame
import sys
import random
import json
import os
from datetime import datetime

# 1. INICIALIZAÇÃO
pygame.init()
pygame.font.init()

# 2. CONFIGURAÇÕES DA JANELA (TELA CHEIA)
info = pygame.display.Info()
LARGURA, ALTURA = info.current_w, info.current_h
TELA = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("Ilha da Incerteza - Sobreviva com Probabilidade")

# 3. CORES
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
AZUL = (65, 105, 225)
AZUL_CLARO = (173, 216, 230)
MARROM = (139, 69, 19)
CINZA = (100, 100, 100)
AMARELO = (218, 165, 32)
VERMELHO = (220, 20, 60)
LARANJA = (255, 140, 0)
AZUL_AGUA = (0, 191, 255)
ROXO = (128, 0, 128)
VERDE_ESCURO = (0, 100, 0)

# 4. RELÓGIO E FPS
relogio = pygame.time.Clock()
FPS = 60

# 5. ESTADOS DO JOGO
class EstadoJogo:
    EXPLORACAO = 0
    MENU = 1
    EVENTO = 2
    COMBATE = 3
    GAME_OVER = 4
    VITORIA = 5
    TRANSICAO = 6
    PORTAL = 7
    CRAFTING = 8

estado_atual = EstadoJogo.EXPLORACAO

# 6. FONTES
try:
    fonte_pequena = pygame.font.Font(None, 24)
    fonte_media = pygame.font.Font(None, 36)
    fonte_grande = pygame.font.Font(None, 72)
except:
    fonte_pequena = pygame.font.SysFont(None, 24)
    fonte_media = pygame.font.SysFont(None, 36)
    fonte_grande = pygame.font.SysFont(None, 72)

# 7. FUNÇÕES DE CARREGAMENTO DE ASSETS
def carregar_imagem(caminho, escala=None):
    """Carrega uma imagem e aplica escala se especificado"""
    try:
        if os.path.exists(caminho):
            imagem = pygame.image.load(caminho).convert_alpha()
            if escala:
                imagem = pygame.transform.scale(imagem, escala)
            return imagem
    except:
        print(f"Erro ao carregar imagem: {caminho}")
    surface = pygame.Surface(escala if escala else (50, 50), pygame.SRCALPHA)
    surface.fill(ROXO)
    return surface

def carregar_sprite_sheet(caminho, escala=None):
    """Carrega um sprite sheet com as coordenadas CORRETAS"""
    try:
        sheet = pygame.image.load(caminho).convert_alpha()
        
        frames = {}
        
        # ✅ COORDENADAS CORRETAS fornecidas pelo usuário
        coordenadas = {
            'baixo': [
                (0, 0, 64, 64),    # Frame 1 - Baixo
                (64, 0, 64, 64),   # Frame 2 - Baixo
                (128, 0, 64, 64),  # Frame 3 - Baixo
                (192, 0, 64, 64)   # Frame 4 - Baixo
            ],
            'esquerda': [
                (0, 64, 64, 64),    # Frame 1 - Esquerda
                (64, 64, 64, 64),   # Frame 2 - Esquerda
                (128, 64, 64, 64),  # Frame 3 - Esquerda
                (192, 64, 64, 64)   # Frame 4 - Esquerda
            ],
            'direita': [
                (0, 128, 64, 64),    # Frame 1 - Direita
                (64, 128, 64, 64),   # Frame 2 - Direita
                (128, 128, 64, 64),  # Frame 3 - Direita
                (192, 128, 64, 64)   # Frame 4 - Direita
            ],
            'cima': [
                (0, 192, 64, 64),    # Frame 1 - Cima
                (64, 192, 64, 64),   # Frame 2 - Cima
                (128, 192, 64, 64),  # Frame 3 - Cima
                (192, 192, 64, 64)   # Frame 4 - Cima
            ]
        }
        
        for direcao, frames_list in coordenadas.items():
            frames[direcao] = []
            for i, (x, y, larg, alt) in enumerate(frames_list):
                try:
                    frame = sheet.subsurface(pygame.Rect(x, y, larg, alt))
                    if escala:
                        frame = pygame.transform.scale(frame, escala)
                    frames[direcao].append(frame)
                except:
                    fallback = pygame.Surface((larg, alt))
                    fallback.fill([VERMELHO, VERDE, AZUL, AMARELO][list(coordenadas.keys()).index(direcao) % 4])
                    if escala:
                        fallback = pygame.transform.scale(fallback, escala)
                    frames[direcao].append(fallback)
        
        return frames
        
    except Exception as e:
        print(f"❌ Erro ao carregar sprite sheet: {e}")
        frames = {
            'baixo': [pygame.Surface((64, 64)) for _ in range(4)],
            'esquerda': [pygame.Surface((64, 64)) for _ in range(4)],
            'direita': [pygame.Surface((64, 64)) for _ in range(4)],
            'cima': [pygame.Surface((64, 64)) for _ in range(4)]
        }
        for i, (direcao, surf_list) in enumerate(frames.items()):
            for surf in surf_list:
                surf.fill([VERMELHO, VERDE, AZUL, AMARELO][i])
        return frames

def carregar_sprites():
    """Carrega todas as imagens do jogo"""
    sprites = {
        'player_frames': carregar_sprite_sheet('assets/images/player/player.png', (96, 96)),
        
        'areas': {
            'Praia': carregar_imagem('assets/images/areas/beach.png', (LARGURA, ALTURA)),
            'Floresta': carregar_imagem('assets/images/areas/forest.png', (LARGURA, ALTURA)),
            'Montanha': carregar_imagem('assets/images/areas/mountain.png', (LARGURA, ALTURA)),
            'Lago': carregar_imagem('assets/images/areas/lake.png', (LARGURA, ALTURA)),
            'Deserto': carregar_imagem('assets/images/areas/desert.png', (LARGURA, ALTURA))
        },
        
        'itens': {
            'Madeira': carregar_imagem('assets/images/items/wood.png', (40, 40)),
            'Pedra': carregar_imagem('assets/images/items/stone.png', (40, 40)),
            'Comida': carregar_imagem('assets/images/items/food.png', (40, 40)),
            'Água': carregar_imagem('assets/images/items/water.png', (40, 40)),
            'Coco': carregar_imagem('assets/images/items/coconut.png', (40, 40)),
            'Cogumelo': carregar_imagem('assets/images/items/mushroom.png', (40, 40)),
            'Peixe': carregar_imagem('assets/images/items/fish.png', (40, 40)),
            'Faca': carregar_imagem('assets/images/items/knife.png', (40, 40)),
            'Lança': carregar_imagem('assets/images/items/spear.png', (40, 40))
        },
        
        'portal': carregar_imagem('assets/images/portal.png', (80, 80))
    }
    return sprites

# 8. CLASSES DO JOGO
class Jogador:
    def __init__(self, sprites):
        self.x = LARGURA // 2
        self.y = ALTURA // 2
        self.largura = 64
        self.altura = 64
        self.velocidade = 5
        self.saude = 100
        self.fome = 100
        self.sede = 100
        self.inventario = {'Madeira': 5, 'Pedra': 3, 'Comida': 3, 'Água': 3, 'Coco': 0, 'Cogumelo': 0, 'Peixe': 0, 'Faca': 0, 'Lança': 0}
        self.ferramentas_ativas = {'Faca': False, 'Lança': False}
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
        self.dias_sobrevividos = 0
        self.direcao = 'baixo'
        self.frame_atual = 0
        self.animacao_timer = 0
        self.animacao_velocidade = 150
        self.sprites = sprites
        self.movendo = False
        self.area_atual = None
        self.bonus_coleta = 0

    def atualizar(self, teclas, delta_tempo, areas, portal_rect):
        self.movendo = False
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.x -= self.velocidade
            self.direcao = 'esquerda'
            self.movendo = True
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.x += self.velocidade
            self.direcao = 'direita'
            self.movendo = True
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.y -= self.velocidade
            self.direcao = 'cima'
            self.movendo = True
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.y += self.velocidade
            self.direcao = 'baixo'
            self.movendo = True

        # Limites da tela
        self.x = max(0, min(LARGURA - self.largura, self.x))
        self.y = max(0, min(ALTURA - self.altura, self.y))

        self.rect.x = self.x
        self.rect.y = self.y

        # Atualizar bônus de coleta baseado nas ferramentas
        self.bonus_coleta = 0
        if self.ferramentas_ativas['Faca']:
            self.bonus_coleta += 0.2
        if self.ferramentas_ativas['Lança']:
            self.bonus_coleta += 0.3

        # Verificar se o jogador está interagindo avec o portal
        if self.rect.colliderect(portal_rect):
            return "portal"

        # Verificar se o jogador está saindo da tela para mudar de área
        nova_area = None
        if self.x <= 0:
            self.x = LARGURA - self.largura - 10
            nova_area = "esquerda"
        elif self.x >= LARGURA - self.largura:
            self.x = 10
            nova_area = "direita"
        elif self.y <= 0:
            self.y = ALTURA - self.altura - 10
            nova_area = "cima"
        elif self.y >= ALTURA - self.altura:
            self.y = 10
            nova_area = "baixo"

        # Verificar colisão com áreas para definir a área atual
        self.area_atual = None
        for area in areas:
            if self.rect.colliderect(area.rect):
                self.area_atual = area
                break

        if self.movendo:
            self.animacao_timer += delta_tempo
            if self.animacao_timer >= self.animacao_velocidade:
                self.animacao_timer = 0
                self.frame_atual = (self.frame_atual + 1) % 4
        else:
            self.frame_atual = 0

        return nova_area

    def desenhar(self, tela):
        frames_direcao = self.sprites['player_frames'].get(self.direcao, [])
        
        if frames_direcao and self.frame_atual < len(frames_direcao):
            sprite = frames_direcao[self.frame_atual]
            tela.blit(sprite, (self.x, self.y))
        else:
            pygame.draw.rect(tela, VERMELHO, self.rect)

    def usar_item(self, item):
        if self.inventario.get(item, 0) > 0:
            self.inventario[item] -= 1
            if item in ["Comida", "Cogumelo", "Coco", "Peixe"]:
                self.fome = min(100, self.fome + 30)
                return f"Comeu {item}. Fome +30!"
            elif item == "Água":
                self.sede = min(100, self.sede + 50)
                return f"Bebeu {item}. Sede +50!"
            elif item in ["Faca", "Lança"]:
                # Alterna o estado da ferramenta
                self.ferramentas_ativas[item] = not self.ferramentas_ativas[item]
                status = "equipada" if self.ferramentas_ativas[item] else "desequipada"
                
                # Desequipa outras ferramentas se esta foi equipada
                if self.ferramentas_ativas[item]:
                    for ferramenta in self.ferramentas_ativas:
                        if ferramenta != item:
                            self.ferramentas_ativas[ferramenta] = False
                
                return f"{item} {status}. Bônus de coleta aplicado!"
        return f"Não tem {item} suficiente!"

    def esta_vivo(self):
        return self.saude > 0

class Area:
    def __init__(self, nome, cor, recursos, risco, x, y, largura, altura, sprite=None):
        self.nome = nome
        self.cor = cor
        self.recursos = recursos
        self.risco = risco
        self.rect = pygame.Rect(x, y, largura, altura)
        self.descricao = self.gerar_descricao()
        self.sprite = sprite
        self.conexoes = {}

    def definir_conexoes(self, conexoes):
        self.conexoes = conexoes

    def gerar_descricao(self):
        descricoes = {
            "Praia": "Areia white e mar calmo. Cuidado com a ressaca.",
            "Floresta": "Vegetação densa. Sons estranhos ecoam entre as árvores.",
            "Montanha": "Terreno íngreme e ar rarefeito. A vista é magnífica.",
            "Lago": "Água cristalina. Pode esconder perigos subaquáticos.",
            "Deserto": "Calor intenso e areia movediça. Recursos escassos."
        }
        return descricoes.get(self.nome, "Uma área misteriosa da ilha.")

    def explorar(self, bonus_coleta=0):
        resultado = {"recursos": {}, "evento": None, "dano": 0}
        
        for recurso, prob in self.recursos.items():
            # Aplicar bônus de coleta se houver
            prob_com_bonus = min(1.0, prob + (prob * bonus_coleta))
            if random.random() < prob_com_bonus:
                qtd = random.randint(1, 3)
                # Chance de conseguir um item extra com bônus
                if bonus_coleta > 0 and random.random() < bonus_coleta:
                    qtd += 1
                resultado["recursos"][recurso] = qtd
        
        if random.random() < self.risco:
            eventos = [
                ("Uma cobra venenosa te atacou!", 10, 20),
                ("Você caiu em um arbusto espinhado.", 5, 15),
                ("Uma tempestade surpreendeu você.", 8, 18),
                ("Um animal selvagem te perseguiu.", 12, 25),
                ("Você tropeçou em uma pedra.", 3, 10)
            ]
            evento_escolhido = random.choice(eventos)
            resultado["evento"] = evento_escolhido[0]
            resultado["dano"] = random.randint(evento_escolhido[1], evento_escolhido[2])
        
        return resultado

    def desenhar(self, tela, fundo_completo=False):
        if self.sprite and fundo_completo:
            tela.blit(self.sprite, (0, 0))
        elif self.sprite:
            tela.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(tela, self.cor, self.rect)
        pygame.draw.rect(tela, PRETO, self.rect, 2)

# 9. FUNÇÕES DE UTILIDADE
def desenhar_barra(tela, x, y, largura, altura, valor, max_valor, cor_preenchimento, cor_fundo):
    pygame.draw.rect(tela, cor_fundo, (x, y, largura, altura))
    preenchimento = (valor / max_valor) * largura
    pygame.draw.rect(tela, cor_preenchimento, (x, y, preenchimento, altura))
    pygame.draw.rect(tela, PRETO, (x, y, largura, altura), 1)

def desenhar_texto_com_borda(tela, texto, fonte, cor_texto, cor_borda, posicao):
    """Desenha texto com borda para melhor visibilidade"""
    x, y = posicao
    # Renderiza a borda (desenha o texto em várias posições ao redor)
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        texto_borda = fonte.render(texto, True, cor_borda)
        tela.blit(texto_borda, (x + dx, y + dy))
    
    # Renderiza o texto principal
    texto_surface = fonte.render(texto, True, cor_texto)
    tela.blit(texto_surface, (x, y))

def desenhar_texto_centralizado(tela, texto, fonte, cor_texto, cor_borda, y):
    texto_surface = fonte.render(texto, True, cor_texto)
    texto_rect = texto_surface.get_rect(center=(LARGURA // 2, y))
    
    # Desenha borda
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        texto_borda = fonte.render(texto, True, cor_borda)
        texto_borda_rect = texto_borda.get_rect(center=(LARGURA // 2 + dx, y + dy))
        tela.blit(texto_borda, texto_borda_rect)
    
    tela.blit(texto_surface, texto_rect)

def salvar_jogo(jogador, dias):
    dados = {
        "saude": jogador.saude,
        "fome": jogador.fome,
        "sede": jogador.sede,
        "inventario": jogador.inventario,
        "ferramentas_ativas": jogador.ferramentas_ativas,
        "dias_sobrevividos": dias,
        "data_salvamento": datetime.now().isoformat()
    }
    with open("game_data.json", "w") as f:
        json.dump(dados, f, indent=4)
    return "Jogo salvo com sucesso!"

def carregar_jogo():
    if os.path.exists("game_data.json"):
        with open("game_data.json", "r") as f:
            return json.load(f)
    return None

def verificar_crafting(jogador):
    """Verifica se o jogador tem recursos para craftar itens"""
    receitas = {
        "Faca": {"Madeira": 2, "Pedra": 3},
        "Lança": {"Madeira": 3, "Pedra": 5}  # CORREÇÃO: Removido o requisito de faca
    }
    
    itens_craftaveis = []
    for item, recursos in receitas.items():
        pode_craftar = True
        for recurso, quantidade in recursos.items():
            if jogador.inventario.get(recurso, 0) < quantidade:
                pode_craftar = False
                break
        if pode_craftar:
            itens_craftaveis.append(item)
    
    return itens_craftaveis

def craftar_item(jogador, item):
    """Crafta um item se o jogador tiver os recursos necessários"""
    receitas = {
        "Faca": {"Madeira": 2, "Pedra": 3},
        "Lança": {"Madeira": 3, "Pedra": 5}  # CORREÇÃO: Removido o requisito de faca
    }
    
    if item in receitas:
        for recurso, quantidade in receitas[item].items():
            if jogador.inventario.get(recurso, 0) < quantidade:
                return f"Recursos insuficientes para craftar {item}. Necessário: {receitas[item]}"
        
        # Deduz os recursos
        for recurso, quantidade in receitas[item].items():
            jogador.inventario[recurso] -= quantidade
        
        # Adiciona o item craftado
        jogador.inventario[item] = jogador.inventario.get(item, 0) + 1
        return f"{item} craftado com sucesso! Recursos usados: {receitas[item]}"
    
    return f"Receita para {item} não encontrada"

# 10. INICIALIZAÇÃO DO JOGO
sprites = carregar_sprites()
jogador = Jogador(sprites)

def criar_mundo(sprites):
    areas = [
        Area("Praia", (210, 180, 140), {"Coco": 0.8, "Madeira": 0.4, "Pedra": 0.2}, 0.2, 0, 0, LARGURA, ALTURA, sprites['areas']['Praia']),
        Area("Floresta", VERDE, {"Madeira": 0.7, "Cogumelo": 0.5, "Pedra": 0.3}, 0.4, LARGURA, 0, LARGURA, ALTURA, sprites['areas']['Floresta']),
        Area("Montanha", CINZA, {"Pedra": 0.9, "Madeira": 0.2}, 0.6, 0, ALTURA, LARGURA, ALTURA, sprites['areas']['Montanha']),
        Area("Lago", (0, 150, 255), {"Água": 0.9, "Peixe": 0.3, "Pedra": 0.1}, 0.3, LARGURA, ALTURA, LARGURA, ALTURA, sprites['areas']['Lago']),
        Area("Deserto", AMARELO, {"Pedra": 0.3}, 0.7, -LARGURA, 0, LARGURA, ALTURA, sprites['areas']['Deserto'])
    ]
    
    # Definir conexões entre as áreas conforme solicitado
    areas[0].definir_conexoes({"esquerda": areas[4], "direita": areas[1]})  # Praia
    areas[1].definir_conexoes({"cima": areas[2], "esquerda": areas[0], "baixo": areas[3], "direita": areas[4]})     # Floresta
    areas[2].definir_conexoes({"baixo": areas[1]})                        # Montanha (cima removido)
    areas[3].definir_conexoes({"cima": areas[1]})                        # Lago
    areas[4].definir_conexoes({"direita": areas[0], "esquerda": areas[1]}) # Deserto
    
    return areas

areas = criar_mundo(sprites)
area_atual = areas[0]  # Começa na praia
mensagem = "Bem-vindo à Ilha da Incerteza! Use WASD para mover, E para explorar, 1-9 para usar itens, C para crafting, P para portal."
cooldown_explorar = 0
COOLDOWN_MAX = FPS * 1.5
tempo_ultimo_decaimiento = 0
INTERVALO_DECAIMENTO = 5000
dia_tempo = 0
DIA_DURACAO = 60000
dias_sobrevividos = 0
transicao_timer = 0
TRANSICAO_DURACAO = 30

# Portal para troca de áreas
portal_rect = pygame.Rect(LARGURA - 100, ALTURA - 100, 80, 80)
portal_ativado = False
portal_cooldown = 0

dados_salvos = carregar_jogo()
if dados_salvos:
    jogador.saude = dados_salvos["saude"]
    jogador.fome = dados_salvos["fome"]
    jogador.sede = dados_salvos["sede"]
    jogador.inventario = dados_salvos["inventario"]
    jogador.ferramentas_ativas = dados_salvos.get("ferramentas_ativas", {"Faca": False, "Lança": False})
    dias_sobrevividos = dados_salvos["dias_sobrevividos"]
    mensagem = f"Jogo carregado. Sobrevivendo há {dias_sobrevividos} dias."

# 11. LOOP PRINCIPAL
executando = True
while executando:
    tempo_atual = pygame.time.get_ticks()
    delta_tempo = relogio.tick(FPS)
    
    # --- MANUSEIO DE EVENTOS ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_e and cooldown_explorar <= 0 and estado_atual == EstadoJogo.EXPLORACAO:
                resultado = area_atual.explorar(jogador.bonus_coleta)
                cooldown_explorar = COOLDOWN_MAX
                
                if resultado["recursos"]:
                    for recurso, qtd in resultado["recursos"].items():
                        jogador.inventario[recurso] = jogador.inventario.get(recurso, 0) + qtd
                    recursos_texto = ", ".join([f"{qtd}x {r}" for r, qtd in resultado["recursos"].items()])
                    mensagem = f"Encontrou: {recursos_texto} em {area_atual.nome}!"
                    if jogador.bonus_coleta > 0:
                        mensagem += " (Bônus de ferramentas aplicado!)"
                else:
                    mensagem = f"Explorou {area_atual.nome} mas não encontrou nada."
                
                if resultado["evento"]:
                    jogador.saude -= resultado["dano"]
                    mensagem += f" {resultado['evento']} (-{resultado['dano']} saúde)"
            
            # CORREÇÃO: Criar uma lista fixa de itens para mapear teclas corretamente
            if evento.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                # Criar lista de itens disponíveis (com quantidade > 0)
                itens_disponiveis = [item for item, qtd in jogador.inventario.items() if qtd > 0]
                
                # Verificar se o índice é válido
                index = evento.key - pygame.K_1
                if index < len(itens_disponiveis):
                    item_selecionado = itens_disponiveis[index]
                    mensagem = jogador.usar_item(item_selecionado)
                else:
                    mensagem = "Nenhum item nesta posição"
            
            if evento.key == pygame.K_s:
                mensagem = salvar_jogo(jogador, dias_sobrevividos)
            
            if evento.key == pygame.K_r:
                areas = criar_mundo(sprites)
                area_atual = areas[0]
                mensagem = "Mundo recarregado!"
            
            if evento.key == pygame.K_p and estado_atual == EstadoJogo.EXPLORACAO:
                portal_ativado = True
                estado_atual = EstadoJogo.PORTAL
                mensagem = "Selecione uma área para viajar"
            
            if evento.key == pygame.K_c and estado_atual == EstadoJogo.EXPLORACAO:
                itens_craftaveis = verificar_crafting(jogador)
                if itens_craftaveis:
                    estado_atual = EstadoJogo.CRAFTING
                    mensagem = "Selecione um item para craftar (1-9) ou ESC para cancelar"
                else:
                    # Mostra as receitas mesmo quando não pode craftar
                    receitas = {
                        "Faca": "2 Madeira + 3 Pedra",
                        "Lança": "3 Madeira + 5 Pedra"  # CORREÇÃO: Atualizada a receita
                    }
                    mensagem = "Não pode craftar nada. Receitas: " + "; ".join([f"{item}: {rec}" for item, rec in receitas.items()])
            
            if evento.key == pygame.K_ESCAPE:
                if estado_atual == EstadoJogo.PORTAL:
                    estado_atual = EstadoJogo.EXPLORACAO
                    mensagem = "Viagem cancelada"
                elif estado_atual == EstadoJogo.CRAFTING:
                    estado_atual = EstadoJogo.EXPLORACAO
                    mensagem = "Crafting cancelado"
                else:
                    executando = False
            
            if estado_atual == EstadoJogo.PORTAL:
                if evento.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    index = evento.key - pygame.K_1
                    if index < len(areas):
                        area_destino = areas[index]
                        estado_atual = EstadoJogo.TRANSICAO
                        transicao_timer = TRANSICAO_DURACAO
                        mensagem = f"Viajando para {area_destino.nome}"
            
            if estado_atual == EstadoJogo.CRAFTING:
                itens_craftaveis = verificar_crafting(jogador)
                if evento.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    index = evento.key - pygame.K_1
                    if index < len(itens_craftaveis):
                        item_selecionado = itens_craftaveis[index]
                        mensagem = craftar_item(jogador, item_selecionado)
                        estado_atual = EstadoJogo.EXPLORACAO
                    else:
                        mensagem = "Índice inválido no menu de crafting"
                        estado_atual = EstadoJogo.EXPLORACAO
    
    # --- ATUALIZAÇÕES DE LÓGICA ---
    teclas = pygame.key.get_pressed()
    
    if estado_atual == EstadoJogo.EXPLORACAO:
        resultado = jogador.atualizar(teclas, delta_tempo, areas, portal_rect)
        
        # Verificar se o jogador ativou o portal
        if resultado == "portal":
            portal_ativado = True
            estado_atual = EstadoJogo.PORTAL
            mensagem = "Selecione uma área para viajar"
        
        # Verificar se o jogador está tentando mudar de área pelas bordas
        elif resultado and resultado in area_atual.conexoes:
            proxima_area = area_atual.conexoes[resultado]
            estado_atual = EstadoJogo.TRANSICAO
            transicao_timer = TRANSICAO_DURACAO
            area_destino = proxima_area
        elif resultado:
            # Se tentou sair por uma direção que não tem conexão
            mensagem = "Não há caminho nesta direção!"
        
        if cooldown_explorar > 0:
            cooldown_explorar -= 1
        
        if tempo_atual - tempo_ultimo_decaimiento > INTERVALO_DECAIMENTO:
            tempo_ultimo_decaimiento = tempo_atual
            
            jogador.fome -= 2
            jogador.sede -= 3
            
            # Ferramentas ativas reduzem o decaimento
            if jogador.ferramentas_ativas['Faca']:
                jogador.fome -= 0.5  # Redução menor na fome
            if jogador.ferramentas_ativas['Lança']:
                jogador.sede -= 0.5  # Redução menor na sede
            
            if jogador.fome <= 0:
                jogador.saude -= 5
                mensagem = "Fome extrema! Saúde diminuindo."
            if jogador.sede <= 0:
                jogador.saude -= 8
                mensagem = "Desidratação! Saúde diminuindo rapidamente."
            
            jogador.fome = max(0, jogador.fome)
            jogador.sede = max(0, jogador.sede)
            
            dia_tempo += INTERVALO_DECAIMENTO
            if dia_tempo >= DIA_DURACAO:
                dia_tempo = 0
                dias_sobrevividos += 1
                jogador.dias_sobrevividos = dias_sobrevividos
                mensagem = f"Novo dia amanhece! Dia {dias_sobrevividos} na ilha."
        
        if not jogador.esta_vivo():
            estado_atual = EstadoJogo.GAME_OVER
            mensagem = "Você não sobreviveu à Ilha da Incerteza..."
        elif dias_sobrevividos >= 10 and jogador.inventario.get("Madeira", 0) >= 30:
            estado_atual = EstadoJogo.VITORIA
            mensagem = "Você construiu uma jangada e escapou da ilha!"
    
    elif estado_atual == EstadoJogo.TRANSICAO:
        transicao_timer -= 1
        if transicao_timer <= 0:
            area_atual = area_destino
            estado_atual = EstadoJogo.EXPLORACAO
            mensagem = f"Você chegou à {area_atual.nome}"
    
    # --- RENDERIZAÇÃO ---
    # Desenhar o cenário atual (fundo completo)
    if estado_atual in [EstadoJogo.EXPLORACAO, EstadoJogo.PORTAL, EstadoJogo.CRAFTING]:
        area_atual.desenhar(TELA, fundo_completo=True)
    elif estado_atual == EstadoJogo.TRANSICAO:
        # Efeito de transição (fade entre áreas)
        alpha = int(255 * (transicao_timer / TRANSICAO_DURACAO))
        s = pygame.Surface((LARGURA, ALTURA))
        s.set_alpha(alpha)
        area_atual.desenhar(TELA, fundo_completo=True)
        area_destino.desenhar(TELA, fundo_completo=True)
        TELA.blit(s, (0, 0))
    
    # Desenhar o jogador (exceto durante portal e crafting)
    if estado_atual == EstadoJogo.EXPLORACAO:
        jogador.desenhar(TELA)
    
    # Desenhar o portal
    if estado_atual == EstadoJogo.EXPLORACAO:
        if 'portal' in sprites:
            TELA.blit(sprites['portal'], portal_rect)
        else:
            pygame.draw.rect(TELA, ROXO, portal_rect)
        desenhar_texto_com_borda(TELA, "Portal [P]", fonte_pequena, BRANCO, PRETO, (portal_rect.x, portal_rect.y - 25))
    
    # UI - Barras de status
    desenhar_barra(TELA, 10, 10, 200, 20, jogador.saude, 100, VERMELHO, (100, 0, 0))
    desenhar_barra(TELA, 10, 40, 200, 20, jogador.fome, 100, LARANJA, (100, 50, 0))
    desenhar_barra(TELA, 10, 70, 200, 20, jogador.sede, 100, AZUL_AGUA, (0, 50, 100))
    
    desenhar_texto_com_borda(TELA, f"Saúde: {int(jogador.saude)}", fonte_pequena, BRANCO, PRETO, (15, 11))
    desenhar_texto_com_borda(TELA, f"Fome: {int(jogador.fome)}", fonte_pequena, BRANCO, PRETO, (15, 41))
    desenhar_texto_com_borda(TELA, f"Sede: {int(jogador.sede)}", fonte_pequena, BRANCO, PRETO, (15, 71))
    desenhar_texto_com_borda(TELA, f"Dia: {dias_sobrevividos}", fonte_pequena, BRANCO, PRETO, (15, 101))
    
    # Indicador de ferramentas ativas
    y_ferramentas = 130
    desenhar_texto_com_borda(TELA, "FERRAMENTAS:", fonte_pequena, BRANCO, PRETO, (10, y_ferramentas))
    y_ferramentas += 25
    
    for ferramenta, ativa in jogador.ferramentas_ativas.items():
        if ativa:
            cor = VERDE
            status = "ON"
        else:
            cor = VERMELHO
            status = "OFF"
        desenhar_texto_com_borda(TELA, f"{ferramenta}: {status}", fonte_pequena, cor, PRETO, (15, y_ferramentas))
        y_ferramentas += 20
    
    # UI - Inventário (melhorado com separação clara)
    y_inv = y_ferramentas + 10
    desenhar_texto_com_borda(TELA, "INVENTÁRIO:", fonte_pequena, BRANCO, PRETO, (10, y_inv))
    y_inv += 30

    tamanho_item = 40
    # CORREÇÃO: Criar lista apenas com itens que têm quantidade > 0
    itens_visiveis = [(item, qtd) for item, qtd in jogador.inventario.items() if qtd > 0]
    
    for i, (item, qtd) in enumerate(itens_visiveis):
        # Adicionar número do item (1-9) - CORREÇÃO: usar índice da lista filtrada
        numero_item = f"{i+1}."
        desenhar_texto_com_borda(TELA, numero_item, fonte_pequena, BRANCO, PRETO, (20, y_inv))
        
        if item in sprites['itens']:
            item_sprite = pygame.transform.scale(sprites['itens'][item], (tamanho_item, tamanho_item))
            TELA.blit(item_sprite, (45, y_inv - 5))
        
        # Nome do item e quantidade em linhas separadas
        desenhar_texto_com_borda(TELA, f"{item}", fonte_pequena, BRANCO, PRETO, (95, y_inv))
        desenhar_texto_com_borda(TELA, f"Qtd: {qtd}", fonte_pequena, BRANCO, PRETO, (95, y_inv + 20))
        y_inv += 55
    
    # UI - Área atual (movida para posição mais segura)
    area_info_x = LARGURA - 350
    desenhar_texto_com_borda(TELA, f"Área: {area_atual.nome}", fonte_pequena, BRANCO, PRETO, (area_info_x, 10))
    
    # Quebrar a descrição em linhas se necessário
    descricao = area_atual.descricao
    if len(descricao) > 40:
        partes = []
        palavras = descricao.split()
        linha_atual = ""
        
        for palavra in palavras:
            if len(linha_atual) + len(palavra) + 1 <= 40:
                linha_atual += palavra + " "
            else:
                partes.append(linha_atual.strip())
                linha_atual = palavra + " "
        
        if linha_atual:
            partes.append(linha_atual.strip())
        
        for i, linha in enumerate(partes):
            desenhar_texto_com_borda(TELA, linha, fonte_pequena, BRANCO, PRETO, (area_info_x, 40 + i * 25))
    else:
        desenhar_texto_com_borda(TELA, descricao, fonte_pequena, BRANCO, PRETO, (area_info_x, 40))
    
    # UI - Bônus de coleta
    if jogador.bonus_coleta > 0:
        desenhar_texto_com_borda(TELA, f"Bônus de Coleta: +{int(jogador.bonus_coleta * 100)}%", fonte_pequena, VERDE, PRETO, (area_info_x, 100))
    
    # UI - Mensagens e controles (centralizadas na parte inferior)
    mensagem_width = fonte_pequena.size(mensagem)[0]
    desenhar_texto_com_borda(TELA, mensagem, fonte_pequena, BRANCO, PRETO, (LARGURA // 2 - mensagem_width // 2, ALTURA - 60))
    
    controles = "WASD: Mover | E: Explorar | 1-9: Usar item | C: Crafting | P: Portal | S: Salvar | R: Recarregar | ESC: Sair"
    controles_width = fonte_pequena.size(controles)[0]
    desenhar_texto_com_borda(TELA, controles, fonte_pequena, BRANCO, PRETO, (LARGURA // 2 - controles_width // 2, ALTURA - 30))
    
    # Menu de seleção de portal
    if estado_atual == EstadoJogo.PORTAL:
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        TELA.blit(s, (0, 0))
        
        desenhar_texto_centralizado(TELA, "SELECIONE UMA ÁREA", fonte_media, BRANCO, PRETO, ALTURA // 2 - 150)
        
        for i, area in enumerate(areas):
            y_pos = ALTURA // 2 - 80 + i * 50
            texto = f"{i+1}. {area.nome} - {area.descricao}"
            desenhar_texto_centralizado(TELA, texto, fonte_pequena, BRANCO, PRETO, y_pos)
        
        desenhar_texto_centralizado(TELA, "Pressione ESC para cancelar", fonte_pequena, BRANCO, PRETO, ALTURA // 2 + 150)
    
    # Menu de crafting
    elif estado_atual == EstadoJogo.CRAFTING:
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        TELA.blit(s, (0, 0))
        
        desenhar_texto_centralizado(TELA, "SISTEMA DE CRAFTING", fonte_media, BRANCO, PRETO, ALTURA // 2 - 150)
        
        itens_craftaveis = verificar_crafting(jogador)
        receitas = {
            "Faca": "2 Madeira + 3 Pedra",
            "Lança": "3 Madeira + 5 Pedra"  # CORREÇÃO: Atualizada a receita
        }
        
        if itens_craftaveis:
            for i, item in enumerate(itens_craftaveis):
                y_pos = ALTURA // 2 - 80 + i * 50
                texto = f"{i+1}. {item} - {receitas[item]}"
                desenhar_texto_centralizado(TELA, texto, fonte_pequena, BRANCO, PRETO, y_pos)
        else:
            # Mostra todas as receitas mesmo quando não pode craftar
            desenhar_texto_centralizado(TELA, "Nenhum item craftável disponível", fonte_pequena, VERMELHO, PRETO, ALTURA // 2 - 50)
            for i, (item, rec) in enumerate(receitas.items()):
                y_pos = ALTURA // 2 + i * 30
                texto = f"{item}: {rec}"
                desenhar_texto_centralizado(TELA, texto, fonte_pequena, AMARELO, PRETO, y_pos)
        
        desenhar_texto_centralizado(TELA, "Pressione ESC para cancelar", fonte_pequena, BRANCO, PRETO, ALTURA // 2 + 150)
    
    # Telas de fim de jogo
    if estado_atual == EstadoJogo.GAME_OVER:
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        TELA.blit(s, (0, 0))
        
        desenhar_texto_centralizado(TELA, "GAME OVER", fonte_grande, VERMELHO, PRETO, ALTURA // 2 - 50)
        desenhar_texto_centralizado(TELA, f"Sobreviveu por {dias_sobrevividos} dias", fonte_media, BRANCO, PRETO, ALTURA // 2 + 20)
        desenhar_texto_centralizado(TELA, "Pressione R para recomeçar", fonte_pequena, BRANCO, PRETO, ALTURA // 2 + 70)
        
        if teclas[pygame.K_r]:
            jogador = Jogador(sprites)
            areas = criar_mundo(sprites)
            area_atual = areas[0]
            dias_sobrevividos = 0
            estado_atual = EstadoJogo.EXPLORACAO
            mensagem = "Novo jogo iniciado!"
    
    elif estado_atual == EstadoJogo.VITORIA:
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 100, 0, 180))
        TELA.blit(s, (0, 0))
        
        desenhar_texto_centralizado(TELA, "VITÓRIA!", fonte_grande, BRANCO, PRETO, ALTURA // 2 - 50)
        desenhar_texto_centralizado(TELA, f"Escapou em {dias_sobrevividos} dias", fonte_media, BRANCO, PRETO, ALTURA // 2 + 20)
        desenhar_texto_centralizado(TELA, "Pressione R para jogar novamente", fonte_pequena, BRANCO, PRETO, ALTURA // 2 + 70)
        
        if teclas[pygame.K_r]:
            jogador = Jogador(sprites)
            areas = criar_mundo(sprites)
            area_atual = areas[0]
            dias_sobrevividos = 0
            estado_atual = EstadoJogo.EXPLORACAO
            mensagem = "Novo jogo iniciado!"
    
    pygame.display.flip()

# 12. ENCERRAMENTO
pygame.quit()
sys.exit()