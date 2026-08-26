import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys, random, math, time, datetime, json
from pypresence import Presence
from setupvars import *

doRPC = False

if doRPC:
    RPC = Presence(1541135004078309517)
    RPC.connect()
pygame.init()
pygame.font.init()
pygame.mixer.init()

def load(data):
    global fishesHeld, balance, reelTime, maxFishes, fishSpawnCap, fishScaredRange, catchTimer, fishCount, fullscreen, lowGraphicsMode, volume, theme, wideMode, fishSFX, fastSun, achs
    with open('.saves/save.philooxy', 'r') as f:
        lines = f.readlines()
        if data == "var":
            fishesHeld = json.loads(lines[0])
            balance = int(lines[1])
            reelTime = json.loads(lines[2])[0]
            maxFishes = json.loads(lines[3])[0]
            fishSpawnCap = json.loads(lines[4])[0]
            fishScaredRange = json.loads(lines[5])[0]
            catchTimer = json.loads(lines[6])[0]
            fishCount = int(lines[7])
        elif data == "bought":
            reeltimeupgrade.bought = json.loads(lines[2])[1]
            hookupgrade.bought = json.loads(lines[3])[1]
            spawncapupgrade.bought = json.loads(lines[4])[1]
            scaredrangeupgrade.bought = json.loads(lines[5])[1]
            catchtimeupgrade.bought = json.loads(lines[6])[1]
        elif data == "achs":
            achs_temp = json.loads(lines[8])
            j = 0
            for i in achs:
                try:
                    i.got = bool(int(achs_temp[j]))
                except IndexError:
                    i.got = "no"

                if i.got == True:
                    i.got2 = True

                if i.got == False:
                    i.got = "no"
                    i.got2 = "no2"
                j += 1
    if data == "settings":
        with open('settings.philooxy', 'r') as f:
            lines = f.readlines()
            fullscreen = bool(int(lines[0]))
            lowGraphicsMode = bool(int(lines[1]))
            volume = float(lines[2])
            #theme = int(lines[3])

            wideMode = bool(int(lines[4]))
            fishSFX = bool(int(lines[5]))
            fastSun = bool(int(lines[6]))


load("var")
load("settings")
#i have no idea what to name this
def buttonCheck(rect, image, slider):
    global startTransitionY, startTransitionX, hovering
    check = False
    image = pygame.transform.scale(image, (rect[2], rect[3]))
    if rect.collidepoint(pygame.mouse.get_pos()):
        hovering = True
        match startTransitionY:
            case 0 | 100 | 200:
                match startTransitionX:
                    case 0 | 100 | 200:
                        check = True
    if check and not(slider):
        image = pygame.transform.scale(image, (rect[2]*1.2, rect[3]*1.2))
        rect = rect.inflate(rect[2]*0.2, rect[3]*0.2)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    return rect, image, check

def checkClick(resetClick):
    global isClicking
    click = False
    if pygame.mouse.get_pressed()[0] == False and isClicking == True:
        isClicking = False
    elif pygame.mouse.get_pressed()[0]:
        if isClicking == False:
            click = True
        if resetClick:
            isClicking = True
    return click

def updateButton(baseRect, image):
    update = False
    image = pygame.transform.scale(image, (baseRect[2], baseRect[3]))
    check = False

    rect, image, check = buttonCheck(baseRect, image, False)

    if check:
        click = checkClick(False)
        if click:
            update = True

    screen.blit(image, rect)

    return update

class button():
    def __init__(self, newarea, image):
        self.image = pygame.image.load(image)
        self.newarea = newarea

    def update(self, rect):
        global area
        update = updateButton(pygame.Rect(rect), self.image)
        if update:
            area = self.newarea

class toggleButton():
    def __init__(self, var):
        self.image_on = toggle_on
        self.image_off = toggle_off
        if var:
            self.var = True
        else:
            self.var = False
    def update(self, var, rect):
        toggle = False
        if var:
            self.image = self.image_on
        else:
            self.image = self.image_off
        update = updateButton(pygame.Rect(rect), self.image)
        if update:
            toggle = True
        if toggle:
            if self.var:
                self.var = False
            else:
                self.var = True
        return self.var

fishSFX_toggle = toggleButton(fishSFX)
fullscreen_toggle = toggleButton(fullscreen)
wideMode_toggle = toggleButton(wideMode)
fastSun_toggle = toggleButton(fastSun)
lowGraphicsMode_toggle = toggleButton(lowGraphicsMode)

class slider():
    def __init__(self, var, maxvar):
        self.image_bar = slider_bar
        self.image_ball = slider_ball
        self.max = maxvar
        self.pos = (var/maxvar)*100
        self.click = False
    def update(self, var, pos):
        global isClicking
        check = False
        click = False
        screen.blit(self.image_bar, pos)
        rect = pygame.Rect(pos[0]-15, pos[1]-15, 130, 40)
        useless, useless, check = buttonCheck(rect, self.image_bar, True)
        if check:
            
            if pygame.mouse.get_pressed()[0] == False and self.click == True:
                self.click = False
            elif pygame.mouse.get_pressed()[0]:
                if self.click == False:
                    click = True

            if click:
                self.pos = pygame.mouse.get_pos()[0]-pos[0]
                if self.pos > 100:
                    self.pos = 100
                elif self.pos < 0:
                    self.pos = 0
        screen.blit(self.image_ball, (pos[0]+self.pos-7.5, pos[1]-2.5))

        var = self.pos/100*self.max

        return var

themeSlider = slider(theme, 4)
volumeSlider = slider(volume*100, 100)

def setVolume(volume):
    ykwtm.set_volume(volume)
    mus_menu.set_volume(volume)
    mus_fishing.set_volume(volume)

class fishy():
    def __init__(self):
        global fishes, fishingrect, fishingrect2

        #print("You know what that means")

        self.pos = (random.randint(-200, 200), random.randint(20, 200))
        self.type = random.randint(1,5)
        if self.type == 3:
            self.type = 2
        else:
            self.type = 1
        self.dir = random.randint(1, 2)
        self.caught = False
        self.scared = 0
        self.speed = random.random()+0.5*self.type
        self.speed2 = self.speed
        self.anim = 0
        self.catchTimer = -31
        if self.type == 1:
            self.catchTime = 50
        if self.type == 2:
            self.catchTime = 25

        self.imagepath = f'assets/fishes/fish{self.type}'
        self.image = pygame.image.load(f'{self.imagepath}_0.png')
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], self.rect[2], self.rect[3])

        self.rotate = random.randint(0,4)*90
        self.bobber = ""

        fishes.append(self)

    def update(self):
        global moving, offsetX, offsetY, fishCount, bobberFallAnim, reelAnim, fishes, fishesHeld, maxFishes, fishCaughtArray, catchTimer, scaredCounter, outranFish, clickFish

        self.image = pygame.image.load(f'{self.imagepath}_{int((self.anim*self.speed/10)%2)}.png')

        self.speed = self.speed2

        self.anim += 1
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.caught == True:
            self.image = pygame.transform.rotate(self.image, self.rotate)

        if self.pos[0] < -180:
            self.dir = 1
        elif self.pos [0] > 180:
            self.dir = 2

        if self.catchTimer > -30:
            self.catchTimer -= 1


        #if self.rect.colliderect(fishingrect2) and (moving == True or self.caught == True):
        #    self.scared = 30
        if self.scared > 0:
            self.speed = 3*self.speed2

            if self.caught == False:
                if self.pos[0] > self.bobber.pos[0]:
                    self.dir = 1
                elif self.pos[0] < self.bobber.pos[0]:
                    self.dir = 2

            self.scared -= 1

        if self.bobber != "":
            if self.bobber.reel == False:
                if -30 < self.catchTimer <= 0:
                    self.caught = False

                if self.catchTimer == 0:
                    fishCaughtArray.remove(self)
                    self.pos = (self.pos[0], self.pos[1]+(16+-64*random.randint(0,1)))
                    if self.pos[1] < 20:
                        self.pos = (self.pos[0], 20)

        if self.dir == 2:
            self.pos = (self.pos[0]-1*self.speed, self.pos[1])
        else:
            self.pos = (self.pos[0]+1*self.speed, self.pos[1])

        if self.caught == True:
            self.pos = (self.bobber.pos[0], self.bobber.pos[1]+24+11)
            if self.bobber.pos[0] <= -40 and self.bobber.pos[1] <= 0 and self.bobber.cast == False:
                self.bobber.reel = True

        if self.pos[0] > 320 or self.pos[0] < -320 or ((self.pos[1] > 200) and self.caught == False) or 0 < startTransitionY < 100:
            if not(0 < startTransitionY < 100):
                scaredCounter += 1
            fishes.remove(self)

        self.rect[0], self.rect[1] = WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1]

        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            clickFish = True

        screen.blit(self.image, self.rect)

#basic upgrade item
class shopItem():
    def __init__(self, name, desc, image, cost, costIncrement, increment, cap):
        self.image = pygame.image.load(image)
        self.imagepath = image
        self.cost = cost
        self.cost2 = cost
        self.costIncrement = costIncrement
        self.increment = increment
        self.name = name
        self.desc = desc
        self.cap = cap
        self.isClicking = False
        self.upgrade = False
        self.capCheck = True
        self.capCheck2 = True
        self.bought = 0

    def update(self, var, rect):
        global balance, hovering, startTransitionY, startTransitionX

        check = False
        click = False
        self.upgrade = False

        self.rect, self.image, check = buttonCheck(pygame.Rect(rect), self.image, False)

        if check:

            self.cost = self.cost2 + self.costIncrement*self.bought

            if self.increment > 0:
                self.capCheck = (var+self.increment < self.cap)
            elif self.increment < 0:
                self.capCheck = (var+self.increment > self.cap)

            if self.increment > 0:
                self.capCheck2 = (var < self.cap)
            elif self.increment < 0:
                self.capCheck2 = (var > self.cap)

            click = checkClick(True)
            if click:
                if balance - self.cost >= 0:

                    if self.capCheck2:
                        self.bought += 1
                        var += self.increment
                        balance -= self.cost

            desc1, desc1Rect = renderText(self.desc, ut_xs)
            desc1Rect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + 10 + 20)
            screen.blit(desc1, desc1Rect)

            if self.capCheck2:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                if self.increment > 0:
                    self.capCheck2 = var+self.increment > self.cap
                elif self.increment < 0:
                    self.capCheck2 = var+self.increment < self.cap

                if self.capCheck2:
                    var2 = self.cap
                else:
                    var2 = var+self.increment
                desc2Text = f'{var} -> {var2}'

                cost, costRect = renderText(f'Cost: ${self.cost}', ut_xs)
                costRect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + desc1Rect[3]/2 + 20 + 16)
                screen.blit(cost, costRect)

            else:
                var = self.cap
                desc2Text = f'MAX ({var})'
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)

            desc2, desc2Rect = renderText(desc2Text, ut_xs)
            desc2Rect.center = (self.rect.center[0], self.rect.center[1] + self.rect[3]/2 + desc1Rect[3]/2 + 20 + 30)
            screen.blit(desc2, desc2Rect)

        name, nameRect = renderText(self.name, ut_s)
        nameRect.center = (self.rect.center[0], self.rect.bottom + 10)
        screen.blit(name, nameRect)

        screen.blit(self.image, self.rect)

        return var

class achievement():
    def __init__(self, icon, name, desc, hidden):
        global achs
        self.icon = pygame.image.load(icon)
        self.bg = ach_bg
        self.name = name
        self.desc = desc
        self.got = "no"
        self.got2 = "no2"
        self.easing = 0
        self.showing = False
        self.hidden = hidden
        achs.append(self)
    def update(self, got):
        global achs_unlocked, achs, achs_showing, showingAch
        
        if got and (self.got2 == "no2"):
            self.got = True
            if showingAch == "":
                showingAch = self
                self.got2 = False

        if (not(self.got2)) and not(self in achs_unlocked) and showingAch == self:
            self.showing = True
            if self.easing == 0:
                showingAch = self
                self.got = True
                #achs_unlocked.append(self)
                achs_showing.append(self)
                self.easing += 0.01
            if self.easing <= 5:
                self.pos = pygame.math.lerp(220, 0, ease(self.easing))
                self.easing += 0.01
            elif self.easing <= 6:
                self.pos = pygame.math.lerp(0, 220, ease(self.easing-5))
                self.easing += 0.01
            elif self.easing == 6.0:
                self.got2 = True
                achs_showing.remove(self)
                self.showing = False
                self.easing += 1
            else:
                showingAch = ""

            rect = pygame.Rect(-self.pos-5, HEIGHT-75, 220, 75)
            screen.blit(self.bg, rect)

            name, nameRect = renderText(self.name, ut_s)
            nameRect.topright = (rect[0]+210-8, HEIGHT-75+16)
            screen.blit(name, nameRect)

            desc, descRect = renderText(self.desc, ut_xs)
            descRect.topright = (rect[0]+210-8, HEIGHT-20)
            screen.blit(desc, descRect)

            screen.blit(self.icon, (rect[0]+16, HEIGHT-75+18))


    def draw(self, rect):
        if self.got == True:
            tempicon = self.icon
        elif self.got == "no":
            tempicon = ach_locked
        rect, tempicon, check = buttonCheck(rect, tempicon, False)
        if check:
            if self.hidden and self.got == "no":
                tempname = "???"
                tempdesc = "???"
            else:
                tempname = self.name
                tempdesc = self.desc
            name, nameRect = renderText(tempname, ut_s)
            nameRect.center = (rect[0]+rect[2]/2, rect[1]+rect[3]/2+rect[3])
            screen.blit(name, nameRect)

            desc, descRect = renderText(tempdesc, ut_xs)
            descRect.center = (nameRect.center[0], nameRect.center[1]+20)
            screen.blit(desc, descRect)
        screen.blit(tempicon, rect)


ach_realistic_check = achievement("assets/achs/ach_realistic.png", "Realistic Fishing", "Catch a fish without moving", False)
ach_scared_check = achievement("assets/achs/ach_scared.png", "Fish Fear Me", "Scare 5 fish off the screen", False)
#ach_outrun_check = achievement("assets/achs/ach_outrun.png", "You Can't Run", "Outrun a fish and catch it", False)
ach_click_check = achievement("assets/achs/ach_click.png", "Not How You Do It", "Click a fish", True)
showingAch = ""
load("achs")
#upgrades
hookupgrade = shopItem("Hook upgrade", "Increase how much fish you can hold", "assets/upgrade/hookupgrade.png", 50, 25, 3, 50)
spawncapupgrade = shopItem("Max fish upgrade", "Increase how much fish spawn at a time", "assets/upgrade/maxfishupgrade.png", 30, 20, 1, 20)
reeltimeupgrade = shopItem("Reel time upgrade", "Decrease the time to reel in fish", "assets/upgrade/reelupgrade.png", 25, 15, -5, 10)
scaredrangeupgrade = shopItem("Better lure", "Decrease the area where fish get scared", "assets/upgrade/scaredrangeupgrade.png", 55, 5, -4, 16)
catchtimeupgrade = shopItem("Hook glue", "Increase time that fish stay on hook", "assets/upgrade/catchtimeupgrade.png", 40, 20, 20, 200)
load("bought")
#buttons
startbutton = button("fishing", "assets/button/fishbutton.png")
shopbutton = button("shop", "assets/button/shopbutton.png")
settingsbutton = button("settings", "assets/button/settingsbutton.png")
exitbutton = button("exit", "assets/button/exitbutton.png")
sellbutton = button("sell", "assets/button/sellfishbutton.png")
achbutton = button("achs", "assets/button/achbutton.png")

homebutton = button("title", "assets/button/homebutton.png")
homebutton_up = button("title", "assets/button/homebutton-up.png")
homebutton_right = button("title", "assets/button/homebutton-right.png")
homebutton_down = button("title", "assets/button/homebutton-down.png")

minute, hour = 0, 1

#functions
def checkSunset():

    global sunsetCheck, sunriseCheck, nightCheck, hour, minute, fastSun, theme, sunLerp

    if fastSun:
        minute += 1
        if minute > 60:
            minute = 1
            hour += 1
        if hour > 23:
            hour = 0

    else:
        now = datetime.datetime.now()

        hour = int(now.strftime("%H"))
        minute = int(now.strftime("%m"))

    if theme == 3 or theme == 4:
        hour = 23
        minute = 0
    if theme == 2:
        hour = 5
        minute = 30
    if theme == 1:
        hour = 12
        minute = 0

    if 0 <= hour <= 11:
        sunLerp = 1-(hour/11)-(minute/60)/11
    elif 12 <= hour <= 14:
        sunLerp = 0
    elif 15 <= hour <= 23:
        sunLerp = ((hour-15)/11)+(minute/60)/11

    sunsetCheck = 19 <= hour <= 23
    sunriseCheck = 0 <= hour <= 7
    nightCheck = 22 <= hour <= 23 or 0 <= hour <= 3

def checkSprites():
    global sunsetCheck, sunriseCheck, nightCheck, cloudsImage2, cloudsImage, fisherImage_normal, fisherImage_pull, fisherImage, dockImage, dockImage2, skyColor, waterImage, waterImage2, sunImage, bobberImage, titleImage

    cloudsImage2 = cloudsImage2_noon
    cloudsImage = cloudsImage_noon
    fisherImage_normal = fisherImage_normal_noon
    fisherImage_pull = fisherImage_pull_noon
    dockImage = dockImage_noon
    skyColor = skyColor_noon
    waterImage = waterImage_noon
    sunImage = sunImage_noon
    bobberImage = bobberImage_noon
    titleImage = titleImage_noon

    if sunsetCheck or sunriseCheck:
        cloudsImage2 = cloudsImage2_sunset
        cloudsImage = cloudsImage_sunset
        fisherImage_normal = fisherImage_normal_sunset
        fisherImage_pull = fisherImage_pull_sunset
        dockImage = dockImage_sunset
        skyColor = skyColor_sunset
        waterImage = waterImage_sunset
        sunImage = sunImage_sunset
        bobberImage = bobberImage_sunset
        titleImage = titleImage_sunset
    
    if nightCheck:
        cloudsImage2 = cloudsImage2_night
        cloudsImage = cloudsImage_night
        fisherImage_normal = fisherImage_normal_night
        fisherImage_pull = fisherImage_pull_night
        dockImage = dockImage_night
        skyColor = skyColor_night
        waterImage = waterImage_night
        sunImage = sunImage_night
        bobberImage = bobberImage_night
        titleImage = titleImage_night

    dockImage2 = pygame.transform.flip(dockImage, True, False)
    waterImage2 = waterImage
    fisherImage = fisherImage_normal

def checkMusic():
    global sunsetCheck, sunriseCheck, mus_fishing

    if sunsetCheck or sunriseCheck:
        mus_fishing = mus_hotel2
    else:
        mus_fishing = mus_paradise

checkSunset()
checkMusic()

setVolume(volume)

if sunsetCheck or sunriseCheck:
    mus_menu.play(loops=-1)

#Thank you to my friend for teaching me how to ease
def ease(t):
    return 1 - ((1 - t) ** 9)

prevMin = minute
if 0 <= hour <= 11:
    sunLerp = 1-(hour/11)-(minute/60)/11
elif 12 <= hour <= 14:
    sunLerp = 0
elif 15 <= hour <= 23:
    sunLerp = ((hour-14)/11)+(minute/60)/11

def drawbg():
    global cloudOffset, cloudOffset2, waterOffset, startTransitionY, skyColor, fishes, bobberPos, sunsetCheck, fishingrect, linePos, sunMove, sunsetCheck, sunriseCheck, nightCheck, sunLerp, prevMin, minute, hour, lowGraphicsMode, wideMode

    checkSunset()

    checkMusic()

    checkSprites()

    screen.fill(skyColor)

    if nightCheck:
        screen.blit(stars, (0,0+startTransitionY/10))

    if minute != prevMin:
        if 0 <= hour <= 11:
            sunLerp -= 1/660
        if 14 <= hour <= 23:
            sunLerp += 1/660

        prevMin = minute

        if sunLerp < 0:
            sunLerp = 0
        if sunLerp > 1:
            sunLerp = 1

    sunMove = pygame.math.lerp(-250, 250, sunLerp)

    screen.blit(sunImage, (320,startTransitionY+sunMove))

    if lowGraphicsMode == False:
        screen.blit(cloudsImage2, (cloudOffset2,15+startTransitionY/4))

        cloudOffset2 += 0.25
        if cloudOffset2 > 0:
            cloudOffset2 = -680

    screen.blit(cloudsImage, (cloudOffset, -40+2*startTransitionY/5))

    cloudOffset += 0.5
    if cloudOffset > 0:
        cloudOffset = -730

    screen.blit(waterImage, (-100-70*math.sin(waterOffset),startTransitionY))

    if lowGraphicsMode == False:
        screen.blit(waterImage2, (-100+100*math.sin(waterOffset),startTransitionY*3))

    if sunsetCheck or sunriseCheck:
        waterOffset += 0.005
    else:
        waterOffset += 0.01

    for i in fishes:
        i.update()

def drawTitle():
    screen.blit(titleImage, (100+700-startTransitionX*7, 50-700+startTransitionY*7))
    startbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
    shopbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
    settingsbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
    exitbutton.update((WIDTH/2 - 50+640-startTransitionX*6.4, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))
    achbutton.update((WIDTH-42+640-startTransitionX*6.4, HEIGHT-42 - 600 +startTransitionY*6, 32, 32))

def drawShop():
    global maxFishes, fishSpawnCap, reelTime, fishScaredRange, catchTimer, fishesHeld, balance
    maxFishes = hookupgrade.update(maxFishes, (WIDTH/4 - 16-startTransitionX*6.4, HEIGHT/4, 32, 32))
    fishSpawnCap = spawncapupgrade.update(fishSpawnCap, (2*WIDTH/4 - 16-startTransitionX*6.4, HEIGHT/4, 32, 32))
    reelTime = reeltimeupgrade.update(reelTime, (3*WIDTH/4 - 16-startTransitionX*6.4, HEIGHT/4, 32, 32))
    fishScaredRange = scaredrangeupgrade.update(fishScaredRange, (WIDTH/4 - 16-startTransitionX*6.4, 2*HEIGHT/4, 32, 32))
    catchTimer = catchtimeupgrade.update(catchTimer, (2*WIDTH/4 - 16-startTransitionX*6.4, 2*HEIGHT/4, 32, 32))
    homebutton_right.update((30-startTransitionX*6.4, 20, 100, 40))
    sellbutton.update((30-startTransitionX*6.4, HEIGHT - 60, 100, 40))

    fishCounter, fishCounterRect = renderText(f'Fish: {len(fishesHeld)}', ut)
    fishCounterRect.topright = (WIDTH-20-startTransitionX*6.4, 20)
    screen.blit(fishCounter, fishCounterRect)

    balanceCounter, balanceCounterRect = renderText(f'Balance: ${balance}', ut)
    balanceCounterRect.topright = (WIDTH-20-startTransitionX*6.4, 60)
    screen.blit(balanceCounter, balanceCounterRect)

def drawFishing():
    global wideMode, fisherImage_wide, fishcount, fishCaughtArray, maxFishes
    screen.blit(dockImage, (-2, startTransitionY*6-100))
    screen.blit(dockImage2, (WIDTH - 158, startTransitionY*6-100))

    fishCounter, fishCounterRect = renderText(f'Total Fish Caught: {fishCount}', ut)
    fishCounterRect.topright = (WIDTH - 20, 20 + startTransitionY*6)
    screen.blit(fishCounter, fishCounterRect)

    fishesHelder, fishesHelderRect = renderText(f'Fish Held: {len(fishCaughtArray)}/{maxFishes}', ut)
    fishesHelderRect.bottomright = (WIDTH - 20, HEIGHT - 20 + startTransitionY*6)
    screen.blit(fishesHelder, fishesHelderRect)

    homebutton_up.update((20, 20+startTransitionY*6, 100, 40))

def drawToggleSetting(text, coords, var, var_toggle):
    settings, settingsRect = renderText(text, ut)
    settingsRect.topright = coords
    screen.blit(settings, settingsRect)

    var = var_toggle.update(var, (coords[0]+10, coords[1]-2, 32, 32))
    
    return var

def drawSettings():
    global startTransitionX, fullscreen, wideMode, lowGraphicsMode, fishSFX, fastSun, theme, volume
    tempOffsetX = 1280-startTransitionX*6.4

    settings, settingsRect = renderText("Main Settings", ut_b)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 50)
    screen.blit(settings, settingsRect)

    fullscreen = drawToggleSetting("Fullscreen:", (WIDTH+tempOffsetX-82, 100), fullscreen, fullscreen_toggle)
    lowGraphicsMode = drawToggleSetting("Low Graphics Mode:", (WIDTH+tempOffsetX-82, 140), lowGraphicsMode, lowGraphicsMode_toggle)

    settings, settingsRect = renderText(f'Volume: {int(volume*100)}', ut)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 180)
    screen.blit(settings, settingsRect)

    volume = volumeSlider.update(volume, (WIDTH+tempOffsetX-82-100-7, 210))/100

    setVolume(volume)

    if theme == 0:
        themeText = "None"
    elif theme == 1:
        themeText = "Noon"
    elif theme == 2:
        themeText = "Sunset"
    else:
        themeText = "Night"

    settings, settingsRect = renderText(f'Theme: {themeText}', ut)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 250)
    screen.blit(settings, settingsRect) 

    theme = int(themeSlider.update(theme, (WIDTH+tempOffsetX-82-100-7, 280)))


    settings, settingsRect = renderText("silly settings", ut_b)
    settingsRect.topright = (WIDTH+tempOffsetX-82, 300)
    screen.blit(settings, settingsRect)

    wideMode = drawToggleSetting("W I D E M O D E :", (WIDTH+tempOffsetX-82, 350), wideMode, wideMode_toggle)
    fishSFX = drawToggleSetting("fish spawn sfx:", (WIDTH+tempOffsetX-82, 390), fishSFX, fishSFX_toggle)
    fastSun = drawToggleSetting("weird sun:", (WIDTH+tempOffsetX-82, 430), fastSun, fastSun_toggle)

    if wideMode:
        fisherImage_normal = fisherImage_wide

    homebutton.update((20+tempOffsetX, 20, 100, 40))

def save():
    global balance, reelTime, maxFishes, fishSpawnCap, fishScaredRange, catchTimer, fishCount, fishesHeld, reeltimeupgrade, fullscreen, lowGraphicsMode, volume, theme, wideMode, fishSFX, fastSun, achs
    achs_temp = []
    with open('.saves/save.philooxy', 'w') as f:
        reelTime = [reelTime, reeltimeupgrade.bought]
        maxFishes = [maxFishes, hookupgrade.bought]
        fishSpawnCap = [fishSpawnCap, spawncapupgrade.bought]
        fishScaredRange = [fishScaredRange, scaredrangeupgrade.bought]
        catchTimer = [catchTimer, catchtimeupgrade.bought]
        lines = [f'{balance}\n', f'{reelTime}\n', f'{maxFishes}\n', f'{fishSpawnCap}\n', f'{fishScaredRange}\n', f'{catchTimer}\n', f'{fishCount}\n']
        f.write(f'{fishesHeld}\n')
        f.writelines(lines)
        for i in achs:
            if i.got == "no":
                i.got = 0
            achs_temp.append(int(i.got))
        f.write(f'{achs_temp}\n')
    with open('settings.philooxy', 'w') as f:
        lines = [f'{int(fullscreen)}\n', f'{int(lowGraphicsMode)}\n', f'{float(volume)}\n', f'\n', f'{int(wideMode)}\n', f'{int(fishSFX)}\n', f'{int(fastSun)}\n']
        f.writelines(lines)

def renderText(text, font):
    text = font.render(text, False, (0,0,0))
    rect = text.get_rect()

    return text,rect

#achievement-related variables
moving2 = False
scaredCounter = 0
outranFish = False
clickFish = False

def updateAchs():
    global moving2, reelAnim, scaredCounter, outranFish, clickFish
    ach_realistic_check.update(not(moving2) and reelAnim)
    ach_scared_check.update(scaredCounter >= 5)
    #ach_outrun_check.update(outranFish) #removed because it was buggy
    ach_click_check.update(clickFish)

def drawAchs():
    homebutton_down.update((WIDTH-120-640+startTransitionX*6.4, HEIGHT-60-1200+startTransitionY*6, 100, 40))
    global achs
    for i in range(len(achs)):
        achs[i].draw( pygame.Rect((1+i%4)*(WIDTH/5)-640+startTransitionX*6.4, (1+int(i/4))*(HEIGHT/5)+(-1200+startTransitionY*6), 32, 32 ) )

def transition(transitionVar, lerpMin, lerpMax, easing, a):
    global lowGraphicsMode
    finishedTransition = False

    if a:
        check3 = transitionVar < lerpMax
    else:
        check3 = lerpMax < transitionVar

    if check3:
        transitionVar = pygame.math.lerp(lerpMin, lerpMax, ease(easing))
        easing += 0.01

        finishedTransition = False

        if a:
            check2 = lerpMax-0.3 <= transitionVar < lerpMax
        else:
            check2 = (lerpMax <= transitionVar < lerpMax+0.3)
        if check2:
            transitionVar = lerpMax

    elif transitionVar == float(lerpMax):
        easing = 0
        finishedTransition = True

    if lowGraphicsMode == True:
        transitionVar = lerpMax


    return transitionVar, easing, finishedTransition

startAnim = True

startTransitionX = 100


class bobber():
    global bobbers, fishScaredRange
    def __init__(self, controls, fisherPos, fisherFlip, linePos):
        self.pos = (0,0)
        bobbers.append(self)
        self.reel = False
        self.cast = True
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + 16 + self.pos[1], 32, 32)
        self.scaredRect = pygame.Rect(WIDTH/2 - fishScaredRange + self.pos[0], HEIGHT/2 - fishScaredRange + 16 + self.pos[1], 2*fishScaredRange, 2*fishScaredRange)
        self.image = bobberImage
        self.fishCaughtArray = []
        self.moving = False
        self.castAnimCounter = 0
        self.reelAnimCounter = 0
        self.fisher_normal = fisherImage_normal
        self.fisher_pull = fisherImage_pull
        self.controls = controls
        self.fisherFlip = fisherFlip
        self.fisherPos = fisherPos
        self.linePos = linePos
        self.linePos2 = self.linePos
        self.exponent = 0

    def update(self):
        global fishes, fishCaughtAray, maxFishes, outranFish, moving, wideMode
        for i in fishes:
            if i.rect.colliderect(self.rect) and not(i.caught) and len(fishCaughtArray) < maxFishes:
                if not(-30 < i.catchTimer <= 0):
                    i.caught = True
                    fishCaughtArray.append(i)
                    outranFish = True
                    i.bobber = self
                    if catchTimer < catchtimeupgrade.cap:
                        i.catchTimer = catchTimer + i.catchTime

            if i.rect.colliderect(self.scaredRect) and moving:
                i.scared = 30
                i.bobber = self
        bobberPos = (WIDTH/2+self.pos[0]-16, HEIGHT/2+self.pos[1]-16+startTransitionY*6)

        fisherImage = fisherImage_normal
        if self.reel and not(wideMode):
            fisherImage = fisherImage_pull

        if wideMode:
            fisherImage = fisherImage_wide

        if self.fisherFlip:
            fisherImage = pygame.transform.flip(fisherImage, True, False)

        if not(wideMode):
            screen.blit(fisherImage, (self.fisherPos[0], startTransitionY*6+self.fisherPos[1]-100))
        else:
            screen.blit(fisherImage, (-100, startTransitionY*6+fisherPos[1]-100))

        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2-5 + self.pos[1], 32, 32)
        self.scaredRect = pygame.Rect(WIDTH/2 - fishScaredRange + self.pos[0], HEIGHT/2 - fishScaredRange + self.pos[1]+11, 2*fishScaredRange, 2*fishScaredRange)

        pygame.draw.line(screen, (0,0,0), (self.linePos[0], self.linePos[1]+startTransitionY*6), (bobberPos[0]+15, bobberPos[1]), width=2)
        screen.blit(self.image, bobberPos)

    def move(self):
        global moving, bobberSpeed, moving2
        pressed_keys = pygame.key.get_pressed()

        moving = False

        if pressed_keys[self.controls[2]] and self.pos[0] > -200:
            moving = True
            self.pos = (self.pos[0] - 1*bobberSpeed, self.pos[1])
        if pressed_keys[self.controls[3]] and self.pos[0] < 200:
            moving = True
            self.pos = (self.pos[0] + 1*bobberSpeed, self.pos[1])
        if pressed_keys[self.controls[0]] and self.pos[1] > 0:
            moving = True
            self.pos = (self.pos[0], self.pos[1] - 1*bobberSpeed)
        if pressed_keys[self.controls[1]] and self.pos[1] < 200:
            moving = True
            self.pos = (self.pos[0], self.pos[1] + 1*bobberSpeed)

        if pressed_keys[self.controls[2]] and pressed_keys[self.controls[3]]:
            moving = False
        if pressed_keys[self.controls[0]] and pressed_keys[self.controls[1]]:
            moving = False

        if moving and not(self.cast):
            moving2 = True

    def castAnim(self):
        global moving, moving2

        moving = True
        if self.castAnimCounter < 1:
            self.pos = (-169, -124)
            self.exponent = 10
            self.pos = (self.pos[0], self.pos[1] -129)
        if self.castAnimCounter <= 97:
            self.pos = (self.pos[0] + 1, self.pos[1])
            self.exponent += 0.05
            self.pos = (self.pos[0], 100*math.sin(self.exponent)-70)
            self.castAnimCounter += 1
        else:
            self.pos = (self.pos[0], 0)
            self.cast = False
            moving2 = False
            self.castAnimCounter = 0

    def reelAnim(self):
        global reelTime, fishCaughtArray, xmove_temp, ymove_temp, fishCount, fishes
        tempReelTime = reelTime*(len(fishCaughtArray))/2
        if not(self.fisherFlip):
            self.linePos = (self.linePos2[0]-10, self.linePos2[1]-10)
        else:
            self.linePos = (self.linePos2[0]+10, self.linePos2[1]-10)
        if self.reelAnimCounter == 0:
            xmove_temp = ((WIDTH/2+self.pos[0])-142)/tempReelTime
            ymove_temp = ((HEIGHT/2+self.pos[1])-102)/tempReelTime
            self.reelAnimCounter = 1
        if self.reelAnimCounter < tempReelTime+1:
            self.pos = (self.pos[0]-xmove_temp, self.pos[1]-ymove_temp)
            self.reelAnimCounter += 1
        if self.reelAnimCounter >= tempReelTime+1:
            self.castAnimCounter = 0
            self.reelAnimCounter = 0

            while len(fishCaughtArray) > 0:
                for i in fishes:
                    if i.caught == True:
                        fishes.remove(i)
                        fishCaughtArray.remove(i)
                        i.caught == False
                        fishCount += 1
                        fishesHeld.append(i.type)
            self.linePos = self.linePos2
            self.reel = False
            self.cast = True
            self.reelAnimCounter = 0

bobber1 = bobber([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT], (0,0), False, (150, 101))
#bobber2 = bobber([pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d], (WIDTH-150,0), True, (WIDTH-140, 101))

def main(area):
    global bobberFallAnim, fishingMusic, reelAnim, menuMusic, startTransitionY, startTransitionX, offsetX, offsetY, bobberSpeed, bobberFall, bobberReel, exponent, waterOffset, fishCount, fishingrect, fishingrect2, moving, fishes, cloudOffset, cloudOffset2, reelTime, linePos, fishSpawnCap, fishCaughtArray, fishesHeld, balance, fisherImage, fishSFX, bobberPos, easingY, easingX, run, sunsetCheck, sunriseCheck, nightCheck, lowGraphicsMode, wideMode, fullscreen, startAnim, doRPC, moving2

    drawbg()

    if area == "exit":
        run = False
        save()

    if area == "sell":
        for i in fishesHeld:
            if i == 1:
                balance += 5
            elif i == 2:
                balance += 10
            fishesHeld.remove(i)
        area = "shop"

    if area == "title":

        if menuMusic == False:
            while len(fishes) > 0:
                for i in fishes:
                    fishes.remove(i)

            menuMusic = True
            if not(sunsetCheck) and not(sunriseCheck):
                pygame.mixer.stop()
                mus_menu.play(loops=-1)
            bobberFallAnim = True
            reelAnim = False
            bobberFall = 0
            bobberReel = 0
            offsetX = 0
            offsetY = 0
            fishCaughtArray = []
            fishingMusic = False
            if sunsetCheck or sunriseCheck:
                fishingMusic = True

            if doRPC:
                RPC.update(
                    state="In Menus",
                    details=f'Balance: ${balance}',
                    name="Philooxy's Phishing",
                )

        for i in bobbers:
            i.castAnimCounter = 0
            i.cast = True
            exponent = 10
            i.pos = (-169, -124)

        drawTitle()

        linePos = (150, 101+startTransitionY*6)

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 0, 100, easingY, True)
        if not(finishedTransition):
            if not(startAnim):
                linePos = (150, 101+startTransitionY*6)
                drawFishing()
        else:
            for i in bobbers:
                i.pos = (-169, -124)
            startAnim = False

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 200, 100, easingY, False)
        if not(finishedTransition):
           drawAchs()

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 0, 100, easingX, True)
        if not(finishedTransition):
            drawShop()

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 200, 100, easingX, False)
        if not(finishedTransition):
            drawSettings()

    if area == "fishing":

        menuMusic = False

        if fishingMusic == False:
            fishingMusic = True
            if not(sunsetCheck) and not(sunriseCheck):
                pygame.mixer.stop()
                mus_fishing.play(loops=-1)
                menuMusic = False
            if sunsetCheck or sunriseCheck:
                menuMusic = True

            if doRPC:
                RPC.update(
                    state="Fishing",
                    details=f'Total Fish Caught: {fishCount}',
                    name="Philooxy's Phishing",
                )

        drawFishing()

        for i in bobbers:
            if i.reel and startTransitionY == 0:
                i.reelAnim()

            moving = False
            if i.cast and startTransitionY == 0:
                i.castAnim()

            if not(i.cast) and not(i.reel) and startTransitionY == 0.0:
                i.move()
            i.update()
    
        homebutton_up.update((20, 20+startTransitionY*6, 100, 40))

        if lowGraphicsMode == True:
            startTransitionY = 0
            linePos = (150, 101+startTransitionY*6)

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 100, 0, easingY, False)
        if not(finishedTransition):
            drawTitle()

            linePos = (150, 101+startTransitionY*6)
        else:
            if len(fishes) < fishSpawnCap:
                r = random.randint(1, 100)
                if r == 33:
                    if fishSFX == True:
                        ykwtm.play()
                    fish = fishy()

    if area == "shop":

        drawShop()
      
        if lowGraphicsMode == True:
            startTransitionX = 0

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 100, 0, easingX, False)
        if not(finishedTransition):
            drawTitle()
        
    if area == "settings":

        drawSettings()

        startTransitionX, easingX, finishedTransition = transition(startTransitionX, 100, 200, easingX, True)
        if not(finishedTransition):
            drawTitle()

    if area == "achs":

        drawAchs()

        startTransitionY, easingY, finishedTransition = transition(startTransitionY, 100, 200, easingY, True)
        if not(finishedTransition):
            drawTitle()


def update():
    pressed_keys = pygame.key.get_pressed()

    clock.tick(60)

    if fullscreen != pygame.display.is_fullscreen():
        pygame.display.toggle_fullscreen()

    pygame.display.flip()

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            save()

    pygame.mixer.music.set_volume(volume)

    screen.fill((255,255,255))

    hovering = False

    main(area)

    updateAchs()

    checkClick(True)

    if hovering == False:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    update()