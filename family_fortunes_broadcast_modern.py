import pygame, sys, math, random, json, os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Family Fortunes - MODERN FINAL")
clock = pygame.time.Clock()

# ===== RESOURCE PATH (UNTUK EXE) =====
def resource_path(path):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, path)

# ===== LOADERS =====
def load_img(x):
    try: return pygame.image.load(resource_path(x)).convert_alpha()
    except: return pygame.Surface((100,50), pygame.SRCALPHA)

def load_snd(x):
    try: return pygame.mixer.Sound(resource_path(x))
    except: return None

logo = load_img("logo.png")
strike_img = load_img("strike.png")

snd_correct = load_snd("correct.wav")
snd_wrong = load_snd("wrong.wav")
snd_bell = load_snd("bell.wav")
snd_repeat = load_snd("repeat.wav")
snd_saysay = load_snd("saysay.wav")
snd_applause = load_snd("applause.wav")

# ===== FONT =====
font = pygame.font.SysFont("arial", 24, True)
big = pygame.font.SysFont("arial", 44, True)

WHITE=(255,255,255)
YELLOW=(255,200,0)
BLUE=(40,80,200)

# ===== LOAD JSON =====
with open(resource_path("question.json")) as f:
    data = json.load(f)

main_q = data["main_game"]
big_q = data["big_money"]

# ===== STATE =====
answers=[]; scores=[]; revealed=[]; progress=[]
question=""
round_num=1
multiplier=1

p1=0; p2=0
turn=1
strikes=0
steal=False
round_score=0

history=[]; history_index=-1
mode="main"

# ===== BACKGROUND =====
bg_offset=0; shine_x=-300; led_phase=0
def draw_bg():
    global bg_offset, shine_x, led_phase

    for y in range(HEIGHT):
        c=120+int(40*math.sin((y+bg_offset)*0.03))
        pygame.draw.line(screen,(c,0,0),(0,y),(WIDTH,y))
    bg_offset+=2

    shine_x+=10
    if shine_x>WIDTH: shine_x=-300
    for i in range(200):
        s=pygame.Surface((2,HEIGHT),pygame.SRCALPHA)
        s.fill((255,255,255,max(0,120-i)))
        screen.blit(s,(shine_x+i,0))

    led_phase+=0.2
    for x in range(0,WIDTH,20):
        b=int(150+100*math.sin(led_phase+x*0.05))
        pygame.draw.circle(screen,(b,b,0),(x,5),4)
        pygame.draw.circle(screen,(b,b,0),(x,HEIGHT-5),4)

# ===== ROUND MULTIPLIER =====
def get_multiplier(r):
    if r<=2: return 1
    elif r==3: return 2
    elif r<=5: return 3
    else: return random.choice([1,2,3])

# ===== LOAD QUESTION =====
def load_q():
    global answers,scores,revealed,progress
    global question,strikes,steal,round_score,multiplier
    global history,history_index

    q=random.choice(main_q)
    q["answers"].sort(key=lambda x:x[1], reverse=True)

    answers=[x[0] for x in q["answers"]]
    scores=[x[1] for x in q["answers"]]
    revealed=[False]*len(answers)
    progress=[0]*len(answers)

    question=q["question"]
    strikes=0; steal=False; round_score=0
    multiplier=get_multiplier(round_num)

    state={
        "answers":answers[:],
        "scores":scores[:],
        "revealed":revealed[:],
        "progress":progress[:],
        "question":question,
        "round":round_num
    }

    history=history[:history_index+1]
    history.append(state)
    history_index+=1

def load_history(i):
    global answers,scores,revealed,progress,question,round_num
    s=history[i]
    answers=s["answers"]; scores=s["scores"]
    revealed=s["revealed"]; progress=s["progress"]
    question=s["question"]; round_num=s["round"]

# ===== DRAW =====
def draw_main():
    draw_bg()

    screen.blit(big.render(str(p1),True,YELLOW),(50,50))
    screen.blit(big.render(str(p2),True,YELLOW),(950,50))

    screen.blit(font.render(f"ROUND {round_num}  x{multiplier}",True,YELLOW),(450,20))

    for i,a in enumerate(answers):
        row=i%4; col=i//4
        x=200+col*400; y=150+row*80

        pygame.draw.rect(screen,BLUE,(x,y,300,60),border_radius=12)

        if revealed[i]:
            if progress[i]<300: progress[i]+=10
            pygame.draw.rect(screen,(255,255,255),(x,y,progress[i],60))

            t=font.render(a,True,(0,0,0))
            s=font.render(str(scores[i]*multiplier),True,(0,0,0))
            screen.blit(t,(x+20,y+15))
            screen.blit(s,(x+240,y+15))

    for i in range(strikes):
        img=pygame.transform.scale(strike_img,(120,120))
        screen.blit(img,(WIDTH//2-60,100+i*120))

    screen.blit(font.render(question,True,WHITE),(300,600))

# ===== INPUT =====
user=""
def handle(e):
    global user,strikes,round_score,turn,p1,p2,steal,round_num

    if e.type!=pygame.KEYDOWN: return

    if e.unicode.isalpha() or e.unicode==" ":
        user+=e.unicode.upper()

    if e.key==pygame.K_BACKSPACE:
        user=user[:-1]

    if e.key==pygame.K_RETURN:
        found=False
        for i,a in enumerate(answers):
            if user==a and not revealed[i]:
                revealed[i]=True
                round_score+=scores[i]*multiplier
                if snd_correct: snd_correct.play()
                if i==0 and snd_saysay: snd_saysay.play()
                found=True

        if not found:
            strikes+=1
            if snd_wrong: snd_wrong.play()

        user=""

        if strikes>=3 and not steal:
            steal=True
            turn=2 if turn==1 else 1
            return

        if strikes>=4 and steal:
            if turn==1: p1+=round_score
            else: p2+=round_score
            next_round()

# ===== FLOW =====
def next_round():
    global round_num
    round_num+=1
    load_q()

def prev_round():
    global history_index
    if history_index>0:
        history_index-=1
        load_history(history_index)

def faceoff():
    if snd_bell: snd_bell.play()
    for _ in range(120):
        draw_bg()
        txt=big.render("FACE OFF!",True,YELLOW)
        screen.blit(txt,(420,300))
        pygame.display.flip()
        clock.tick(60)

# ===== BIG MONEY =====
def big_money():
    total=0
    qs=random.sample(big_q,5)

    for q in qs:
        total+=ask(q,15)

    if snd_repeat: snd_repeat.play()

    for q in qs:
        total+=ask(q,20)

    return total

def ask(q, time_limit):
    user=""; timer=time_limit*60

    while timer>0:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()

            if e.type==pygame.KEYDOWN:
                if e.unicode.isalpha(): user+=e.unicode.upper()
                if e.key==pygame.K_BACKSPACE: user=user[:-1]
                if e.key==pygame.K_RETURN:
                    if user in q["answers"]:
                        return q["answers"][user]
                    return 0

        draw_bg()
        screen.blit(big.render("BIG MONEY",True,YELLOW),(400,50))
        screen.blit(font.render(q["question"],True,WHITE),(200,200))
        screen.blit(big.render(user,True,YELLOW),(300,300))
        screen.blit(big.render(str(timer//60),True,YELLOW),(900,100))

        pygame.display.flip()
        clock.tick(60)
        timer-=1

    return 0

# ===== ENDING =====
particles=[]
def ending():
    if snd_applause: snd_applause.play()

    for _ in range(300):
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()

        draw_main()

        win="TEAM 1 WIN!" if p1>p2 else "TEAM 2 WIN!"
        screen.blit(big.render(win,True,YELLOW),(420,320))

        pygame.display.flip()
        clock.tick(60)

# ===== RUN =====
faceoff()
load_q()

while True:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()

        handle(e)

        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_n: next_round()
            if e.key==pygame.K_p: prev_round()
            if e.key==pygame.K_b:
                score=big_money()
                if turn==1: p1+=score
                else: p2+=score
                ending()

    draw_main()
    pygame.display.flip()
    clock.tick(60)
