import pygame, sys, random, json, math, os
import numpy as np

pygame.init()
pygame.mixer.init()

# ================== WINDOW ==================
WIDTH, HEIGHT = 1366, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Family Fortunes - RETRO 1980 FINAL")
clock = pygame.time.Clock()

# ================== RESOURCE ==================
def resource_path(p):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, p)

# ================== COLORS ==================
BLUE   = (20,100,255)
BLACK  = (0,0,0)
YELLOW = (255,230,0)
GRID   = (40,40,40)
WHITE  = (255,255,255)

# ================== FONT ==================
try:
    font = pygame.font.Font(resource_path("PressStart2P.ttf"), 20)
    big  = pygame.font.Font(resource_path("PressStart2P.ttf"), 34)
except:
    font = pygame.font.SysFont("couriernew", 28, True)
    big  = pygame.font.SysFont("couriernew", 40, True)

# ================== 8-BIT BEEP ==================
def beep(freq=600, duration=0.1):
    sr = 44100
    t = np.linspace(0, duration, int(sr*duration), False)
    wave = 0.5*np.sign(np.sin(2*np.pi*freq*t))
    snd = pygame.sndarray.make_sound((wave*32767).astype(np.int16))
    snd.play()

# ================== LOAD DATA ==================
with open(resource_path("question.json")) as f:
    data = json.load(f)

questions = data["main_game"]

# ================== GAME STATE ==================
answers=[]; scores=[]; revealed=[]; progress=[]; flip=[]
question=""

round_num=1
multiplier=1

p1=0; p2=0
turn=1

strikes=0
steal=False
round_score=0

history=[]; history_index=-1

# ================== ROUND ==================
def get_multiplier(r):
    if r<=2: return 1
    elif r==3: return 2
    elif r<=5: return 3
    else: return random.choice([1,2,3])

# ================== LOAD QUESTION ==================
def load_q():
    global answers, scores, revealed, progress, flip
    global question, strikes, steal, round_score, multiplier
    global history, history_index

    q = random.choice(questions)
    random.shuffle(q["answers"])

    # batasi maks 8
    q_answers = q["answers"][:8]

    answers = [a[0].upper() for a in q_answers]
    scores  = [a[1] for a in q_answers]

    revealed = [False]*len(answers)
    progress = [0]*len(answers)  # fill px
    flip     = [0]*len(answers)  # frame counter

    question = q["question"].upper()
    strikes=0; steal=False; round_score=0
    multiplier = get_multiplier(round_num)

    state = {
        "answers":answers[:],
        "scores":scores[:],
        "revealed":revealed[:],
        "progress":progress[:],
        "flip":flip[:],
        "question":question,
        "round":round_num
    }
    history = history[:history_index+1]
    history.append(state)
    history_index += 1

def load_history(i):
    global answers, scores, revealed, progress, flip, question, round_num
    s = history[i]
    answers=s["answers"]; scores=s["scores"]
    revealed=s["revealed"]; progress=s["progress"]
    flip=s["flip"]; question=s["question"]; round_num=s["round"]

# ================== BOARD & GRID ==================
BOARD_X, BOARD_Y = 220, 80
BOARD_W, BOARD_H = 900, 520
GRID_SIZE = 40

def draw_board():
    pygame.draw.rect(screen, BLACK, (BOARD_X, BOARD_Y, BOARD_W, BOARD_H))
    # grid 40px
    for x in range(BOARD_X, BOARD_X+BOARD_W+1, GRID_SIZE):
        pygame.draw.line(screen, GRID, (x, BOARD_Y), (x, BOARD_Y+BOARD_H))
    for y in range(BOARD_Y, BOARD_Y+BOARD_H+1, GRID_SIZE):
        pygame.draw.line(screen, GRID, (BOARD_X, y), (BOARD_X+BOARD_W, y))

# ================== ANSWERS (FILL + FLIP) ==================
ROW_H = 60  # 8 baris pas di 520px (dengan margin)
START_Y = 110
TEXT_X  = 320
NUM_X   = 250
SCORE_X = 980
FILL_MAX_W = 600
FILL_SPEED = 20

def draw_answers():
    for i, a in enumerate(answers):
        y = START_Y + i*ROW_H

        # nomor
        num = font.render(str(i+1), True, YELLOW)
        screen.blit(num, (NUM_X, y))

        if not revealed[i]:
            dots = font.render("........", True, YELLOW)
            screen.blit(dots, (TEXT_X, y))
            continue

        # fill kiri -> kanan
        if progress[i] < FILL_MAX_W:
            progress[i] = min(FILL_MAX_W, progress[i] + FILL_SPEED)

        pygame.draw.rect(screen, WHITE, (TEXT_X, y, progress[i], 40))

        # glow tip di ujung fill
        if progress[i] < FILL_MAX_W:
            glow = pygame.Surface((6, 40), pygame.SRCALPHA)
            glow.fill((255,255,255,120))
            screen.blit(glow, (TEXT_X + progress[i]-3, y))

        # flip reveal
        if flip[i] > 0:
            flip[i] += 1
            scale = abs(math.sin(flip[i]*0.2))
            w = int(FILL_MAX_W * scale)
            rect = pygame.Rect(TEXT_X + FILL_MAX_W//2 - w//2, y, w, 40)
            pygame.draw.rect(screen, YELLOW, rect)
            if flip[i] > 10:
                txt = font.render(a, True, BLACK)
                scr = font.render(str(scores[i]*multiplier), True, BLACK)
                screen.blit(txt, (TEXT_X+10, y))
                screen.blit(scr, (SCORE_X, y))
        else:
            txt = font.render(a, True, BLACK)
            scr = font.render(str(scores[i]*multiplier), True, BLACK)
            screen.blit(txt, (TEXT_X+10, y))
            screen.blit(scr, (SCORE_X, y))

# ================== STRIKE ==================
strike_flash = 0
def draw_strikes():
    global strike_flash
    for i in range(strikes):
        y = 200 + i*100

        visible = True
        if strike_flash>0:
            visible = (pygame.time.get_ticks()//120)%2==0

        if not visible:
            continue

        # kiri
        pygame.draw.line(screen, YELLOW, (170, y), (210, y+40), 10)
        pygame.draw.line(screen, YELLOW, (210, y), (170, y+40), 10)
        # kanan
        pygame.draw.line(screen, YELLOW, (1130, y), (1170, y+40), 10)
        pygame.draw.line(screen, YELLOW, (1170, y), (1130, y+40), 10)

    if strike_flash>0:
        strike_flash -= 1

# ================== CRT ==================
def draw_crt():
    for y in range(0, HEIGHT, 2):
        pygame.draw.line(screen, (0,0,0), (0,y), (WIDTH,y), 1)

# ================== INPUT ==================
user=""
def handle(e):
    global user, strikes, steal, turn, p1, p2, round_score, round_num, strike_flash

    if e.type!=pygame.KEYDOWN:
        return

    if e.unicode.isalpha() or e.unicode==" ":
        user += e.unicode.upper()

    if e.key==pygame.K_BACKSPACE:
        user = user[:-1]

    if e.key==pygame.K_RETURN:
        found=False
        for i,a in enumerate(answers):
            if user == a and not revealed[i]:
                revealed[i] = True
                flip[i] = 1
                progress[i] = 1
                round_score += scores[i]*multiplier
                beep(900)
                if i == 0:  # top answer
                    beep(1200, 0.05)
                found=True

        if not found:
            strikes += 1
            strike_flash = 30
            beep(200)

        user = ""

        # auto steal
        if strikes >= 3 and not steal:
            steal = True
            turn = 2 if turn==1 else 1
            return

        if strikes >= 4 and steal:
            if turn==1: p1 += round_score
            else: p2 += round_score
            next_round()

# ================== FLOW ==================
def next_round():
    global round_num
    round_num += 1
    load_q()

def prev_round():
    global history_index
    if history_index > 0:
        history_index -= 1
        load_history(history_index)

# ================== START ==================
load_q()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        handle(e)

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_n:
                next_round()
            if e.key == pygame.K_p:
                prev_round()

    screen.fill(BLUE)

    draw_board()
    draw_answers()
    draw_strikes()

    # info
    screen.blit(font.render(question, True, YELLOW), (260, 620))
    screen.blit(big.render(f"R{round_num} x{multiplier}", True, YELLOW), (40, 40))
    screen.blit(big.render(str(p1), True, YELLOW), (40, 110))
    screen.blit(big.render(str(p2), True, YELLOW), (40, 170))

    draw_crt()

    pygame.display.flip()
    clock.tick(60)
