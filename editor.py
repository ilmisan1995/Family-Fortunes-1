import pygame, sys, json, os

pygame.init()

W, H = 1200, 800
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("ALL-IN-ONE FAMILY FORTUNES EDITOR")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 22)
big  = pygame.font.SysFont("arial", 32, True)

WHITE=(255,255,255)
BLACK=(0,0,0)
BLUE=(30,60,150)
PURPLE=(80,40,180)
YELLOW=(255,220,0)
GRAY=(200,200,200)

FILE="question.json"

# ===== LOAD =====
if os.path.exists(FILE):
    data=json.load(open(FILE))
else:
    data={"main_game":[], "big_money":[]}

# ===== STATE =====
mode="MAIN"   # MAIN / BIG
preview="MODERN"  # MODERN / RETRO

question=""
answers=[]
scores=[]

input_text=""
active_field="QUESTION"

# ===== BUTTON =====
class Button:
    def __init__(self, text, x,y,w,h):
        self.text=text
        self.rect=pygame.Rect(x,y,w,h)

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        txt=font.render(self.text, True, BLACK)
        screen.blit(txt,(self.rect.x+10,self.rect.y+8))

    def click(self, pos):
        return self.rect.collidepoint(pos)

btn_add   = Button("ADD ANSWER", 50, 650, 150, 40)
btn_save  = Button("SAVE", 220, 650, 100, 40)
btn_mode  = Button("SWITCH MODE", 340, 650, 150, 40)
btn_prev  = Button("PREVIEW", 510, 650, 150, 40)

# ===== SAVE =====
def save_data():
    if mode=="MAIN":
        if len(answers)<3: return
        data["main_game"].append({
            "question":question,
            "answers":[[answers[i], int(scores[i])] for i in range(len(answers))]
        })
    else:
        data["big_money"].append({
            "question":question,
            "answers":{answers[i]:int(scores[i]) for i in range(len(answers))}
        })

    with open(FILE,"w") as f:
        json.dump(data,f,indent=2)

# ===== DRAW MODERN =====
def draw_modern():
    pygame.draw.rect(screen, PURPLE, (700, 100, 450, 500))
    for i in range(8):
        y=120+i*50
        pygame.draw.rect(screen,(120,80,220),(720,y,300,40),border_radius=20)

        if i<len(answers):
            txt=font.render(f"{i+1}. {answers[i]} ({scores[i]})",True,WHITE)
            screen.blit(txt,(730,y+8))

# ===== DRAW RETRO =====
def draw_retro():
    pygame.draw.rect(screen, BLACK, (700,100,450,500))
    for x in range(700,1150,40):
        pygame.draw.line(screen,(50,50,50),(x,100),(x,600))
    for y in range(100,600,40):
        pygame.draw.line(screen,(50,50,50),(700,y),(1150,y))

    for i in range(len(answers)):
        y=120+i*50
        txt=font.render(f"{i+1} {answers[i]}",True,YELLOW)
        scr=font.render(str(scores[i]),True,YELLOW)
        screen.blit(txt,(720,y))
        screen.blit(scr,(1050,y))

# ===== LOOP =====
while True:
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()

        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_BACKSPACE:
                input_text=input_text[:-1]
            elif e.key==pygame.K_RETURN:
                if active_field=="QUESTION":
                    question=input_text
                elif active_field=="ANSWER":
                    answers.append(input_text)
                elif active_field=="SCORE":
                    if input_text.isdigit():
                        scores.append(input_text)
                input_text=""
            else:
                input_text+=e.unicode.upper()

        if e.type==pygame.MOUSEBUTTONDOWN:
            if btn_add.click(e.pos):
                active_field="ANSWER"
            if btn_save.click(e.pos):
                save_data()
                question=""; answers=[]; scores=[]
            if btn_mode.click(e.pos):
                mode="BIG" if mode=="MAIN" else "MAIN"
            if btn_prev.click(e.pos):
                preview="RETRO" if preview=="MODERN" else "MODERN"

    screen.fill(BLUE)

    # LEFT PANEL
    screen.blit(big.render(f"MODE: {mode}",True,YELLOW),(50,20))
    screen.blit(font.render("QUESTION:",True,WHITE),(50,80))
    screen.blit(font.render(question,True,YELLOW),(50,110))

    screen.blit(font.render("INPUT:",True,WHITE),(50,180))
    screen.blit(font.render(input_text,True,YELLOW),(50,210))

    y=260
    for i in range(len(answers)):
        txt=f"{i+1}. {answers[i]} ({scores[i]})"
        screen.blit(font.render(txt,True,WHITE),(50,y))
        y+=30

    # BUTTONS
    btn_add.draw()
    btn_save.draw()
    btn_mode.draw()
    btn_prev.draw()

    # PREVIEW
    screen.blit(big.render(f"PREVIEW: {preview}",True,YELLOW),(700,50))
    if preview=="MODERN":
        draw_modern()
    else:
        draw_retro()

    pygame.display.flip()
    clock.tick(60)
