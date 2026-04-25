# family_fortunes_broadcast.py
import pygame, sys, math, random, json, os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Family Fortunes - BROADCAST MASTER")
clock = pygame.time.Clock()

# ========= SAFE LOADERS =========
def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        # fallback kosong
        surf = pygame.Surface((200, 100), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255,255,255), (0,0,200,100), 3)
        return surf

def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except:
        return None

# ========= ASSETS =========
logo = load_image("logo.png")
strike_img = load_image("strike.png")

top_sound = load_sound("top.wav")
correct_sound = load_sound("correct.wav")
wrong_sound = load_sound("wrong.wav")
repeat_sound = load_sound("repeat.wav")
bell_sound = load_sound("bell.wav")
saysay = load_sound("saysay.wav")
applause = load_sound("applause.wav")

# ========= FONT =========
def f(size): return pygame.font.SysFont("arial", size, bold=True)
font = f(24)
big = f(44)

WHITE=(255,255,255)
YELLOW=(255,200,0)
BLUE=(40,80,200)

# ========= LOAD JSON =========
if not os.path.exists("question.json"):
    print("question.json tidak ditemukan!")
    pygame.quit(); sys.exit()

with open("question.json","r") as file:
    data = json.load(file)

main_questions = data["main_game"]
big_questions = data["big_money"]

# ========= BACKGROUND =========
bg_offset=0
shine_x=-300
led_phase=0

def draw_bg():
    global bg_offset, shine_x, led_phase

    for y in range(HEIGHT):
        c = 120 + int(40*math.sin((y+bg_offset)*0.03))
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

# ========= OPENING =========
def opening():
    scale, alpha = 0.3, 0
    for _ in range(240):
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()

        draw_bg()

        w=int(logo.get_width()*scale)
        h=int(logo.get_height()*scale)
        img=pygame.transform.smoothscale(logo,(w,h))
        img.set_alpha(alpha)

        screen.blit(img,(WIDTH//2-w//2,HEIGHT//2-h//2))

        if scale<1.05: scale+=0.01
        if alpha<255: alpha+=5

        pygame.display.flip()
        clock.tick(60)

# ========= GAME STATE =========
answers=[]; scores=[]; revealed=[]; progress=[]
round_score=0; strikes=0; turn=1; p1=0; p2=0; steal=False
question=""; top_index=0

# history
history=[]
history_index=-1

# ========= LOAD QUESTION =========
def load_q():
    global answers,scores,revealed,progress
    global round_score,strikes,steal,top_index
    global history, history_index

    q=random.choice(main_questions)
    q["answers"].sort(key=lambda x:x[1], reverse=True)

    answers=[x[0] for x in q["answers"]]
    scores=[x[1] for x in q["answers"]]
    revealed=[False]*len(answers)
    progress=[0]*len(answers)

    round_score=0
    strikes=0
    steal=False
    top_index=0

    # save history
    state={
        "answers":answers[:],
        "scores":scores[:],
        "revealed":revealed[:],
        "progress":progress[:],
        "round_score":round_score,
        "strikes":strikes,
        "question":q["question"]
    }

    history = history[:history_index+1]
    history.append(state)
    history_index+=1

    return q["question"]

def load_history(idx):
    global answers,scores,revealed,progress,round_score,strikes,question
    state=history[idx]
    answers=state["answers"][:]
    scores=state["scores"][:]
    revealed=state["revealed"][:]
    progress=state["progress"][:]
    round_score=state["round_score"]
    strikes=state["strikes"]
    question=state["question"]

# ========= DRAW =========
def draw():
    draw_bg()

    # score
    screen.blit(big.render(str(p1),True,YELLOW),(50,50))
    screen.blit(big.render(str(p2),True,YELLOW),(950,50))

    # round
    rtxt=font.render(f"ROUND {history_index+1}",True,YELLOW)
    screen.blit(rtxt,(480,20))

    for i,a in enumerate(answers):
        row=i%4; col=i//4
        x=200+col*400; y=150+row*80

        color = (255,200,0) if i==top_index else BLUE
        pygame.draw.rect(screen,color,(x,y,300,60),border_radius=12)

        if revealed[i]:
            if progress[i]<300: progress[i]+=10
            pygame.draw.rect(screen,(255,255,255),(x,y,progress[i],60))

            t=font.render(a,True,(0,0,0))
            s=font.render(str(scores[i]),True,(0,0,0))
            screen.blit(t,(x+20,y+15))
            screen.blit(s,(x+240,y+15))

    # strike
    for i in range(strikes):
        img=pygame.transform.scale(strike_img,(120,120))
        screen.blit(img,(WIDTH//2-60,100+i*120))

    # question
    qtxt=font.render(question,True,WHITE)
    screen.blit(qtxt,(300,600))

# ========= INPUT =========
user=""

def handle(e):
    global user,strikes,round_score,turn,p1,p2,steal

    if e.type!=pygame.KEYDOWN: return

    if e.unicode.isalpha():
        user+=e.unicode.upper()

    if e.key==pygame.K_BACKSPACE:
        user=user[:-1]

    if e.key==pygame.K_RETURN:
        found=False
        for i,a in enumerate(answers):
            if user==a and not revealed[i]:
                revealed[i]=True
                round_score+=scores[i]
                if correct_sound: correct_sound.play()
                if i==0 and saysay: saysay.play()
                found=True

        if not found:
            strikes+=1
            if wrong_sound: wrong_sound.play()

        user=""

        if strikes>=3 and not steal:
            steal=True
            turn=2 if turn==1 else 1
            return

        if strikes>=4 and steal:
            if turn==1: p1+=round_score
            else: p2+=round_score
            next_round()

# ========= FLOW =========
def next_round():
    global question,turn
    question=load_q()
    turn=random.choice([1,2])

def faceoff():
    if bell_sound: bell_sound.play()
    for _ in range(120):
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        draw_bg()
        txt=big.render("FACE OFF!",True,YELLOW)
        screen.blit(txt,(420,300))
        pygame.display.flip()
        clock.tick(60)

# ========= BIG MONEY =========
def big_money():
    score=0
    qset=random.sample(big_questions,5)

    for q in qset:
        answered=""
        timer=0

        while timer<300:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit(); sys.exit()

                if e.type==pygame.KEYDOWN:
                    if e.unicode.isalpha():
                        answered+=e.unicode.upper()
                    if e.key==pygame.K_RETURN:
                        if answered in q["answers"]:
                            score+=q["answers"][answered]
                        answered=""
                        return score

            draw_bg()
            screen.blit(big.render("BIG MONEY",True,YELLOW),(400,50))
            screen.blit(big.render(str(score),True,WHITE),(500,120))
            pygame.display.flip()
            clock.tick(60)
            timer+=1

    return score

# ========= ENDING =========
particles=[]
def spawn_confetti():
    for _ in range(100):
        particles.append([random.randint(0,WIDTH),0,random.randint(2,6)])

def update_confetti():
    for p in particles:
        p[1]+=p[2]
        pygame.draw.circle(screen,(255,200,0),(p[0],p[1]),3)

def ending():
    spawn_confetti()
    if applause: applause.play()

    for _ in range(300):
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()

        draw()
        update_confetti()

        win="TEAM 1 WIN!" if p1>p2 else "TEAM 2 WIN!"
        screen.blit(big.render(win,True,YELLOW),(420,320))

        pygame.display.flip()
        clock.tick(60)

# ========= RUN =========
opening()
faceoff()
next_round()

while True:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()

        handle(e)

        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_n:
                next_round()
            if e.key==pygame.K_p and history_index>0:
                history_index-=1
                load_history(history_index)
            if e.key==pygame.K_b:
                print("BIG MONEY:", big_money())

    draw()
    pygame.display.flip()
    clock.tick(60)
